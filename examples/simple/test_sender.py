# Python imports
import time

# Notyfre imports
from notyfire import Sender


if __name__ == '__main__':
    s = Sender()
    for i in xrange(500):
        s.send(default = 'hello')
        time.sleep(0.2)