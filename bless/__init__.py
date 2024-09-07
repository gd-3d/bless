bl_info = {
    "name" : "bless", 
    "author" : "michaeljared, aaronfranke, yankscally, valyarhal", 
    "description" : "",
    "blender" : (4, 2, 0),
    "version" : (0, 1, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy

#thank you VERY MUCH to Valy Arhal for this autoload script and all the extra help! <3

#region Module Autoloader

from typing import Iterable
import importlib
from os import name as os_name
from os import sep as os_separator
from pathlib import WindowsPath, PosixPath


folder_name_blacklist: list[str]=["__pycache__"] 
file_name_blacklist: list[str]=["__init__.py"]
file_name_blacklist.extend(["addon_updater", "addon_updater_ops"])


addon_folders = []
addon_files = []

PATHTYPE = ""
match os_name:
    case "posix":
        PATHTYPE = "PosixPath"
    case "nt":
        PATHTYPE = "WindowsPath"

addon_path_iter = [ eval(PATHTYPE)( __path__[0] ) ]
addon_path_iter.extend(eval(PATHTYPE)( __path__[0] ).iterdir())

for folder_path in addon_path_iter:
    
    if (  folder_path.is_dir() ) and ( folder_path.exists() ) and ( folder_path.name not in folder_name_blacklist ):
        addon_folders.append( folder_path )

        for subfolder_path in folder_path.iterdir():
            if ( subfolder_path.is_dir() ) and ( subfolder_path.exists()):
                addon_path_iter.append( subfolder_path )
                addon_folders.append( subfolder_path )

addon_files = [[folder_path, file_name.name[0:-3]] for folder_path in addon_folders for file_name in folder_path.iterdir() if ( file_name.is_file() ) and ( file_name.name not in file_name_blacklist ) and ( file_name.suffix == ".py" )]

for folder_file_batch in addon_files:
    file = folder_file_batch[1]
    
    if (file not in locals()):
        relative_path = str(folder_file_batch[0].relative_to( __path__[0] ) ).replace(os_separator,"." )

        import_line = f"from . {relative_path if relative_path != '.' else ''} import {file}"
        exec(import_line)
    else:
        reload_line = f"{file} = importlib.reload({file})"
        exec(reload_line)

import inspect
_class_object_list = tuple(alx_class[1] for file_batch in addon_files for alx_class in inspect.getmembers(eval(file_batch[1]), inspect.isclass) )

ClassQueue = _class_object_list



def register_class_queue():
    for Class in ClassQueue:
        try:
            bpy.utils.register_class(Class)
        except:
            try:
                bpy.utils.unregister_class(Class)
                bpy.utils.register_class(Class)
            except:
                pass

def unregister_class_queue():
    for Class in ClassQueue:
        try:
            bpy.utils.unregister_class(Class)
        except:
            print("Can't Unregister", Class)

# again, huge thanks Valy Arhal.

#endregion




# this allows using this class outside of __init__.py
from .gltf import gltf_export
class glTF2ExportUserExtension(gltf_export.bless_glTF2Extension):

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type:ignore [available to blender not vscode and won't throw an error]
        self.Extension = Extension

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        return super().gather_gltf_extensions_hook(gltf_plan, export_settings)
    
    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        return super().gather_node_hook(gltf2_object, blender_object, export_settings)

#import bless_preferences
from .gltf import physics
from .map import grid
from .map import panel

def register_properties():
    #bpy.types.World.game = bpy.props.PointerProperty(type=bless_preferences.BlessGameConfig)

    bpy.types.Scene.body_properties = bpy.props.PointerProperty(type=physics.OMI_physics_body)
    bpy.types.Scene.shape_properties = bpy.props.PointerProperty(type=physics.OMI_physics_shape)
    bpy.types.Scene.map_properties = bpy.props.PointerProperty(type=panel.MapProperties)
    bpy.types.Scene.unit_size = grid.unit_size

def unregister_properties():
    del bpy.types.Scene.body_properties
    del bpy.types.Scene.shape_properties
    del bpy.types.Scene.unit_size




from . import addon_updater_ops
from . import bless_keymap_utils


def register():
    addon_updater_ops.update_path_fix = __path__
    addon_updater_ops.register(bl_info)

    register_class_queue()
    register_properties()

    bless_keymap_utils.bless_CreateKeymaps()

    bpy.context.preferences.use_preferences_save = True

def unregister():
    addon_updater_ops.unregister()

    unregister_class_queue()
    unregister_properties()
    
