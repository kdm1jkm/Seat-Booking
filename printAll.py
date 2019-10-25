from Seat import Seat
import os

def print_all(seat):
    #  number of student
    nos = 0
    for i in range(seat.max_num):
        if nos < len(seat.get_all_gcn(i)):
            nos = len(seat.get_all_gcn(i))
    os.system("mode con cols=%d lines=%d" % (74, nos + 20))
    print("┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓\n┃\t1교시(%d명)\t┃\t2교시(%d명)\t┃\t3교시(%d명)\t┃" % (len(seat.get_all_gcn(0)), len(seat.get_all_gcn(1)), len(seat.get_all_gcn(2))))
    print("┃\t\t\t┃\t\t\t┃\t\t\t┃")
    for i in range(nos):
        name = []
        for j in range(3):
            name.append(seat.get_student(j, i))
            if name[j] == -1: name[j] = "\t"
            else: name[j] = name[j][0]
            # if len(name[j]) == 2: name[j] += " "
        print("┃\t%02d. %s\t┃\t%02d. %s\t┃\t%02d. %s\t┃" % (i+1, name[0], i+1, name[1], i+1, name[2]))
    print("┃\t\t\t┃\t\t\t┃\t\t\t┃")
    print("┣━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━┫")
        
    
    
    

if __name__ == '__main__':
    seat = Seat(3)

    seat.load_data()

    seat.read_database()
    
    print_all(seat)
    pass