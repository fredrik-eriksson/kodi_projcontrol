import xbmcgui

def display_error_message(
        message,
        title="Projector Command Failed",
        type_=xbmcgui.NOTIFICATION_ERROR,
        time=1000,
        sound=True):
    """Display an error message in the Kodi interface"""
    display_message(message, title=title, type_=type_, time=time, sound=sound)

def display_message(
        message, 
        title="Report from projector", 
        type_=xbmcgui.NOTIFICATION_INFO,
        time=5000,
        sound=False):
    """Display an informational message in the Kodi interface"""

    dialog = xbmcgui.Dialog()
    dialog.notification(
            title, 
            message,
            type_,
            time,
            sound)

