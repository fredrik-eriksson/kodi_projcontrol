# -*- coding: utf-8 -*-
# Copyright (c) 2015,2018 Fredrik Eriksson <git@wb9.se>
#               2018 Petter Reinholdtsen <pere@hungry.com>
# This file is covered by the MIT license, read LICENSE for details.

"""Module for communicating with BenQ projectors supporting RS232
serial interface.

Protocol description fetched on 2020-07-04 from
https://business-display.benq.com/content/dam/bb/en/product/projector/corporate/lh770/quick-start-guide/lh770-rs232-control-guide-0-windows7-windows8-winxp.pdf

"""

import os
import re
import select

import serial

import lib.commands
import lib.errors
from lib.helpers import log

# List of all valid models and their input sources
# Remember to add new models to the settings.xml-file as well
_valid_sources_ = {
        "535 series": {
            "COMPUTER/YPbPr":		"RGB",
            "COMPUTER 2/YPbPr2":	"RGB2",
			"HDMI(MHL)":			"hdmi",
			"HDMI 2(MHL2)":			"hdmi2",
			"Composite":			"vid",
			"S-Video":				"svid",
            }
        }

# map the generic commands to ESC/VP21 commands
_command_mapping_ = {
        lib.CMD_PWR_ON: "<CR>*pow=on#<CR>",
        lib.CMD_PWR_OFF: "<CR>*pow=off#<CR>",
        lib.CMD_PWR_QUERY: "<CR>*pow=?#<CR>",

        lib.CMD_SRC_QUERY: "<CR>*sour=?#<CR>",
        lib.CMD_SRC_SET: "<CR>*sour={source_id}#<CR>",
        }

_serial_options_ = {
        "baudrate": 115200,
        "bytesize": serial.EIGHTBITS,
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE
}

def get_valid_sources(model):
    """Return all valid source strings for this model"""
    if model in _valid_sources_:
        return list(_valid_sources_[model].keys())
    return None

def get_serial_options():
    return _serial_options_

def get_source_id(model, source):
    """Return the "real" source ID based on projector model and human readable
    source string"""
    if model in _valid_sources_ and source in _valid_sources_[model]:
        return _valid_sources_[model][source]
    return None

class ProjectorInstance:

    def __init__(self, model, ser, timeout=5):
        """Class for managing BenQ projectors

        :param model: BenQ model
        :param ser: open Serial port for the serial console
        :param timeout: time to wait for response from projector
        """
        self.serial = ser
        self.timeout = timeout
        self.model = model
        res = self._verify_connection()
        if not res:
            raise lib.errors.ProjectorError(
                    "Could not verify ready-state of projector"
                    #"Verify returned {}".format(res)
                    )


    def _verify_connection(self):
        """Verify that the projecor is ready to receive commands.  Use the
        <CR>*ltim=?#<CR> command to see if we get a valid response.

        """
        res = self._send_command("<CR>*ltim=?#<CR>")
        return res is not None

    def _read_response(self):
        """Read response from projector"""
        read = ""
        res = ""
        # Match either <CR>*pow=off#<CR> or <CR>*ltim=?#<CR>
        while not re.match('(\([^?]*\)|\(.*\?\)\([-0-9]*,[0-9]*\))', res):
            r, w, x = select.select([self.serial.fileno()], [], [], self.timeout)
            if len(r) == 0:
                raise lib.errors.ProjectorError(
                        "Timeout when reading response from projector"
                        )
            for f in r:
                try:
                    read = os.read(f, 256)
                    res += read
                except OSError as e:
                    raise lib.errors.ProjectorError(
                            "Error when reading response from projector: {}".format(e),
                            )
                    return None

        part = res.split('\n', 1)
        log("projector responded: '{}'".format(part[0]))
        return part[0]


    def _send_command(self, cmd_str):
        """Send command to the projector.

        :param cmd_str: Full raw command string to send to the projector
        """
        ret = None
        try:
            self.serial.write("{}\n".format(cmd_str))
        except OSError as e:
            raise lib.errors.ProjectorError(
                    "Error when Sending command '{}' to projector: {}".\
                        format(cmd_str, e)
                    )
            return ret

        ret = self._read_response()
        while ")" not in ret and ret != '?':
            ret = self._read_response()
        if ret == '?':
            log("Error, command not understood by projector!")
            return None
        log("Command sent successfully!")
        if cmd_str.endswith('?)'):
            r = re.match('\(.+\)\(([-\d]+),(\d+)\)', ret)
            ret = r.group(2)
            if cmd_str in _boolean_commands:
                if int(ret) == 1:
                    ret = True
                elif int(ret) == 0:
                    ret = False
                else:
                    log("Error, unable to parse boolean value!")
                    return None
            elif ret in [
                    _valid_sources_[self.model][x] for x in
                        _valid_sources_[self.model]
                    ]:
                ret = [
                        x for x in
                        _valid_sources_[self.model] if
                            _valid_sources_[self.model][x] == ret][0]

            return ret
        else:
            return None

    def send_command(self, command, **kwargs):
        """Send command to the projector.

        :param command: A valid command from lib
        :param **kwargs: Optional parameters to the command. For BenQ the
            valid keyword is "source_id" on CMD_SRC_SET

        :return: True or False on CMD_PWR_QUERY, a source string on
            CMD_SRC_QUERY, otherwise None.
        """
        if not command in _command_mapping_:
            raise lib.errors.InvalidCommandError(
                    "Command {} not supported".format(command)
                    )

        if command == lib.CMD_SRC_SET:
            cmd_str = _command_mapping_[command].format(**kwargs)
        else:
            cmd_str = _command_mapping_[command]

        log("sending command '{}'".format(cmd_str))
        res = self._send_command(cmd_str)
        log("send_command returned {}".format(res))
        return res
