# module loader
import importlib
from .AlxModuleManager import (
    Alx_Module_Loader
)


from . import bless_keymap_utils
from . import addon_updater_ops
from .map import grid
from . import bless
from .gltf import gltf_export
import bpy
bl_info = {
    "name": "bless",
    "author": "michaeljared, aaronfranke, yankscally, valyarhal",
    "description": "",
    "version": (0, 1, 2),
    "blender": (4, 2, 0),
    "location": "",
    "warning": "",
    "category": "Generic"
}


# allows a glTF2ExportUserExtension class to be defined outside __init__
class glTF2ExportUserExtension(gltf_export.bless_glTF2Extension):

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

    del bpy.types.WindowManager.bless_tools
    del bpy.types.WindowManager.unit_size


# module loader
module_loader = Alx_Module_Loader()
module_loader.developer_blacklist_file({"addon_updater", "addon_updater_ops"})


def register():
    try:
        addon_updater_ops.update_path_fix = __path__
        addon_updater_ops.register(bl_info)
    except:
        pass

    module_loader.developer_register_modules(__path__, globals())

    register_properties()

    bless_keymap_utils.bless_CreateKeymaps()

    bpy.context.preferences.use_preferences_save = True


def unregister():
    addon_updater_ops.unregister()

    module_loader.developer_unregister_modules()

    unregister_properties()
