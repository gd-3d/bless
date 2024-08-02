Docs [REQUIRED]

welcome to the beautiful mess that is developing a blender addon with multiple scripts.

you will need:
1) fake bpy: https://github.com/nutti/fake-bpy-module
2) possibly the Blender Development addon in vscode extensions.

some rules about this autoload:
1) there can only be 1 register/deregister function, and it must be in __init.py__ where bl_info is. do not register in other scripts!
2) panels and operators are autoloaded, but you must load property classes manually here, example at bottom.
3) if everything is setup correctly, reload the addon with F3>reload script (or TODO try make lazy reload button) 

#endregion




Property Docs
TO LOAD PROPERTIES, you must do it here, manually. properties cannot be autoloaded.


example:
(you will need a panel_template.py in the same dir as a module, that includes a MyProps class)


inside /panel_template.py:

class MyProps(bpy.types.PropertyGroup):
    my_string : bpy.props.StringProperty(
    name="string",
    description="words and stuff") #type: ignore