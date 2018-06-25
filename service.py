#!/usr/bin/python2

# -*- coding: utf-8 -*-
# Copyright (c) 2015,2018 Fredrik Eriksson <git@wb9.se>
# This file is covered by the MIT license, read LICENSE for details.

import os
import argparse
import select
import threading

import xbmc
import xbmcaddon
import xbmcgui


import lib
import lib.epson
import lib.errors
try:
    import lib.server
    __server_available__ = True
except ImportError:
    __server_available__ = False

__addon__      = xbmcaddon.Addon()
__server__ = None

def server_available():
    if not __server_available__ and __addon__.getSetting("enabled") == "true":
        lib.helpers.display_error_message("REST API not available, see https://github.com/fredrik-eriksson/kodi_projcontrol for possible reasons")
    return __server_available__

def restart_server():
    """Restart the REST API.
    """
    if not server_available():
        return

    global __server__
    stop_server()
    port = int(__addon__.getSetting("port"))
    address = __addon__.getSetting("address")
    __server__ = threading.Thread(target=lib.server.init_server, args=(port, address))
    __server__.start()
    # wait one second and make sure the server has started
    xbmc.sleep(1000)
    if not __server__.isAlive():
        __server__.join()
        lib.helpers.display_error_message(
                "Failed to start projector web server,\n"\
                "Try to disable and reenable addon")
        __server__ = None
    else:
        lib.helpers.display_message("Started projector server at {}:{}".format(address,port))


def stop_server():
    """Stop the REST API."""
    if not server_available():
        return

    global __server__
    if __server__:
        lib.server.stop_server()
        __server__.join()
        lib.helpers.display_message("Projector API stopped")
    __server__ = None


class ProjectorMonitor(xbmc.Monitor):
    """Subclass of xbmc.Monitor that restarts the twisted web server on
    configuration changes, and starting library updates if configured.
    """
    _update_lock_ = threading.Lock()
    _ongoing_updates_ = set()
    _update_timer_ = None

    def update_libraries(self):
        """Called by the timer to start a new library update if the projector
        is still offline and configuration is set to allow regular library
        updates.
        """
        power_status = lib.commands.report()["power"]
        if not power_status \
                and __addon__.getSetting("lib_update") == "true" \
                and __addon__.getSetting("update_again") == "true":
            if __addon__.getSetting("update_music") == "true":
                xbmc.executebuiltin('UpdateLibrary(music)')
            if __addon__.getSetting("update_video") == "true":
                xbmc.executebuiltin('UpdateLibrary(video)')
        
    def cleanup(self):
        """Remove any lingering timer before exit"""
        with self._update_lock_:
            if self._update_timer_:
                self._update_timer_.cancel()
                self._update_timer_ = None
    

    def onScreensaverActivated(self):
        if __addon__.getSetting("at_ss_start") == "true":
            lib.commands.stop()

    def onScreensaverDeactivated(self):
        if __addon__.getSetting("at_ss_shutdown") == "true":
            lib.commands.start()

    def onSettingsChanged(self):
        if __addon__.getSetting("enabled") == "true":
            restart_server()
        else:
            stop_server()

    def onCleanStarted(self, library):
        self.onScanStarted(library)

    def onCleanFinished(self, library):
        self.onScanFinished(library)
    
    def onScanStarted(self, library):
        self.cleanup()
        with self._update_lock_:
            self._ongoing_updates_.add(library)
        return library

    def onScanFinished(self, library):
        self.cleanup()
        with self._update_lock_:
            self._ongoing_updates_.discard(library)
            if len(self._ongoing_updates_) == 0 \
                    and __addon__.getSetting("lib_update") == "true" \
                    and __addon__.getSetting("update_again") == "true":
                self._update_timer_ = threading.Timer(
                        int(__addon__.getSetting("update_again_at"))*60,
                        self.update_libraries)
                self._update_timer_.start()
        return library


if __name__ == '__main__':
    monitor = ProjectorMonitor()

    if __addon__.getSetting("at_start"):
        lib.commands.start()

    if __addon__.getSetting("enabled") == "true":
        restart_server()

    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            break

    stop_server()
    monitor.cleanup()
    if __addon__.getSetting("at_shutdown"):
        lib.commands.stop(final_shutdown=True)
