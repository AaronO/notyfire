/* Notyfire client class */
function Notyfire(url, port, rememberTransport) {
    this.url = url;
    this.port = port;
    this.rememberTransport = rememberTransport ? rememberTransport : false;
    this.listeners = {};

    // Setup and connect socket
    this.socket = new io.Socket(this.url, { port: this.port, rememberTransport : this.rememberTransport });

    var self = this;

    this.socket.addEvent('connect', function() {
        self.onConnect();
    });

    this.socket.addEvent('message', function(data) {
        self.dispatch(data);
    });
}

Notyfire.prototype.connect = function() {
    this.socket.connect();
}

Notyfire.prototype.listen = function(channel_id, func) {
    this.listeners[channel_id] = this.listeners[channel_id] ? this.listeners[channel_id] : [];
    this.listeners[channel_id].push(func);
}

Notyfire.prototype.onConnect = function() {
    // Do nothing right now
}

Notyfire.prototype.dispatch = function(data) {
    for(channel_id in data) {
        var channel_data = data[channel_id];
        for(i in this.listeners[channel_id]) {
            this.listeners[channel_id][i](channel_data);
        }
    }
}

Notyfire.prototype.doAction = function(action, data) {
    var o = {};
    o[action] = data;
    this.socket.send(o);
}

Notyfire.prototype.subscribe = function(channel_ids) {
    this.doAction('subscribe', channel_ids);
}

Notyfire.prototype.unsubscribe = function(channel_ids) {
    this.doAction('unsubscribe', channel_ids);
}

Notyfire.prototype.addEvent = function(event_id, func) {
    this.socket.addEvent(event_id, func);
}