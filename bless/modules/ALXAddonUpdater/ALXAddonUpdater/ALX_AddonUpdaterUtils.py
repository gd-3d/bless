import re

import bpy


def get_addon_preferences(context: bpy.types.Context = bpy.context, addon_name: str = ""):
    addon = context.preferences.addons.get(addon_name)
    if (addon is not None):
        return addon.preferences
    else:
        return None


def ui_refresh(update_status):
    """Redraw the ui once an async thread has completed"""
    for windowManager in bpy.data.window_managers:
        for window in windowManager.windows:
            for area in window.screen.areas:
                area.tag_redraw()


def is_url(url: str):
    if (re.search(pattern=r"^(http\:\/\/[\S]+)$|^(https\:\/\/[\S]+)$", string=url, flags=re.IGNORECASE) is not None):
        return True

    return False
