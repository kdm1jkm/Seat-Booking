import os
import sys
import time

from prompt_toolkit import prompt

from seatbooking.convert import convert_students_file
from seatbooking.seat import (
    CUT_PREFIX,
    DEFAULT_PERIOD_COUNT,
    OUTPUT_DIR,
    CutStudent,
    Seat,
    student_csv_line,
)

SUPERUSER_PASSWORD = os.environ.get("SUPERUSER_PASSWORD", "1234")
RESET = "\033[0m"
TITLE = "\033[1;36m"
MENU = "\033[1;32m"
STATUS = "\033[33m"


def main() -> None:
    seat = Seat(DEFAULT_PERIOD_COUNT)
    seat.load_data()
    seat.read_database()
    status = "준비됨"

    while True:
        seat.save_data()
        render_screen(seat, status)
        command = prompt("명령 > ").strip().lower()

        if command in {"q", "e", "exit"}:
            break
        status = handle_command(seat, command)

    seat.save_data()


def render_screen(seat: Seat, status: str) -> None:
    clear_screen()
    sys.stdout.write(
        f"{TITLE}좌석 예약{RESET}\n\n"
        f"{seat.render_table()}\n\n"
        f"{MENU}[1]{RESET} 1교시 예약   "
        f"{MENU}[2]{RESET} 2교시 예약   "
        f"{MENU}[3]{RESET} 3교시 예약\n"
        f"{MENU}[d]{RESET} 삭제   "
        f"{MENU}[s]{RESET} CSV 저장   "
        f"{MENU}[r]{RESET} 추첨   "
        f"{MENU}[a]{RESET} 전체 삭제\n"
        f"{MENU}[c]{RESET} 학생 데이터 변환   "
        f"{MENU}[q]{RESET} 종료\n\n"
        f"{STATUS}{status}{RESET}\n",
    )
    sys.stdout.flush()


def clear_screen() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def handle_command(seat: Seat, command: str) -> str:  # noqa: PLR0911
    if command in {"1", "2", "3"}:
        return reserve_student(seat, int(command) - 1)
    if command == "d":
        return delete_student(seat)
    if command == "s" and is_admin():
        seat.export_to_csv()
        return "CSV 파일을 저장했습니다."
    if command == "r" and is_admin():
        return cut_students(seat)
    if command == "a" and is_admin():
        seat.reset()
        seat.read_database()
        return "전체 예약을 삭제했습니다."
    if command == "c" and is_admin():
        return convert_students(seat)
    return "알 수 없는 명령입니다."


def reserve_student(seat: Seat, period_index: int) -> str:
    gcn = ask_text("학반번호")
    if gcn is None:
        return "예약을 취소했습니다."
    if seat.append_student_by_gcn(period_index, gcn):
        return "예약을 추가했습니다."
    return "학생을 찾을 수 없습니다."


def delete_student(seat: Seat) -> str:
    gcn = ask_text("학반번호")
    if gcn is None:
        return "삭제를 취소했습니다."

    student = seat.search_student_by_gcn(gcn)
    if student is None:
        return "예약을 찾을 수 없습니다."

    period_index, student_index = student
    seat.del_student(period_index, student_index)
    return "예약을 삭제했습니다."


def cut_students(seat: Seat) -> str:
    max_students_text = ask_text("몇 명까지")
    if max_students_text is None:
        return "추첨을 취소했습니다."

    try:
        max_students = int(max_students_text)
    except ValueError:
        return "숫자를 입력하세요."
    if max_students < 0:
        return "0 이상의 숫자를 입력하세요."

    cut_people = seat.cut_random(max_students)
    export_cut_people(cut_people)
    return f"{len(cut_people)}명을 추첨했습니다."


def convert_students(seat: Seat) -> str:
    filename = ask_text("변환할 파일")
    if filename is None:
        return "변환을 취소했습니다."

    try:
        count = convert_students_file(filename)
    except (OSError, ValueError, IndexError) as error:
        return f"변환 실패: {error}"

    seat.read_database()
    return f"{count}명의 학생 데이터를 저장했습니다."


def is_admin() -> bool:
    password = prompt(
        "관리자 패스워드 > ",
        is_password=True,
    )
    return password == SUPERUSER_PASSWORD


def ask_text(label: str) -> str | None:
    value = prompt(f"{label} > ").strip()
    return value or None


def export_cut_people(cut_people: list[CutStudent]) -> None:
    output_dir = OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)
    filename = time.strftime(
        f"{CUT_PREFIX}_%Y-%m-%d_%H%M%S.csv",
        time.localtime(time.time()),
    )

    with (output_dir / filename).open("w") as file:
        file.write("이름,층,번호,교시\n")
        for cut_student in cut_people:
            file.write(student_csv_line(cut_student.student, cut_student.period))


if __name__ == "__main__":
    sys.exit(main())
