file1 = 'WSJ_02-21.pos'
file2 = 'WSJ_24.pos'

temp1 = open(file1, 'r')
temp2 = open(file2, 'r')
file1Data = temp1.readlines()
file2Data = temp2.readlines()
file1_line = 0
file2_line = 0

with open('training_file.pos', 'w') as out_file:
    for line in file1Data:
        out_file.write(line)
        #out_file.write('\n')
        file1_line += 1
    print("file 1 written, total lines:", file1_line)
    for line in file2Data:
        out_file.write(line)
        #out_file.write('\n')
        file2_line += 1
    print("file 2 written, total lines:", file2_line)
temp1.close()
temp2.close()
out_file.close()

total_readline = file1_line + file2_line

out_line = 0
with open('training_file.pos', 'r') as file:
    data = file.readlines()
    for line in data:
        out_line += 1
file.close()

print('lines read from two files:', total_readline)
print('lines read from out file:', out_line)








