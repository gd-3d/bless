import json

import bpy

from bless.BLESS_Definitions import standard_texture_channels
from bless.utilities.BLESS_Material_Utils import create_materials_from_textures
from core.bless import BlessClassProperties


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
            prop_hint = prop.get("hint", "")

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
                # Check if this is an enum
                if prop_hint:
                    # Create enum items from hint
                    enum_items = []
                    for i, item in enumerate(prop_hint.split(",")):
                        enum_items.append((str(i), item.strip(), "", i))
                    new_class.__annotations__[prop_name] = bpy.props.EnumProperty(
                        name=prop_name,
                        items=enum_items
                    )
                else:
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
            elif prop_type == "Object":
                # For object references that are inherited from Node3D
                if prop_hint:
                    new_class.__annotations__[prop_name] = bpy.props.PointerProperty(
                        name=prop_name,
                        type=bpy.types.Object,
                        description=f"Reference to a {prop_hint} object"
                    )
                else:
                    new_class.__annotations__[prop_name] = bpy.props.PointerProperty(
                        name=prop_name,
                        type=bpy.types.Object
                    )

        return new_class

    ###### READ GAME PROFILE ########
    #################################

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
                    setattr(bpy.types.Object, f"godot_class_{class_name.lower()}_props",
                            bpy.props.PointerProperty(type=dynamic_class))

            # Remove old godot_class if it exists
            if hasattr(bpy.types.Object, "godot_class"):
                delattr(bpy.types.Object, "godot_class")

            # Create items list with None as first option
            items = [("NONE", "None", "No Godot class assigned")]
            for class_name in profile_data["classes"].keys():
                items.append((class_name, class_name, f"Godot {class_name} class"))

            # Add class selection enum to Object with None as default
            bpy.types.Object.godot_class = bpy.props.EnumProperty(
                name="Godot Class",
                description="Select Godot class for this object",
                items=items,
                default="NONE"
            )

            all_textures = []
            # read materials from the JSON profile
            for texture_path in profile_data["textures"]:
                all_textures.append(texture_path)

            create_materials_from_textures(all_textures, standard_texture_channels)

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
