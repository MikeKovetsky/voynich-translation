
file_path = 'data/eva_ivtff.txt'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find lines mentioning the target pages
targets = ['f67v2', 'f8v', 'f90r1']
for line in lines:
    for target in targets:
        if target in line:
            print(line.strip())
