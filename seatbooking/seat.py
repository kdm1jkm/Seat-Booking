import random
import sqlite3
import time
import unicodedata
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PERIOD_COUNT = 3
GCN_LENGTH = 4
NEW_BOYS_BUILDING = 4
NEW_GIRLS_BUILDING = 5
ROOM_NUMBER_BASE = 100
TABLE_CELL_WIDTH = 22
OUTPUT_DIR = Path("output")
STUDENT_DATABASE = OUTPUT_DIR / "students.db"
LEGACY_STUDENT_DATABASE = Path("data.db")
SEAT_DATABASE = OUTPUT_DIR / "seat.db"
LEGACY_SEAT_DATABASE = Path("seat.db")
RESERVATION_PREFIX = "reservation"
CUT_PREFIX = "cut"

type SeatPosition = tuple[int, int]


@dataclass(frozen=True, slots=True)
class Student:
    name: str
    lfn: int
    gcn: int


@dataclass(frozen=True, slots=True)
class CutStudent:
    student: Student
    period: int


class Seat:
    def __init__(self, numbers: int, _seat: object | None = None) -> None:
        self.max_num = numbers
        self._students_by_period: list[list[Student]] = [[] for _ in range(numbers)]
        self._student_records: list[Student] | None = None

    def append_student(
        self,
        period_index: int,
        gcn: str | int,
        lfn: str | int,
        name: str,
    ) -> bool:
        parsed_gcn = parse_gcn(gcn)
        if parsed_gcn is None:
            return False

        try:
            parsed_lfn = int(lfn)
        except ValueError:
            return False

        self._delete_duplicate(parsed_gcn, parsed_lfn)
        self._students_by_period[period_index].append(
            Student(name, parsed_lfn, parsed_gcn),
        )
        return True

    def edit_student(
        self,
        from_period_index: int,
        student_index: int,
        to_period_index: int,
    ) -> bool:
        student = self.del_student(from_period_index, student_index)
        if student is None:
            return False
        return self.append_student(
            to_period_index,
            student.gcn,
            student.lfn,
            student.name,
        )

    def del_student(self, period_index: int, student_index: int) -> Student | None:
        try:
            return self._students_by_period[period_index].pop(student_index)
        except IndexError:
            return None

    def get_student(self, period_index: int, student_index: int) -> Student | None:
        try:
            return self._students_by_period[period_index][student_index]
        except IndexError:
            return None

    def get_all_name(self, period_index: int) -> list[str]:
        return [student.name for student in self._students_by_period[period_index]]

    def get_all_lfn(self, period_index: int) -> list[int]:
        return [student.lfn for student in self._students_by_period[period_index]]

    def get_all_gcn(self, period_index: int) -> list[int]:
        return [student.gcn for student in self._students_by_period[period_index]]

    def read_database(self, filename: str | Path = STUDENT_DATABASE) -> bool:
        db_path = _existing_path(Path(filename), LEGACY_STUDENT_DATABASE)
        if not db_path.exists():
            return False

        with closing(sqlite3.connect(db_path)) as connection:
            rows = connection.execute(
                "SELECT gcn, lfn, name FROM students ORDER BY position",
            ).fetchall()
        self._student_records = [
            Student(str(name), int(lfn), int(gcn)) for gcn, lfn, name in rows
        ]
        return True

    def append_student_by_gcn(self, period_index: int, gcn: str | int) -> bool:
        if self._student_records is None:
            return False

        parsed_gcn = parse_gcn(gcn)
        if parsed_gcn is None:
            return False

        for student in self._student_records:
            if student.gcn == parsed_gcn:
                return self.append_student(
                    period_index,
                    student.gcn,
                    student.lfn,
                    student.name,
                )

        return False

    def cut_random(self, max_students: int) -> list[CutStudent]:
        cut_people: list[CutStudent] = []
        for period_index, students in enumerate(self._students_by_period):
            while len(students) > max_students:
                student_index = random.randrange(len(students))
                cut_people.append(
                    CutStudent(students.pop(student_index), period_index + 1)
                )

        return cut_people

    def save_data(self, filename: str | Path = SEAT_DATABASE) -> None:
        db_path = Path(filename)
        db_path.parent.mkdir(exist_ok=True)
        with closing(sqlite3.connect(db_path)) as connection, connection:
            _create_seat_tables(connection)
            connection.execute("DELETE FROM meta")
            connection.execute("DELETE FROM reservations")
            connection.execute("DELETE FROM student_cache")
            connection.executemany(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                [
                    ("max_num", str(self.max_num)),
                    (
                        "student_records_loaded",
                        str(int(self._student_records is not None)),
                    ),
                ],
            )
            connection.executemany(
                """
                INSERT INTO reservations (period_index, position, name, lfn, gcn)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        period_index,
                        position,
                        student.name,
                        student.lfn,
                        student.gcn,
                    )
                    for period_index, students in enumerate(self._students_by_period)
                    for position, student in enumerate(students)
                ],
            )
            if self._student_records is not None:
                connection.executemany(
                    """
                    INSERT INTO student_cache (position, gcn, lfn, name)
                    VALUES (?, ?, ?, ?)
                    """,
                    [
                        (position, student.gcn, student.lfn, student.name)
                        for position, student in enumerate(self._student_records)
                    ],
                )

    def load_data(self, filename: str | Path = SEAT_DATABASE) -> None:
        db_path = _existing_path(Path(filename), LEGACY_SEAT_DATABASE)
        if not db_path.exists():
            return

        with closing(sqlite3.connect(db_path)) as connection:
            meta = dict(connection.execute("SELECT key, value FROM meta").fetchall())
            self.max_num = int(meta.get("max_num", self.max_num))
            self._students_by_period = [[] for _ in range(self.max_num)]

            for period_index, _position, name, lfn, gcn in connection.execute(
                """
                SELECT period_index, position, name, lfn, gcn
                FROM reservations
                ORDER BY period_index, position
                """,
            ):
                self._students_by_period[int(period_index)].append(
                    Student(str(name), int(lfn), int(gcn)),
                )

            if meta.get("student_records_loaded") == "1":
                rows = connection.execute(
                    "SELECT gcn, lfn, name FROM student_cache ORDER BY position",
                ).fetchall()
                self._student_records = [
                    Student(str(name), int(lfn), int(gcn)) for gcn, lfn, name in rows
                ]
            else:
                self._student_records = None

    def reset(self) -> None:
        self._students_by_period = [[] for _ in range(self.max_num)]
        self._student_records = []

    def search_student_by_gcn(self, gcn: str | int) -> SeatPosition | None:
        parsed_gcn = parse_gcn(gcn)
        if parsed_gcn is None:
            return None

        for period_index, students in enumerate(self._students_by_period):
            for student_index, student in enumerate(students):
                if parsed_gcn == student.gcn:
                    return (period_index, student_index)

        return None

    def export_to_csv(self, filename: str | Path | None = None) -> None:
        csv_path = (
            Path(filename)
            if filename is not None
            else Path(
                time.strftime(
                    f"{OUTPUT_DIR}\\{RESERVATION_PREFIX}_%Y-%m-%d_%H%M%S.csv",
                    time.localtime(time.time()),
                ),
            )
        )
        csv_path.parent.mkdir(exist_ok=True)
        with csv_path.open("w") as file:
            file.write("이름,층,번호,교시\n")
            for period_index, students in enumerate(self._students_by_period):
                for student in students:
                    file.write(student_csv_line(student, period_index + 1))

    def render_table(self) -> str:
        nos = max((len(students) for students in self._students_by_period), default=0)
        periods = list(range(self.max_num))
        top = "┌" + "┬".join("─" * TABLE_CELL_WIDTH for _ in periods) + "┐"
        header = (
            "│"
            + "│".join(
                _pad_cell(
                    f"{period_index + 1}교시 ({len(self.get_all_gcn(period_index))}명)",
                )
                for period_index in periods
            )
            + "│"
        )
        divider = "├" + "┼".join("─" * TABLE_CELL_WIDTH for _ in periods) + "┤"
        bottom = "└" + "┴".join("─" * TABLE_CELL_WIDTH for _ in periods) + "┘"

        rows = [
            (
                "│"
                + "│".join(
                    _pad_cell(
                        _student_cell(self.get_student(period_index, student_index)),
                    )
                    for period_index in periods
                )
                + "│"
            )
            for student_index in range(nos)
        ]

        if not rows:
            rows.append(
                "│"
                + "│".join(
                    _pad_cell("예약 없음" if period_index == 0 else "")
                    for period_index in periods
                )
                + "│",
            )

        return "\n".join([top, header, divider, *rows, bottom])

    def _delete_duplicate(self, gcn: int, lfn: int) -> None:
        for students in self._students_by_period:
            for student_index, student in enumerate(students):
                if student.gcn == gcn and student.lfn == lfn:
                    students.pop(student_index)
                    return


def _student_cell(student: Student | None) -> str:
    if student is None:
        return ""
    return f"{student.gcn} {student.name}"


def _pad_cell(text: str) -> str:
    return text + " " * max(TABLE_CELL_WIDTH - _display_width(text), 0)


def _display_width(text: str) -> int:
    return sum(
        2 if unicodedata.east_asian_width(character) in {"F", "W"} else 1
        for character in text
    )


def _existing_path(path: Path, fallback: Path) -> Path:
    if path.exists() or not fallback.exists():
        return path
    return fallback


def format_library_floor(lfn: int) -> str:
    floor = (lfn - (lfn % ROOM_NUMBER_BASE)) // ROOM_NUMBER_BASE
    if floor == NEW_BOYS_BUILDING:
        return "남자신관"
    if floor == NEW_GIRLS_BUILDING:
        return "여자신관"
    return f"{floor}층"


def parse_gcn(gcn: str | int) -> int | None:
    gcn_text = str(gcn)
    if len(gcn_text) != GCN_LENGTH:
        return None
    if gcn_text[1:2].casefold() == "a":
        gcn_text = f"30{gcn_text[2:]}"
    elif gcn_text[1:2].casefold() == "b":
        gcn_text = f"31{gcn_text[2:]}"
    try:
        return int(gcn_text)
    except ValueError:
        return None


def student_csv_line(student: Student, period: int) -> str:
    floor = format_library_floor(student.lfn)
    room_number = student.lfn % ROOM_NUMBER_BASE
    return f"{student.name},{floor},{room_number}번,{period}교시\n"


def _create_seat_tables(connection: sqlite3.Connection) -> None:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reservations (
            period_index INTEGER NOT NULL,
            position INTEGER NOT NULL,
            name TEXT NOT NULL,
            lfn INTEGER NOT NULL,
            gcn INTEGER NOT NULL
        )
        """,
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS student_cache (
            position INTEGER NOT NULL,
            gcn INTEGER NOT NULL,
            lfn INTEGER NOT NULL,
            name TEXT NOT NULL
        )
        """,
    )
