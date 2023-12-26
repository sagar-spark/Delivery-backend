# Author: CP

import hashlib

def getMd5Hash(string):
    a = hashlib.md5(string.encode())
    return a.hexdigest()

