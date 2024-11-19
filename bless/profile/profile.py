import bpy
import json
from bpy.props import StringProperty, EnumProperty, PointerProperty

class BlessClassProperties(bpy.types.PropertyGroup):
    """Base class for dynamic properties"""
    pass

def get_profile_classes(self, context):
    """Get classes from game profile for enum"""
    items = []
    tools = context.window_manager.bless_tools
    
    try:
        if tools.profile_filepath:
            with open(tools.profile_filepath, 'r') as f:
                profile_data = json.load(f)
                for class_name in profile_data.get("classes", {}):
                    items.append((class_name, class_name, ""))
    except Exception as e:
        print(f"Error loading profile classes: {e}")
    
    return items if items else [("NONE", "No Classes", "")]

class BlessSelectGameProfile(bpy.types.Operator):
    """Select Game Profile Path"""
    bl_idname = "object.select_game_profile"
    bl_label = "Select Game Profile"
    
    filepath: StringProperty(subtype='FILE_PATH')
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        tools = context.window_manager.bless_tools
        tools.profile_filepath = self.filepath
        # After setting the filepath, load the profile
        bpy.ops.object.load_game_profile()
        return {'FINISHED'}

class BlessClassFactory(bpy.types.Operator):
    """Create dynamic properties from game profile"""
    bl_idname = "object.create_dynamic_class"
    bl_label = "Create Dynamic Class"

    def create_dynamic_class(self, class_name, properties):
        # Create a new type dynamically
        new_class = type(
            f"Bless{class_name}Properties",
            (BlessClassProperties,),
            {
                "__annotations__": {},
                "bl_idname": f"bless.{class_name.lower()}_properties",
                "bl_label": class_name
            }
        )

        # Add properties to the class
        for prop in properties:
            prop_name = prop["name"]
            prop_type = prop["type"]
            
            # Map Godot types to Blender property types
            if prop_type == "Vector3":
                new_class.__annotations__[prop_name] = bpy.props.FloatVectorProperty(
                    name=prop_name,
                    size=3
                )
            elif prop_type == "float":
                new_class.__annotations__[prop_name] = bpy.props.FloatProperty(
                    name=prop_name
                )
            elif prop_type == "int":
                new_class.__annotations__[prop_name] = bpy.props.IntProperty(
                    name=prop_name
                )
            elif prop_type == "bool":
                new_class.__annotations__[prop_name] = bpy.props.BoolProperty(
                    name=prop_name
                )
            elif prop_type == "String":
                new_class.__annotations__[prop_name] = bpy.props.StringProperty(
                    name=prop_name
                )

        return new_class

    def execute(self, context):
        try:
            # Load the game profile
            tools = context.window_manager.bless_tools
            with open(tools.profile_filepath, 'r') as f:
                profile_data = json.load(f)

            # Create dynamic classes for each class in the profile
            for class_name, class_data in profile_data["classes"].items():
                if class_data["properties"]:
                    # Create the dynamic class
                    dynamic_class = self.create_dynamic_class(class_name, class_data["properties"])
                    
                    # Register the class
                    bpy.utils.register_class(dynamic_class)
                    
                    # Add a property group to Object
                    setattr(bpy.types.Object, f"bless_{class_name.lower()}_props", 
                           PointerProperty(type=dynamic_class))

            # Add class selection enum to Object
            bpy.types.Object.bless_class = EnumProperty(
                name="Godot Class",
                description="Select Godot class for this object",
                items=get_profile_classes
            )

            self.report({'INFO'}, "Dynamic classes created successfully")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create dynamic classes: {str(e)}")
            return {'CANCELLED'}

class BlessLoadGameProfile(bpy.types.Operator):
    """Load Game Profile"""
    bl_idname = "object.load_game_profile"
    bl_label = "Load Game Profile"
    
    def execute(self, context):
        # Create dynamic classes when profile is loaded
        bpy.ops.object.create_dynamic_class()
        return {'FINISHED'}
