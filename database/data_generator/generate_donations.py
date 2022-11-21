import csv
from datetime import datetime, timedelta
import random

# This python script generates donation records and write to CSV format and SQL INSERT statements.

filename_base = 'donations'

count = int(input("Enter number of donations to generate: "))

donors = [
    'S9990000A',
    'S9991111A',
    'T0000000B',
    'T0001111B',
    'S8880000C',
    'S8881111C',
    'S7770000D',
    'S7771111D',
]

quantities = list(range(200, 1000, 50)) # 200 - 950
branches = [ 10001, 10002, 10003, 10004 ]

earliestDate = datetime(2020, 1, 1)
today = datetime.today()

hrIncrement = 24 # Date increment per record, in hours
deltaDays = (today - earliestDate).days
if count > deltaDays:
    hrIncrement = 24 / (count / deltaDays)

# CSV format
# with open(f'{filename_base}-{count}.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile, delimiter=',')
#     for i in range(count):
#         writer.writerow([
#             i + 1, # ID
#             random.choice(donors), # NRIC
#             random.choice(quantities), # Quantity
#             (earliestDate + timedelta(hours=hrIncrement * i)).strftime('%Y-%m-%d'), # Date
#             random.choice(branches), # Branch Id
#             1, # recordedBy
#             'NULL'
#         ])

# SQL INSERT statements
with open(f'{filename_base}-{count}.sql', 'w') as f:
    f.write(
        'INSERT INTO `bloodmanagementsystem`.`BloodDonation` (`id`, `nric`, `quantity`, `date`, `branchId`, `recordedBy`, `usedBy`) VALUES\n'
    )

    for i in range(count):
        data = [
            i + 1, # ID
            f'\"{random.choice(donors)}\"', # NRIC
            random.choice(quantities), # Quantity
            (earliestDate + timedelta(hours=hrIncrement * i)).strftime('\"%Y-%m-%d\"'), # Date
            random.choice(branches), # Branch Id
            1, # recordedBy
            'NULL'
        ]
        data = [str(d) for d in data]
        f.write(f'({",".join(data)})')
        if i == count - 1:
            f.write(';\n')
        else:
            f.write(',\n')