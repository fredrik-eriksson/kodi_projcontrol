"""Module for communicating with Epson projectors supporting the ESC/VP21
protocol over RS232 serial interface.

Protocol description fetched on 2015-06-26 from
https://files.support.epson.com/pdf/pltw1_/pltw1_cm.pdf
"""

import os
import select

import xbmc

import lib
import lib.commands
import lib.errors

# List of all valid models and their input sources
# Remember to add new models to the settings.xml-file as well
_valid_sources_ = {
        "TW3200": {
            "Component":            "10",
            "Component - YCbCr":    "14",
            "Component - YPbPr":    "15",
            "Component - Auto":     "1F",
            "PC":                   "20",
            "HDMI1":                "30",
            "HDMI2":                "A0",
            "Video":                "40",
            "RCA":                  "41",
            "S-Video":              "42"
            }
        }

# map the generic commands to ESC/VP21 commands
_command_mapping_ = {
        lib.CMD_PWR_ON: "PWR ON",
        lib.CMD_PWR_OFF: "PWR OFF",
        lib.CMD_PWR_QUERY: "PWR?",

        lib.CMD_SRC_QUERY: "SOURCE?",
        lib.CMD_SRC_SET: "SOURCE {source_id}"
        }

def get_valid_sources(model):
    """Return all valid source strings for this model"""
    if model in _valid_sources_:
        return _valid_sources_[model].keys()
    return None

def get_source_id(model, source):
    """Return the "real" source ID based on projector model and human readable
    source string"""
    if model in _valid_sources_ and source in _valid_sources_[model]:
        return _valid_sources_[model][source]
    return None

class ProjectorInstance:
    
    def __init__(self, model, ser, timeout=5):
        """Class for managing Epson projectors

        :param model: Epson model
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
        """Verify that the projecor is ready to receive commands. The projector
        is ready when it returns with a colon when sending carriage return to
        it.
        """
        self._send_command("\r")
        res = ""
        while res is not None:
            res = self._read_response()
            if res.endswith(":") :
                return True
            self._send_command("\r")
        return False

    def _read_response(self):
        """Read response from projector"""
        read = ""
        res = ""
        while not read.endswith(":"):
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

        part = res.split('\r', 1)
        xbmc.log("projector responded: '{}'".format(part[0]))
        return part[0]


    def _send_command(self, cmd_str):
        """Send command to the projector.

        :param cmd_str: Full raw command string to send to the projector
        """
        ret = None
        try:
            self.serial.write("{}\r".format(cmd_str))
        except OSError as e:
            raise lib.errors.ProjectorError(
                    "Error when Sending command '{}' to projector: {}".\
                        format(cmd_str, e)
                    )
            return ret

        if cmd_str.endswith('?'):
            ret = self._read_response()
            while "=" not in ret and ret != 'ERR':
                ret = self._read_response()
            if ret == 'ERR':
                xbmc.log("Error!")
                return None
            xbmc.log("No Error!")
            ret = ret.split('=', 1)[1]
            if ret == "01":
                ret = True
            elif ret == "00":
                ret = False
            elif ret in [
                    _valid_sources_[self.model][x] for x in
                        _valid_sources_[self.model]
                    ]:
                ret = [
                        x for x in 
                        _valid_sources_[self.model] if
                            _valid_sources_[self.model][x] == ret][0]
        
            return ret

    def send_command(self, command, **kwargs):
        """Send command to the projector.

        :param command: A valid command from lib
        :param **kwargs: Optional parameters to the command. For Epson the only
            valid keyword is "source_id" on CMD_SRC_SET.

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

        xbmc.log("sending command '{}'".format(cmd_str))
        res = self._send_command(cmd_str)
        xbmc.log("send_command returned {}".format(res))
        return res




