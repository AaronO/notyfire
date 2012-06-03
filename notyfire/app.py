# Python imports
import os

# ZMQ imports
import zmq
from zmq.eventloop import ioloop, zmqstream
ioloop.install()

# Tornado imports
import tornado
import tornado.web

# TornadIO imports
import tornadio
import tornadio.router
import tornadio.server

# Local imports
from notyfire import copyright
from notyfire.channels import ChannelServer



# flashpolicy.xml is bundled in the source
ROOT = os.path.normpath(os.path.dirname(__file__))

# Consts
DEFAULT_PROTOCOLS = ['websocket', 'flashsocket', 'xhr-multipart', 'xhr-polling'],
DEFAULT_FLASH_POLICY_PORT = 843,
DEFAULT_FLASH_POLICY_FILE = os.path.join(ROOT, 'flashpolicy.xml'),
DEFAULT_SOCKET_IO_PORT = 8001
DEFAULT_ZMQ_BIND = 'tcp://127.0.0.1:5000'



class ChannelServerApp(object):
    def __init__(self, **kwargs):
        self.enabled_protocols = kwargs.get('enabled_protocols', DEFAULT_PROTOCOLS)
        self.flash_policy_port = kwargs.get('flash_policy_port', DEFAULT_FLASH_POLICY_PORT)
        self.flash_policy_file = kwargs.get('flash_policy_file', DEFAULT_FLASH_POLICY_FILE)
        self.socket_io_port = kwargs.get('socket_io_port', DEFAULT_SOCKET_IO_PORT)
        self.zmq_bind = kwargs.get('zmq_bind', DEFAULT_ZMQ_BIND)

        self.channel_server = ChannelServer


    def init_zmq(self):
        self.zmq_context = zmq.Context()

        # Socket
        self.zmq_socket = self.zmq_context.socket(zmq.SUB)
        self.zmq_socket.setsockopt(zmq.SUBSCRIBE, '')
        self.zmq_socket.bind(self.zmq_bind)

        # Stream
        self.zmq_stream = zmqstream.ZMQStream(self.zmq_socket, tornado.ioloop.IOLoop.instance())
        self.zmq_stream.on_recv(self.channel_server.dispatch_message)
        

    def init_routes(self):
        router = tornadio.get_router(self.channel_server)
        self.routes = [router.route()]


    def init_application(self):
        self.application = tornado.web.Application(
            self.routes,
            enabled_protocols = self.enabled_protocols,
            flash_policy_port = self.flash_policy_port,
            flash_policy_file = self.flash_policy_file,
            socket_io_port = self.socket_io_port,
        )


    def start(self):
        self.init_routes()
        self.init_zmq()
        self.init_application()

        # Show copyright
        copyright.print_copyright()

        try:
            tornadio.server.SocketServer(self.application)
        except KeyboardInterrupt:
            pass
 
