
import os

def isLocal():
    return os.environ["SERVER_NAME"] == "localhost"

