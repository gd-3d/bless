bl_info = {
    "name" : "gd-3d bless", 
    "author" : "michaeljared, aaronfranke, yankscally, valyarhal", 
    "description" : "",
    "blender" : (4, 2, 0),
    "version" : (0, 0, 4),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
from . import addon_updater_ops



#region Docs [REQUIRED]

# welcome to the beautiful mess that is developing a blender addon with multiple scripts.

# you will need:
# 1) fake bpy: https://github.com/nutti/fake-bpy-module
# 2) possibly the Blender Development addon in vscode extensions.

# some rules about this autoload:
# 1) there can only be 1 register/deregister function, and it must be in __init.py__ where bl_info is. do not register in other scripts!
# 2) panels and operators are autoloaded, but you must load property classes manually here, example at bottom.
# 3) if everything is setup correctly, reload the addon with F3>reload script (or TODO try make lazy reload button) 

#endregion

#region Module Autoloader

#thank you VERY MUCH to Valy Arhal for this autoload script and all the extra help! <3

from typing import Iterable
import importlib
from os import sep as os_separator
from pathlib import Path


folder_name_blacklist: list[str]=["__pycache__"] 
file_name_blacklist: list[str]=["__init__.py"]
file_name_blacklist.extend(["addon_updater", "addon_updater_ops"])


addon_folders = []
addon_files = []

addon_path_iter = [ Path( __path__[0] ) ]
addon_path_iter.extend(Path( __path__[0] ).iterdir())

for folder_path in addon_path_iter:
    
    
    if ( folder_path.is_dir() ) and ( folder_path.exists() ) and ( folder_path.name not in folder_name_blacklist ):
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

# region Property Docs
## TO LOAD PROPERTIES, you must do it here, manually. properties cannot be autoloaded.


# example:
# (you will need a panel_template.py in the same dir as a module, that includes a MyProps class)


# inside /panel_template.py:

# class MyProps(bpy.types.PropertyGroup):
#     my_string : bpy.props.StringProperty(
#         name="string",
#         description="words and stuff") #type: ignore
#endregion

from . import gltf
from . import bless_keymap_utils


from . import grid

def register_properties():
    bpy.types.Scene.body_properties = bpy.props.PointerProperty(type=gltf.OMI_physics_body)
    bpy.types.Scene.shape_properties = bpy.props.PointerProperty(type=gltf.OMI_physics_shape)
    bpy.types.Scene.unit_size = grid.unit_size

def unregister_properties():
    del bpy.types.Scene.body_properties
    del bpy.types.Scene.shape_properties
    del bpy.types.Scene.unit_size



def register():
    addon_updater_ops.update_path_fix = __path__
    addon_updater_ops.register(bl_info)

    register_class_queue()
    register_properties()

    bless_keymap_utils.bless_CreateKeymaps()

    bpy.context.preferences.use_preferences_save = True

def unregister():
    unregister_class_queue()
    unregister_properties()
    
