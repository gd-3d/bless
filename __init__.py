"""
Bless code style:

filename: snake_case.file
class name: UpperCamelCase
everything else: snake_case


Directory catalog: (made on 11/13/24 - v0.1.2)

/addon/ - has all the internal bpy interfaces, automation, and preferences
    alx_module_manager.py
    bless_keymap_utils.py
    addon_updater_ops.py
    bless_preferences.py

/tools/ - operators, properties, .blend files
    grid.py
    autoconvex.py
    quick_test.py
    lock_view.py

/gltf/ - exporting and importing glTF with game related extensions

    gltf_export.py
    gltf_import.py
    TODO:batch_export.py

/physics/
    ! TODO: move all physics related code here
    physics_body.py
    physics_shape.py
    collision_types.py
    collision_layers.py
    collision_mask.py

bless.py
    contains the panel.


"""

import importlib

import bpy

from . import bless, bless_keymap_utils
from .core import grid
from .gltf import gltf_export
from .modules.addon_updater_system.addon_updater import Alx_Addon_Updater
from .modules.Alx_Module_Manager import Alx_Module_Manager
from .user_interface import BLESS_Object_Data_Layouts
from .user_interface.BLESS_Object_Data_Layouts import (
    UIPreset_ObjectDataSheet, UIPreset_ToolBox)

bl_info = {
    "name": "Bless",
    "author": "michaeljared, aaronfranke, yankscally, valerie-bosco",  # gd-3d developers
    "description": "",
    "version": (0, 1, 3),
    "blender": (4, 2, 0),
    "location": "",
    "warning": "",
    "category": "Generic",
    "doc_url": "https://github.com/gd-3d/bless/wiki",
    "tracker_url": "https://github.com/gd-3d/bless/issues",
}


# [REQUIRED] Interface class for GLTF
class glTF2ExportUserExtension(gltf_export.BlessExport):

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        return super().gather_gltf_extensions_hook(gltf_plan, export_settings)

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        return super().gather_node_hook(gltf2_object, blender_object, export_settings)


def register_properties():
    bpy.types.Object.body_properties = bpy.props.PointerProperty(type=bless.OMIPhysicsBody)
    bpy.types.Object.shape_properties = bpy.props.PointerProperty(type=bless.OMIPhysicsShape)
    bpy.types.Object.bless_object_collision_settings = bpy.props.PointerProperty(type=bless.BLESS_ObjectCollisionSettings)

    # Add default bless_class property
    bpy.types.Object.bless_class = bpy.props.EnumProperty(
        name="Godot Class",
        description="Select Godot class for this object",
        items=[("NONE", "None", "No Godot class assigned")],
        default="NONE"
    )

    # persistent-session bless properties
    bpy.types.WindowManager.bless_tools = bpy.props.PointerProperty(type=bless.BlessTools)
    bpy.types.WindowManager.unit_size = grid.unit_size


def unregister_properties():
    del bpy.types.Object.body_properties
    del bpy.types.Object.shape_properties

    del bpy.types.Object.bless_object_collision_settings

    del bpy.types.Object.bless_class

    del bpy.types.WindowManager.bless_tools
    del bpy.types.WindowManager.unit_size


# module loader
module_loader = Alx_Module_Manager(__path__, globals())
addon_updater = Alx_Addon_Updater(__path__[0], bl_info, "Github", "gd-3d", "bless", "https://github.com/gd-3d/bless/releases/")


def register():
    module_loader.developer_register_modules(mute=True)
    addon_updater.register_addon_updater(mute=True)

    bpy.types.VIEW3D_PT_active_tool_duplicate.prepend(UIPreset_ToolBox)
    bpy.types.OBJECT_PT_context_object.prepend(UIPreset_ObjectDataSheet)

    register_properties()
    bless_keymap_utils.bless_CreateKeymaps()
    bpy.context.preferences.use_preferences_save = True


def unregister():
    module_loader.developer_unregister_modules()
    addon_updater.unregister_addon_updater()

    bpy.types.VIEW3D_PT_active_tool_duplicate.remove(UIPreset_ToolBox)
    bpy.types.OBJECT_PT_context_object.remove(UIPreset_ObjectDataSheet)

    module_loader.developer_unregister_modules()
    unregister_properties()


if __name__ == "__main__":
    register()
