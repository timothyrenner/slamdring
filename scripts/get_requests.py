import requests
import csv

fin = open('data/test_data_large.csv', 'r')
fout = open('data/test_data_large_responses.csv', 'w')

reader = csv.reader(fin)
writer = csv.writer(fout)

# Use a persistent connection, just like slamdring does.
session = requests.Session()

for line in reader:
    response = session.get(line[-1])

    writer.writerow(line + [response.text])

fin.close()
fout.close()
