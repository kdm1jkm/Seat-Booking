import pickle
import os
import random
import time


class Seat():
    def __init__(self, numbers, _seat=None):
        self.max_num = numbers
        self.__name = []
        # Library Floor Number
        self.__lfn = []
        # Grade Class Number
        self.__gcn = []
        for i in range(numbers):
            self.__name.append([])
            self.__lfn.append([])
            self.__gcn.append([])

        self.__data = None

        if _seat is not None:
            try:
                pass
            finally:
                pass

    def append_student(self, num, gcn, lfn, name):

        gcn = str(gcn)
        if gcn[1] == 'A' or gcn[1] == 'a':
            gcn = "30%s" % gcn[2:]
        if gcn[1] == 'B' or gcn[1] == 'b':
            gcn = "31%s" % gcn[2:]

        try:
            lfn = int(lfn)
            gcn = int(gcn)
        except ValueError:
            return -1

        b = False

        for i in range(self.max_num):
            for j in range(len(self.__gcn[i])):
                if gcn == self.__gcn[i][j] and lfn == self.__lfn[i][j]:
                    self.del_student(i, j)
                    b = True
                if b: break
            if b: break

        self.__name[num].append(name)
        self.__lfn[num].append(lfn)
        self.__gcn[num].append(gcn)

    def edit_student(self, num, n, nn):
        # num: 교시 / n: 몇번째학생 / nn: next number
        l = self.del_student(num, n)
        self.append_student(nn, l[2], l[1], l[0])

    def del_student(self, num, n):
        l = []
        try:
            l.append(self.__name[num].pop(n))
            l.append(self.__lfn[num].pop(n))
            l.append(self.__gcn[num].pop(n))
        except IndexError:
            return -1
        return l

    def get_student(self, num, n):
        student = []

        try:
            student.append(self.__name[num][n])
            student.append(self.__lfn[num][n])
            student.append(self.__gcn[num][n])
        except IndexError:
            return -1

        return student

    def get_all_name(self, num):
        return self.__name[num]

    def get_all_lfn(self, num):
        return self.__lfn[num]

    def get_all_gcn(self, num):
        return self.__gcn[num]

    def read_database(self, filename="data.dat"):
        if not os.path.exists(filename):
            return -1

        with open(filename, 'rb') as f:
            self.__data = pickle.load(f)

    def append_student_by_gcn(self, num, gcn):
        if self.__data is None:
            return -1

        gcn = str(gcn)
        if gcn[1] == 'A' or gcn[1] == 'a':
            gcn = "30%s" % gcn[2:]
        elif gcn[1] == 'B' or gcn[1] == 'b':
            gcn = "31%s" % gcn[2:]

        try:
            gcn = int(gcn)
        except ValueError:
            return -1

        for i in range(len(self.__data[0])):
            if self.__data[0][i] == gcn:
                self.append_student(num, self.__data[0][i], self.__data[1][i], self.__data[2][i])
                return 0

        return -1

    def cut_random(self, num):
        for i in range(self.max_num):
            while len(self.get_all_gcn(i)) > num:
                p = random.randint(0, len(self.__gcn))
                self.__name[i].pop(p)
                self.__gcn[i].pop(p)
                self.__lfn[i].pop(p)

    def save_data(self, filename="seat.dat"):
        with open(filename, 'wb') as f:
            pickle.dump(self.max_num, f)
            pickle.dump(self.__name, f)
            pickle.dump(self.__gcn, f)
            pickle.dump(self.__lfn, f)
            pickle.dump(self.__data, f)

    def load_data(self, filename="seat.dat"):
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                self.max_num = pickle.load(f)
                self.__name = pickle.load(f)
                self.__gcn = pickle.load(f)
                self.__lfn = pickle.load(f)
                self.__data = pickle.load(f)

    def reset(self):
        self.__name = [[],[],[]]
        self.__lfn = [[],[],[]]
        self.__gcn = [[],[],[]]
        self.__data = [[],[],[]]

    def search_student_by_gcn(self, gcn):

        gcn = str(gcn)
        if gcn[1] == 'A' or gcn[1] == 'a':
            gcn = "30%s" % gcn[2:]
        if gcn[1] == 'B' or gcn[1] == 'b':
            gcn = "31%s" % gcn[2:]

        try:
            gcn = int(gcn)
        except ValueError:
            return -1

        b = False

        for i in range(self.max_num):
            for j in range(len(self.__gcn[i])):
                if gcn == self.__gcn[i][j]:
                    return (i, j)

        return (-1, -1)

    def export_to_csv(self, filename = None):
        if filename is None:
            filename = time.strftime("data\\%Y-%m-%d_%H%M%S.csv", time.localtime(time.time()))
        if not os.path.exists("data"):
            os.mkdir("data")
        with open(filename, 'w') as f:
            f.write("이름,층,번호,교시\n")
            for i in range(self.max_num):
                for j in range(len(self.get_all_gcn(i))):
                    student = self.get_student(i, j)
                    name = self.__name[i][j]
                    ln = "%d번" % (self.__lfn[i][j] % 100)
                    lf = (self.__lfn[i][j] - (self.__lfn[i][j] % 100)) / 100
                    if lf == 4: lf = "남자신관"
                    elif lf == 5: lf = "여자신관"
                    else: lf = "%d층" % lf
                    str = "%s,%s,%s,%s\n" % (name, lf, ln, "%d교시" % (i + 1))
                    f.write(str)

        # name lf n num

