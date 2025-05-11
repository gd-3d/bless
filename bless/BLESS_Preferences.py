import bpy

from .modules.ALXAddonUpdater.ALXAddonUpdater.ALX_AddonUpdaterUI import \
    update_settings_ui


class bless_AddonPreferences(bpy.types.AddonPreferences):
    """"""

    bl_idname = __package__

    addon_preference_tabs: bpy.props.EnumProperty(
        name="", default="HOME",
        items=[
            ("HOME", "home", "", "HOME", 1),
            ("KEYBINDS", "keybinds", "", "EVENT_K", 1 << 1),
            ("SETTINGS", "settings", "", "PREFERENCES", 1 << 2)
        ]
    )  # type:ignore

    auto_check_update: bpy.props.BoolProperty(name="Auto-check for Update", description="If enabled, auto-check for updates using an interval", default=False)  # type:ignore

    updater_interval_months: bpy.props.IntProperty(name='Months', description="Number of months between checking for updates", default=0, min=0)  # type:ignore
    updater_interval_days: bpy.props.IntProperty(name='Days', description="Number of days between checking for updates", default=7, min=0, max=31)  # type:ignore
    updater_interval_hours: bpy.props.IntProperty(name='Hours', description="Number of hours between checking for updates", default=0, min=0, max=23)  # type:ignore
    updater_interval_minutes: bpy.props.IntProperty(name='Minutes', description="Number of minutes between checking for updates", default=0, min=0, max=59)  # type:ignore

    def draw(self, context: bpy.types.Context):
        preference_box: bpy.types.UILayout = self.layout
        preference_box.grid_flow(row_major=True, align=True).prop(self, "addon_preference_tabs", expand=True)

        if (self.addon_preference_tabs == "HOME"):
            from .icons import icons_dictionary
            row = preference_box.split(factor=0.33)
            row.separator()
            row.operator("wm.url_open", text="BLESS Discord", icon_value=icons_dictionary["discord_icon"]).url = ""
            row.separator()

        # if (self.addon_preference_tabs == "KEYBINDS"):
        #     keybinds_column = preference_box.column()

        #     keymap: bpy.types.KeyMap
        #     for keymap, keymap_item in bless_keymap_utils.bless_addon_keymaps:
        #         rna_keymap_ui.draw_kmi([], keymap_configs, keymap, keymap_item, keybinds_column, 0)

        if (self.addon_preference_tabs == "SETTINGS"):
            update_settings_ui(context, preference_box)

# keymap_configs = context.window_manager.keyconfigs.user

# class BlessGameConfig(bpy.types.PropertyGroup):
#     game: bpy.props.StringProperty(name="Game", description="Title of your project.", default="My Game")  # type:ignore
#     game_directory: bpy.props.StringProperty(name="Game Directory", description="Directory of the game.", default="C:\'")  # type:ignore
