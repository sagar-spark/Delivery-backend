# Author: CP

import os

def getEnvValue(string):
    return os.environ.get(string, "None")

