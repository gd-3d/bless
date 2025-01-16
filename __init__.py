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

from . import bless
from . import bless_keymap_utils
from .modules.addon_updater_system.addon_updater import Alx_Addon_Updater
from .modules.Alx_Module_Manager import Alx_Module_Manager
from .gltf import gltf_export
from .core import grid

bl_info = {
    "name": "bless",
    "author": "michaeljared, aaronfranke, yankscally, valyarhal",  # gd-3d developers
    "description": "",
    "version": (0, 1, 3),
    "blender": (4, 2, 0),
    "location": "",
    "warning": "",
    "category": "Generic",
    "doc_url": "https://github.com/gd-3d/bless/wiki",
    "tracker_url": "https://github.com/gd-3d/bless/issues",
}


# glTF2ExportUserExtension needs to be defined inside the __init__, this is a dummy class to allow the implementation to be outside the __init__
class glTF2ExportUserExtension(gltf_export.BlessExport):

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension  # type:ignore [available to blender not vscode and won't throw an error]
        self.Extension = Extension

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        return super().gather_gltf_extensions_hook(gltf_plan, export_settings)

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        return super().gather_node_hook(gltf2_object, blender_object, export_settings)


# import bless_preferences
def register_properties():
    bpy.types.Object.body_properties = bpy.props.PointerProperty(type=bless.OMIPhysicsBody)
    bpy.types.Object.shape_properties = bpy.props.PointerProperty(type=bless.OMIPhysicsShape)
    bpy.types.Object.collision_types = bpy.props.PointerProperty(type=bless.BlessCollisionTypes)
    bpy.types.Object.collision_layers = bpy.props.PointerProperty(type=bless.BlessCollisionLayers)
    bpy.types.Object.collision_mask = bpy.props.PointerProperty(type=bless.BlessCollisionMaskLayers)

    # Add default bless_class property
    bpy.types.Object.bless_class = bpy.props.EnumProperty(
        name="Godot Class",
        description="Select Godot class for this object",
        items=[("NONE", "None", "No Godot class assigned")],
        default="NONE"
    )

    # note[valy] this should not be saved on scene rather window_manager as window manager is session dependant and will persist until blender is closed,
    # while scene will end up duplicating for each blender scene the settings and will lead to settings missmatch
    bpy.types.WindowManager.bless_tools = bpy.props.PointerProperty(type=bless.BlessTools)
    bpy.types.WindowManager.unit_size = grid.unit_size


def unregister_properties():
    del bpy.types.Object.body_properties
    del bpy.types.Object.shape_properties
    del bpy.types.Object.collision_types
    del bpy.types.Object.collision_layers
    del bpy.types.Object.collision_mask
    del bpy.types.Object.bless_class

    del bpy.types.WindowManager.bless_tools
    del bpy.types.WindowManager.unit_size


# module loader
module_loader = Alx_Module_Manager(__path__, globals())
addon_updater = Alx_Addon_Updater(__path__[0], bl_info, "Github", "gd-3d", "bless", "https://github.com/gd-3d/bless/releases/")


def register():
    module_loader.developer_register_modules(mute=True)
    addon_updater.register_addon_updater(mute=True)

    register_properties()
    bless_keymap_utils.bless_CreateKeymaps()
    bpy.context.preferences.use_preferences_save = True


def unregister():
    module_loader.developer_unregister_modules()
    addon_updater.unregister_addon_updater()

    module_loader.developer_unregister_modules()
    unregister_properties()


if __name__ == "__main__":
    register()
