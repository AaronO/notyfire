# ZMQ imports
import zmq


class Sender(object):
    MODE = zmq.PUB
    OPTS = (
        (zmq.LINGER, 0),
    )
    PROTOCOL = 'tcp'
    HOST = '127.0.0.1'
    PORT = 5000

    def __init__(self, protocol = None, host = None, port = None, mode = None, opts = None, connect_now = True):
        self.protocol= protocol or self.PROTOCOL
        self.host = host or self.HOST
        self.port = port or self.PORT
        self.mode = mode or self.MODE
        self.opts = opts or self.OPTS

        self.context = zmq.Context()
        self.socket = self.context.socket(self.MODE)

        for opt, val in self.opts:
            self.socket.setsockopt(opt, val)

        # Connect immediatly by default
        if connect_now:
            self.connect()


    @property
    def connect_adress(self):
        return "%s://%s:%d" % (self.protocol, self.host, self.port)

    def connect(self):
        self.socket.connect(self.connect_adress)

    def send(self, **kwargs):
        if not kwargs:
            raise Exception("Nothing to send")
        self.socket.send_json(kwargs)

    def __del__(self):
        self.socket.close()