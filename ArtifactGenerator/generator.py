import os
import time
import sys

# generate random integer values
from random import seed
from random import randint

from zipfile import ZipFile

seed(time.time())

zip = True
size = 4096
tmpFileName = "payload.txt"
if zip: 
    print(f"Desired size: {size}, Zipping {zip}")
    size = size - 120
else:
    print(f"Desired size: {size}, Zipping {zip}")
payload = ""

f = open(tmpFileName, "w")

for i in range(size):
    payload = payload + f"{randint(0, 9)}"

f.write(payload)
f.close()

print("Payload size:")
print("On disc: ", os.stat(tmpFileName).st_size)
print("As object in Python3 (with 49 bytes overhead, unicode string) ", sys.getsizeof(payload))

if zip:
    zipName = 'sample.zip'
    print("Zip size:")
    zipObj = ZipFile(zipName, 'w')
    zipObj.write(tmpFileName)
    zipObj.close()
    os.remove(tmpFileName)
    print(os.stat(zipName).st_size)
