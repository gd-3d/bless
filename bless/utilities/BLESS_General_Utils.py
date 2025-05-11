import bpy


def GET_BlessPreferences(context: bpy.types.Context):
    if (hasattr(context, "preferences")) and (context.preferences is not None):
        addon = context.preferences.addons.get(__package__)
        if (addon is not None):
            return addon.preferences

    return None
