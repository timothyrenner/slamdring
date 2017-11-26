import csv

fout = open('data/test_data_large.csv', 'w')
writer = csv.writer(fout)

for ii in range(10000):
    writer.writerow([1, "http://localhost:3000/posts/1"])

fout.close()
