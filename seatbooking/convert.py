import sqlite3
from contextlib import closing
from pathlib import Path

from seatbooking.seat import STUDENT_DATABASE, parse_gcn


def convert_students_file(
    filename: str | Path,
    database: str | Path = STUDENT_DATABASE,
) -> int:
    src = Path(filename).read_text(encoding="cp949")

    data: list[tuple[int, int, str]] = []
    for line in src.splitlines():
        if line == "":
            break

        parts = line.split()
        gcn = parse_gcn(parts[0])
        if gcn is None:
            msg = f"Invalid GCN: {parts[0]}"
            raise ValueError(msg)

        data.append((gcn, int(parts[2]), parts[1]))

    db_path = Path(database)
    db_path.parent.mkdir(exist_ok=True)
    with closing(sqlite3.connect(db_path)) as connection, connection:
        connection.execute("DROP TABLE IF EXISTS students")
        connection.execute(
            """
            CREATE TABLE students (
                position INTEGER NOT NULL,
                gcn INTEGER NOT NULL,
                lfn INTEGER NOT NULL,
                name TEXT NOT NULL
            )
            """,
        )
        connection.executemany(
            "INSERT INTO students (position, gcn, lfn, name) VALUES (?, ?, ?, ?)",
            [
                (position, gcn, lfn, name)
                for position, (gcn, lfn, name) in enumerate(data)
            ],
        )

    return len(data)


if __name__ == "__main__":
    print(convert_students_file(input("변환할 파일을 입력하세요: ")))
