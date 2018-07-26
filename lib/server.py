# -*- coding: utf-8 -*-
# Copyright (c) 2015,2018 Fredrik Eriksson <git@wb9.se>
# This file is covered by the BSD-3-Clause license, read LICENSE for details.

import json
import logging

from bottle import get, post, request, response, run

import lib.commands

@get('/')
def start():
    response.content_type = "application/json"
    return json.dumps([ "power", "source"])

@get('/power')
def power():
    response.content_type = "application/json"
    return json.dumps(lib.commands.report())

@post('/power')
def power_req():
    response.content_type = "application/json"
    data = request.json
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
    return json.dumps(ret)

@get('/source')
def source():
    response.content_type = "application/json"
    valid_sources = lib.commands.get_available_sources()
    return flask.jsonify({'sources': valid_sources})

@post('/source')
def source_req():
    response.content_type = "application/json"
    valid_sources = lib.commands.get_available_sources()
    data = request.json
    if data in valid_sources:
        return json.loads({'success': lib.commands.set_source(data)})
    return json.loads({'success': False})


def init_server(port, address):
    """Start the bottle web server.
    
    :param port: port to listen on
    :param address: address to bind to
    """
    run(host=address, port=port)
