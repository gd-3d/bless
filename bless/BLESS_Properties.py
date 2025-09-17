import bpy


class BLESS_PG_SessionProperties(bpy.types.PropertyGroup):
    b_show_tool_box: bpy.props.BoolProperty()  # type:ignore

    b_show_object_data: bpy.props.BoolProperty()  # type:ignore
    b_show_collision_settings: bpy.props.BoolProperty()  # type:ignore


class BLESS_PG_ObjectCollisionSettings(bpy.types.PropertyGroup):
    collision_types: bpy.props.EnumProperty(
        name="Collision Type",
        description="Static level geometry.",
        default="trimesh",
        items=[
            ("trimesh", "Trimesh", "", 1),
            ("convex", "Convex", "", 1 << 1),
            ("custom", "Custom", "", 1 << 2),
            ("none", "None", "", 1 << 3),
        ])  # type: ignore

    layers = [(f"LAYER_{n}", f"{n}", "") for n in range(32)]
    collision_layers: bpy.props.EnumProperty(name="Collision Layers", options={"ENUM_FLAG"}, items=layers)  # type:ignore

    mask_layers = [(f"LAYER_{n}", f"{n}", "") for n in range(32)]
    collision_mask_layers: bpy.props.EnumProperty(name="Collision Mask Layers", options={"ENUM_FLAG"}, items=mask_layers)  # type:ignore


# Default collision type for new objects.
class BLESS_PG_DefaultCollisionType(bpy.types.PropertyGroup):
    collision_types: bpy.props.EnumProperty(
        name="Collision Type",
        description="Static level geometry.",
        default="trimesh",
        items=[
            ("trimesh", "Trimesh", "", 1),
            ("convex", "Convex", "", 1 << 1),
            ("custom", "Custom", "", 1 << 2),
            ("none", "None", "", 1 << 3),
        ])  # type: ignore


# class BlessTools(bpy.types.PropertyGroup):
#     lock_camera: bpy.props.BoolProperty(
#         default=False,
#         update=update_camera_lock
#     )  # type: ignore
#     profile_filepath: bpy.props.StringProperty(
#         name="Game Profile Path",
#         description="Path to the game profile configuration",
#         default="",
#         subtype='FILE_PATH'
#     )  # type: ignore
#     origin_type: bpy.props.EnumProperty(
#         name="Origin Type",
#         description="Origin type",
#         default="BOUNDS",
#         items=[("BOUNDS", "Bounds", "", 1),
#                ("BOTTOM", "Bottom", "", 2),
#                ("CENTER", "Center", "", 3),
#                ("TOP", "Top", "", 4)]
#     )  # type: ignore
#     trimesh_color: bpy.props.FloatVectorProperty(
#         name="Trimesh Color",
#         subtype='COLOR',
#         default=(0.1, 0.8, 0.1, 1),  # green
#         min=0.0, max=1.0,
#         size=4
#     )  # type: ignore
#     convex_color: bpy.props.FloatVectorProperty(
#         name="Convex Color",
#         subtype='COLOR',
#         default=(0.1, 0.1, 0.8, 1),  # blue
#         min=0.0, max=1.0,
#         size=4
#     )  # type: ignore
#     filter_glob: bpy.props.StringProperty(
#         default="*.json",  # Change this to match your profile file type
#         options={'HIDDEN'},
#         maxlen=255,
#     )  # type: ignore


# class BlessClassProperties(bpy.types.PropertyGroup):
#     """Base class for dynamic properties"""
#     pass
