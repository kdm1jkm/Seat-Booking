from Seat import Seat
import os
from printAll import print_all

superuser_password = "__"

# def print_all(seat):
#     # Number of Student
#     nos = 0
#     for i in range(seat.max_num):
#         if nos < len(seat.get_all_gcn(i)):
#             nos = len(seat.get_all_gcn(i))

#     os.system("mode con cols=%d lines=%d" % (48, nos + 10))

#     print("\n1교시(%d명)\t2교시(%d명)\t3교시(%d명)\t" % (len(seat.get_all_gcn(0)), len(seat.get_all_gcn(1)), len(seat.get_all_gcn(2))))

#     for i in range(nos):
#         for j in range(3):
#             name = seat.get_student(j, i)
#             if name == -1:
#                 name = "      "
#             else:
#                 name = name[0]
#             if len(name) == 2 or 4:
#                 name += "  "
#             print("%d. %s\t" % ((i + 1), name), end='')
#         print('')

#     return 0


# def append(seat):
#     print("[1 ~ 3] 예약")
#     print("[4] 삭제")
#     print("[-1] 취소")
#     print("[-2] 종료")
#     time = input("Enter: ")
#     while time != '1' and time != '2' and time != '3':
#         if time == '-1':
#             return 0
#         if time == '-2':
#             return -2
#         if time == '4':
#             return 4
#         if time == '/delete all':
#             return -5
#         time = input("올바른 숫자를 입력하세요: ")

#     time = int(time) - 1

#     gcn = input("-1:취소 | 학반번호를 입력하세요(Ex: 1204): ")
#     while seat.append_student_by_gcn(time, gcn) == -1:
#         if gcn == '-1':
#             return 0
#         gcn = input("유효한 번호를 입력하세요: ")

#     return 0


if __name__ == "__main__":
    seat = Seat(3)

    seat.load_data()

    seat.read_database()

    print_all(seat)

    while True:
        seat.save_data()
        os.system("cls")

        print_all(seat)
        print("┃\t[1] 1교시 예약\t\t[2] 2교시 예약\t\t[3] 3교시 예약\t┃")
        print("┃\t\t\t\t\t\t\t\t\t┃")
        print("┃\t[d] 삭제\t\t[s] 엑셀로 저장\t\t[r] 추첨\t┃")
        print("┃\t[a] 전체 삭제\t\t[e] 종료\t\t\t\t┃")
        print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

        _input = input("[]안의 키를 입력하세요: ")

        if _input == "1" or _input == "2" or _input == "3":
            gcn = 9999
            while seat.append_student_by_gcn(int(_input) - 1, gcn) == -1:
                gcn = input("학반번호를 입력하세요: ")

        elif _input == "D" or _input == "d":
            gcn = input("학반번호를 입력하세요: ")
            (num, n) = seat.search_student_by_gcn(gcn)
            if num != -1:
                seat.del_student(num, n)
        
        elif _input == "s" or _input == "S":
            seat.export_to_csv()
        
        elif _input == "r" or _input == "R":
            if input("관리자 패스워드: ") == superuser_password:
                random = input("몇 명까지 추첨할까요: ")
                seat.cut_random(int(random))
        
        elif _input == "a" or _input == "A":
            if input("관리자 패스워드: ") == superuser_password:
                seat.reset()
                seat.read_database()
        
        elif _input == "e":
            break

    seat.save_data()
