# Python imports
try:
    import simplejson as json
except:
    import json

# TornadIO imports
import tornadio



class Channel(object):

    def __init__(self, channel_id, clients = None):
        self.channel_id = channel_id
        self.clients = clients or set()


    def add_client(self, client):
        self.clients.add(client)


    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)


    def dispatch_message(self, message):
        for c in self.clients:
            c.send({ self.channel_id : message })



class ChannelClientActions(object):

    def handle_client_action(self, action, data):
        actions = {
            'subscribe' : self.user_subscribe,
            'unsubscribe' : self.user_unsubscribe,
        }
        func = actions.get(action)
        if func:
            func(data)

    @classmethod
    def _satinize_channel_list(cls, channel_list_string):
        if isinstance(channel_list_string, basestring):
            channel_list_string = [channel_list_string]
        if isinstance(channel_list_string, (list, tuple)):
            return channel_list_string
        return []

    def user_subscribe(self, data):
        data = self._satinize_channel_list(data)
        channel_list = self.client_channels[self]
        for channel_id in data:
            # Create channel if necessary and subscribe to it
            self.channels[channel_id] = self.channels.get(channel_id , Channel(channel_id))
            self.channels[channel_id].add_client(self)
            channel_list.append(channel_id)


    def user_unsubscribe(self, data):
        data = self._satinize_channel_list(data)
        channel_list = self.client_channels[self]
        for channel_id in data:
            self.channels[channel_id].remove_client(self)
            channel_list.remove(channel_id)



class ChannelZMQActions(object):

    @classmethod
    def handle_zmq_action(cls, action, data):
        cls.get_channel(action).dispatch_message(data)
 



class ChannelServer(tornadio.SocketConnection, ChannelClientActions, ChannelZMQActions):
    channels = {}
    client_channels = {}

    @classmethod
    def get_channel(cls, channel_id):
        if not channel_id in cls.channels:
            cls.channels[channel_id] = Channel(channel_id)
        return cls.channels[channel_id]


    # Messages from ZMQ
    @classmethod
    def dispatch_message(cls, messages):
        for m in messages:
            message = json.loads(m)
            if not isinstance(message, dict):
                return
            for action, data in message.items():
                cls.handle_zmq_action(action, data)
 

    # Messages from the client
    def on_message(self, message):
        if not isinstance(message, dict):
            return
        for action, data in message.items():
            self.handle_client_action(action, data)


    def on_open(self, *args, **kwargs):
        # Connection established, not connected to any channels
        self.client_channels[self] = []
        self.user_subscribe('default')
        

    def on_close(self):
        # Remove user from all clients, cleanup
        channel_ids = self.client_channels.get(self, None)
        if not channel_ids:
            return
        for channel_id in channel_ids:
            self.get_channel(channel_id).remove_client(self)
        del self.client_channels[self]