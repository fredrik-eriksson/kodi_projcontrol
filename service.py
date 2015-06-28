#!/usr/bin/python2
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
import lib.server

__addon__      = xbmcaddon.Addon()
__server__ = None


def restart_server():
    """Restart the twisted web server.
    TODO: This only works the first time the server is started as the twisted
    server cannot be started a second time after being stopped. How to fix?
    """
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
        lib.helpers.display_message(
                "Failed to start projector web server,\n"\
                "Try to disable and reenable addon")
        __server__ = None
    else:
        lib.helpers.display_message("Started projector server at {}:{}".format(address,port))


def stop_server():
    """Stop the twisted web server."""
    global __server__
    if __server__:
        lib.server.stop_server()
        __server__.join()
        lib.helpers.display_message("Projector web server stopped")
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
        power_status = lib.commands.do_cmd(lib.CMD_PWR_QUERY)
        self._update_lock_.acquire()
        if self._update_timer_:
            self._update_timer_.cancel()
            self._update_timer_ = None
        if not power_status \
                and __addon__.getSetting("lib_update") == "true" \
                and __addon__.getSetting("update_again") == "true":
            if __addon__.getSetting("update_music") == "true":
                xbmc.executebuiltin('UpdateLibrary(music)')
            if __addon__.getSetting("update_video") == "true":
                xbmc.executebuiltin('UpdateLibrary(video)')
        
    def cleanup(self):
        """Remove any lingering timer before exit"""
        self._update_lock_.acquire()
        if self._update_timer_:
            self._update_timer_.cancel()
            self._update_timer_ = None
    
    def onSettingsChanged(self):
        if __addon__.getSetting("enabled") == "true":
            pass
            #restart_server()
        else:
            stop_server()

    def onCleanStarted(self, library):
        self.onScanStarted(library)

    def onCleanFinished(self, library):
        self.onScanFinished(library)
    
    def onScanStarted(self, library):
        self._update_lock_.acquire()
        if self._update_timer_:
            self._update_timer_.cancel()
            self._update_timer_ = None
        self._ongoing_updates_.add(library)
        self._update_lock_.release()
        return library

    def onScanFinished(self, library):
        self._update_lock_.acquire()
        self._ongoing_updates_.discard(library)
        if self._update_timer_:
            self._update_timer_.cancel()
            self._update_timer_ = None
        if len(self._ongoing_updates_) == 0 \
                and __addon__.getSetting("lib_update") == "true" \
                and __addon__.getSetting("update_again") == "true":
            self._update_timer_ = threading.Timer(
                    int(__addon__.getSetting("update_again_at"))*60,
                    self.update_libraries)
            self._update_timer_.start()
        self._update_lock_.release()
        return library


if __name__ == '__main__':
    monitor = ProjectorMonitor()

    if __addon__.getSetting("enabled") == "true":
        restart_server()

    while True:
        if monitor.abortRequested():
            stop_server()
            monitor.cleanup()
            break

        xbmc.sleep(1000)
