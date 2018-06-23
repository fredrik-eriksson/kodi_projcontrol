import logging

import flask
import flaskish

import lib.commands

app = flask.Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def start():
    return flask.jsonify([ "power", "source"])

@app.route('/power', methods=['POST', 'GET'])
def power():
    if flask.request.method == 'GET':
        return flask.jsonify(lib.commands.report())

    data = flask.request.get_json()
    ret = {'success': False}
    if data == 'on':
        lib.commands.start()
        ret['success'] = True
    elif data == 'off':
        lib.commands.stop()
        ret['success'] = True
    elif data == 'toggle':
        lib.commands.toggle_power()
        ret['success'] = True
    return flask.jsonify(ret)

@app.route('/source', methods=['POST', 'GET'])
def source():
    valid_sources = lib.commands.get_available_sources()
    if flask.request.method == 'GET':
        return flask.jsonify({'sources': valid_sources})

    data = flask.request.get_json()
    if data in valid_sources:
        return flask.jsonify({'success': lib.commands.set_source(data)})
    return flask.jsonify({'success': False})


def init_server(port, address):
    """Start the flask web server.
    
    :param port: port to listen on
    :param address: address to bind to
    """
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app.run(host=address, port=port)
