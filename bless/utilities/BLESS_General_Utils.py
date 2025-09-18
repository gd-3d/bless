import json
from typing import Optional

import bpy


def GET_BlessPreferences(context: bpy.types.Context):
    if (hasattr(context, "preferences")) and (context.preferences is not None):
        addon = context.preferences.addons.get(__package__)
        if (addon is not None):
            return addon.preferences

    return None


def DEV_BlessConsolePrint(message: str, header: Optional[bool] = False):
    separator = "=" * 50
    if header:
        print(f"\n{separator}")
        print(f"[BLESS] {message}")
        print(f"{separator}")
    else:
        print(f"[BLESS] {message}")


def get_profile_classes(self, context):
    """Get classes from game profile for enum"""
    # Always start with None as the first option
    items = [("NONE", "None", "No Godot class assigned")]
    tools = context.window_manager.bless_tools

    try:
        if tools.profile_filepath:
            with open(tools.profile_filepath, 'r') as f:
                profile_data = json.load(f)
                for class_name in profile_data.get("classes", {}):
                    items.append((class_name.upper(), class_name, f"Godot {class_name} class"))
    except Exception as e:
        print(f"Error loading profile classes: {e}")

    return items
