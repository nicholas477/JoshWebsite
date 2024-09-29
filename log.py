from termcolor import colored
import sys
import datetime
from contextlib import redirect_stdout

class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

def open_log_file():
    now = datetime.datetime.now()
    return open(now.strftime("log_%Y-%m-%d__%I-%M-%S-%p.log"), 'w')

log_file = open_log_file()

# Tee stdout to console + log file
original_stdout = sys.stdout
sys.stdout = Tee(sys.stdout, log_file)

xprint = print
def print(*args, **kwargs):
    now = datetime.datetime.now()
    datestr = now.strftime("[%Y-%m-%d %I:%M:%S %p] ")

    sys.stdout.write(colored(datestr, "green"))
    xprint(*args, **kwargs)