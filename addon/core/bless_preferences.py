import bpy
import rna_keymap_ui

from .addon_updater_ops import make_annotations, update_settings_ui
from . import bless_keymap_utils


@make_annotations
class bless_AddonPreferences(bpy.types.AddonPreferences):
    """"""

    bl_idname = __package__


    addon_preference_tabs : bpy.props.EnumProperty(name="", default="HOME", 
        items=[
            ("HOME", "home", "", "HOME", 1),
            ("KEYBINDS", "keybinds", "", "EVENT_K", 1<<1),
            ("SETTINGS", "settings" , "", "PREFERENCES", 1<<2)
        ]) #type:ignore


    auto_check_update : bpy.props.BoolProperty(name="Auto-check for Update", description="If enabled, auto-check for updates using an interval", default=False) #type:ignore

    updater_interval_months : bpy.props.IntProperty(name='Months', description="Number of months between checking for updates", default=0, min=0) #type:ignore
    updater_interval_days : bpy.props.IntProperty(name='Days', description="Number of days between checking for updates", default=7, min=0, max=31) #type:ignore
    updater_interval_hours : bpy.props.IntProperty(name='Hours', description="Number of hours between checking for updates", default=0, min=0, max=23) #type:ignore
    updater_interval_minutes : bpy.props.IntProperty(name='Minutes', description="Number of minutes between checking for updates", default=0, min=0, max=59) #type:ignore


    def draw(self, context:bpy.types.Context):
        preference_box = self.layout

        keymap_configs = context.window_manager.keyconfigs.user
        
        
        preference_box.grid_flow(row_major=True, align=True).prop(self, "addon_preference_tabs", expand=True)

        if (self.addon_preference_tabs == "KEYBINDS"):
            keybinds_column = preference_box.column()

            keymap : bpy.types.KeyMap
            for keymap, keymap_item in bless_keymap_utils.bless_addon_keymaps:
                rna_keymap_ui.draw_kmi([], keymap_configs, keymap, keymap_item, keybinds_column, 0)

        if (self.addon_preference_tabs == "SETTINGS"):
            update_settings_ui(self,context)


def bless_GetPreferences():
    return bpy.context.preferences.addons[__package__].preferences