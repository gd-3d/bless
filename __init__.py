## gd-3d blender

## addon init + operator and panel registration autoload.

## required.
bl_info = {
    "name" : "gd-3d blender", 
    "author" : "michaeljared, aaronfranke, yankscally, valyarhal", 
    "description" : "",
    "blender" : (4, 2, 0),
    "version" : (0, 0, 2),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy

from . import gltf_extensions_definitions

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





#region Modue Auto loader

#thank you VERY MUCH to Valy Arhal for this autoload script and all the extra help! <3

from typing import Iterable
import importlib
from os import sep as os_separator
from pathlib import Path


folder_name_blacklist: list[str]=["__pycache__"] 
file_name_blacklist: list[str]=["__init__.py"]
if (bpy.app.version[0]<=4 and bpy.app.version[1]<=1):
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




## hooks found and implemented by michaeljared from this original gist:
## https://gist.github.com/bikemurt/0c36561a29527b98220230282ab11181

class glTF2ExportUserExtension:

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type:ignore [available to blender not vscode and won't throw an error]
        self.Extension = Extension

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}
        
        from . import gltf_extensions_definitions
        n = "OMI_physics_shape"
        # here is where you need to load up the shapes associated with the OMI_physics_body
        shape_array = []
        for obj in bpy.context.scene.objects:
            shape_array.append(obj[n])
                # what the flip
       
        
        gltf_plan.extensions[n] = self.Extension(
            name=n,
            extension={"shapes": shape_array},
            required=False
        )

        pass

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}

        # store possible options as an array, iterate, and then tag the gltf data
        n = "OMI_physics_body"
        if n in blender_object:
            gltf2_object.extensions[n] = self.Extension(
                name=n,
                extension=blender_object[n],
                required=False
            )

#region Property Docs
## TO LOAD PROPERTIES, you must do it here, manually. properties cannot be autoloaded.


# example:
# (you will need a panel_template.py in the same dir as a module, that includes a MyProps class)


# inside /panel_template.py:

# class MyProps(bpy.types.PropertyGroup):
#     my_string : bpy.props.StringProperty(
#         name="string",
#         description="words and stuff") #type: ignore
#endregion

def register_properties():
    bpy.types.Scene.body_properties = bpy.props.PointerProperty(type=gltf_extensions_definitions.OMI_Physics_Body)
    bpy.types.Scene.shape_properties = bpy.props.PointerProperty(type=gltf_extensions_definitions.OMI_Physics_Shape)

def unregister_properties():
    del bpy.types.Scene.body_properties
    del bpy.types.Scene.shape_properties


def register():
    register_class_queue()
    register_properties()

def unregister():
    unregister_class_queue()
    unregister_properties()