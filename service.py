#!/usr/bin/python2

# -*- coding: utf-8 -*-
# Copyright (c) 2015,2018 Fredrik Eriksson <git@wb9.se>
# This file is covered by the BSD-3-Clause license, read LICENSE for details.

import os
import argparse
import datetime
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
        lib.helpers.display_error_message(32200)
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
        lib.helpers.display_error_message(32201)
        __server__ = None
    else:
        lib.helpers.display_message(32300, " {}:{}".format(address,port))


def stop_server():
    """Stop the REST API."""
    if not server_available():
        return

    global __server__
    if __server__:
        lib.server.stop_server()
        __server__.join()
        lib.helpers.display_message(32301)
    __server__ = None


class ProjectorMonitor(xbmc.Monitor):
    """Subclass of xbmc.Monitor that restarts the twisted web server on
    configuration changes, and starting library updates if configured.
    """
    _update_lock_ = threading.Lock()
    _ongoing_updates_ = set()
    _update_timer_ = None
    _ss_activation_timer_ = None
    _last_power_command_ = datetime.datetime.fromtimestamp(0)

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
        if self._ss_activation_timer_:
            self._ss_activation_timer_.cancel()
    
        with self._update_lock_:
            if self._update_timer_:
                self._update_timer_.cancel()
                self._update_timer_ = None

    def onScreensaverActivated(self):
        if __addon__.getSetting("at_ss_start") == "true":
            self._ss_activation_timer_ = threading.Timer(
                    int(__addon__.getSetting("at_ss_start_delay")),
                    lib.commands.stop)
            self._ss_activation_timer_.start()

    def onScreensaverDeactivated(self):
        if self._ss_activation_timer_:
            self._ss_activation_timer_.cancel()

        if __addon__.getSetting("at_ss_shutdown") == "true":
            min_turnaround = int(__addon__.getSetting("min_turnaround"))
            time_since_stop = datetime.datetime.now() - _last_power_command_
            if time_since_stop.days == 0 and time_since_stop.seconds < min_turnaround:
                xbmc.sleep((min_turnaround-time_since_stop.seconds)*1000)
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
