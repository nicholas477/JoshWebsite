from termcolor import colored
import sys
import datetime

xprint = print
def print(*args, **kwargs):
    now = datetime.datetime.now()
    sys.stdout.write(colored(now.strftime("[%Y-%m-%d %I:%M:%S %p] "), "green"))
    xprint(*args, **kwargs)