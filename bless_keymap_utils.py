# import bpy

# #don't rename to generic list like addon_keymaps, can cause issues with shadow naming
# bless_addon_keymaps = []

# def bless_EditKeymaps(KeyconfigSource="Blender", ConfigSpaceName="", ItemidName="", OperatorID="", MapType="", Key="", UseShift=False, UseCtrl=False, UseAlt=False, TriggerType="PRESS", Active=False):
#     """KeyconfigSource : [Blender, Blender addon, Blender user]"""
#     if (KeyconfigSource != "") and (ConfigSpaceName != ""):
#         try:
#             WindowManager = bpy.context.window_manager
#             match KeyconfigSource:
#                 case "Blender":
#                     DefaultKeyConfigs = WindowManager.keyconfigs.default
#                 case "Blender addon":
#                     DefaultKeyConfigs = WindowManager.keyconfigs.addon
#                 case "Blender user":
#                     DefaultKeyConfigs = WindowManager.keyconfigs.user

#             DefaultKeyMaps = DefaultKeyConfigs.keymaps
#             KeymapItems = DefaultKeyMaps[ConfigSpaceName].keymap_items
#             for KeymapItem in KeymapItems:
#                 if (OperatorID == ""):
#                     if (KeymapItem is not None) and (KeymapItem.idname == ItemidName):
#                         if (MapType != ""):
#                             KeymapItem.map_type = MapType
#                         if (Key != ""):
#                             KeymapItem.type = Key
#                         KeymapItem.shift = UseShift
#                         KeymapItem.ctrl = UseCtrl
#                         KeymapItem.alt = UseAlt
#                         KeymapItem.value = TriggerType
#                         KeymapItem.active = Active

#                 if (OperatorID != ""):
#                     if (KeymapItem is not None) and (KeymapItem.properties is not None) and (KeymapItem.idname == ItemidName) and (KeymapItem.properties.name == OperatorID):
#                         if (MapType != ""):
#                             KeymapItem.map_type = MapType
#                         if (Key != ""):
#                             KeymapItem.type = Key
#                         KeymapItem.shift = UseShift
#                         KeymapItem.ctrl = UseCtrl
#                         KeymapItem.alt = UseAlt
#                         KeymapItem.value = TriggerType
#                         KeymapItem.active = Active
#         except Exception as error:
#             pass

# def bless_KeymapRegister(keymap_call_type="", config_space_name="", space_type="EMPTY", region_type="WINDOW", addon_class=None, key="NONE", key_modifier="NONE", use_shift=False, use_ctrl=False, use_alt=False, trigger_type="PRESS", **kwargs):
#     """
#     Available keymap_call_type: ["DEFAULT", "OPERATOR", "MENU", "PANEL", "PIE"]
#     """

#     wm = bpy.context.window_manager
#     kmc = wm.keyconfigs.addon

#     keymap_call_id = None
#     match keymap_call_type:
#         case "DEFAULT":
#             keymap_call_id = addon_class
#         case "OPERATOR":
#             keymap_call_id = addon_class.bl_idname
#         case "MENU":
#             keymap_call_id = "wm.call_menu"
#         case "PANEL":
#             keymap_call_id = "wm.call_panel"
#         case "PIE":
#             keymap_call_id = "wm.call_menu_pie"

#     if (kmc is not None):
#         Keymap : bpy.types.KeyMap = kmc.keymaps.new(name=config_space_name , space_type=space_type, region_type=region_type, modal=False, tool=False)
#         KeymapItem = Keymap.keymap_items.new(idname=keymap_call_id, type=key, key_modifier=key_modifier, shift=use_shift, ctrl=use_ctrl, alt=use_alt, value=trigger_type, head=True)

#         if (KeymapItem.properties is not None):
#             if (keymap_call_type in ["PANEL", "MENU", "PIE"]):
#                 KeymapItem.properties.name = addon_class.bl_idname

#             for property, value in kwargs.items():
#                 if (hasattr(KeymapItem.properties, f"{property}")):
#                     setattr(KeymapItem.properties, property, value)

#         else:
#             print(f"KeymapItem.properties: {KeymapItem.properties}")

#         bless_addon_keymaps.append((Keymap, KeymapItem))
#     else:
#         print("keymap error")


# def bless_CreateKeymaps():
#     """
#     creates the addon's keymaps \n
#     [takes no parameters]
#     """

#     # add keymaps here with the functions above edit to change default keymaps create for new keymaps
#     #bless_CreateKeymaps()
#     pass
