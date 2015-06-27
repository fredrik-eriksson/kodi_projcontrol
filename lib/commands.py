"""High level commands that can be used on the projectors"""
import os

import xbmc
import xbmcaddon

import lib
import lib.errors
import lib.helpers

import lib.epson

__addon__ =  xbmcaddon.Addon()

def open_proj():
    """Open the serial device, only intended to be used from do_cmd()
    
    :return: a file descriptor or None
    """
    try:
        fd = os.open(__addon__.getSetting("device"), os.O_RDWR)
        return fd
    except OSError as e:
        lib.helpers.display_error_message(
                "Error when opening projector serial device: {}".format(e)
                )
        return None

def do_cmd(command, **kwargs):
    """Execute a command to the projector and return any output.

    :param command: one of the commands from lib
    :param **kwargs: optional arguments to command

    :return: output from projector or None
    """
    res = None
    fd = open_proj()
    manufacturer = __addon__.getSetting("manufacturer")
    if fd:
        if manufacturer == "Epson":
            model = __addon__.getSetting("epson_model")
            try:
                proj = lib.epson.ProjectorInstance(
                        model,
                        fd, 
                        int(__addon__.getSetting("timeout")))
            except lib.errors.ProjectorError as pe:
                lib.helpers.display_error_message(str(pe))
                return res
        else:
            lib.helpers.display_error_message(
                    "Manufacturer {} is not supported".format(manufacturer))
            return res
        try:
            res = proj.send_command(command, **kwargs)
        except lib.errors.ProjectorError as pe:
            lib.helpers.display_error_message(str(pe))
        os.close(fd)
    if res:
        return res

def start():
    """Start the projector"""
    do_cmd(lib.CMD_PWR_ON)

def stop():
    """Shut down the projector"""
    do_cmd(lib.CMD_PWR_OFF)
    if __addon__.getSetting("lib_update") == "true":
        if __addon__.getSetting("update_music") == "true":
            xbmc.executebuiltin('UpdateLibrary(music)')
        if __addon__.getSetting("update_video") == "true":
            xbmc.executebuiltin('UpdateLibrary(video)')

def toggle_power():
    """Toggle the power to the projector"""
    if do_cmd(lib.CMD_PWR_QUERY):
        stop()
    else:
        start()

def report():
    """Report current power status and used source. The report is both returned
    as a dict and displayed as a kodi notification.
    
    :return: a dict containing 'power' and 'source' entries.
    """

    pwr = do_cmd(lib.CMD_PWR_QUERY)
    src = do_cmd(lib.CMD_SRC_QUERY)
    lib.helpers.display_message("Power on: {}\nSource: {}".format(pwr, src))
    xbmc.executebuiltin("Notification(Kaka, KAKA, 10000)")
    return {"power": pwr, "source": src}

def set_source(source):
    """Set input source for projector. To get a list of valid source strings,
    use GET on /source or call get_available_sources().

    :param source: valid input source string
    """
    manufacturer = __addon__.getSetting("manufacturer")
    if manufacturer == "Epson":
        model = __addon__.getSetting("epson_model")
        src_id = lib.epson.get_source_id(model, source)
        if not src_id:
            lib.helpers.display_error_message(
                    "Invalid source '{}' for this model".format(source)
            )
            return False
    else:
        helpers.display_error_message(
                "Manufacturer {} is not supported".format(Manufacturer))
        return False
    do_cmd(lib.CMD_SRC_SET, source_id=src_id)
    return True

def get_available_sources():
    """Return a list valid sources for the configured projector."""
    manufacturer = __addon__.getSetting("manufacturer")
    if manufacturer == "Epson":
        model = __addon__.getSetting("epson_model")
        return lib.epson.get_valid_sources(model)
    else:
        helpers.display_error_message(
                "Manufacturer {} is not supported".format(Manufacturer))
    return None
