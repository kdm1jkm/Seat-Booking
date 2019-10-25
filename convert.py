import pickle
import os

filename = "sampledata.txt"

if not os.path.exists(filename):
    filename = input("변환할 파일을 입력하세요: ")

with open(filename, 'r') as f:
    src = f.read()

data = [[],[],[]]

for i in src.split('\n'):
    if i == '': break

    if i.split(' ')[0][1] == "A":
        i = '30%s' % i[2:]
    elif i.split(' ')[0][1] == "B":
        i = '31%s' % i[2:]

    data[0].append(int(i.split(' ')[0]))
    data[1].append(int(i.split(' ')[2]))
    data[2].append(i.split(' ')[1])

with open('data.dat', 'wb') as f:
    pickle.dump(data, f)

print(data)
