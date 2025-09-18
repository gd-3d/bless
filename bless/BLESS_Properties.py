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

    # region collision mask layers
    layers_1_8 = [(f"LAYER_{n}", f"{n+1}", "") for n in range(0, 8)]
    collision_layers_1_8: bpy.props.EnumProperty(name="collision layers 1-8", options={"ENUM_FLAG"}, items=layers_1_8)  # type:ignore

    layers_9_16 = [(f"LAYER_{n}", f"{n+1}", "") for n in range(8, 16)]
    collision_layers_9_16: bpy.props.EnumProperty(name="collision layers 9-16", options={"ENUM_FLAG"}, items=layers_9_16)  # type:ignore

    layers_17_24 = [(f"LAYER_{n}", f"{n+1}", "") for n in range(16, 24)]
    collision_layers_17_24: bpy.props.EnumProperty(name="collision layers 17-24", options={"ENUM_FLAG"}, items=layers_17_24)  # type:ignore

    layers_25_32 = [(f"LAYER_{n}", f"{n+1}", "") for n in range(24, 32)]
    collision_layers_25_32: bpy.props.EnumProperty(name="collision layers 25-32", options={"ENUM_FLAG"}, items=layers_25_32)  # type:ignore
    # endregion

    # region collision mask layers
    mask_layers_1_8 = [(f"LAYER_{n}", f"{n+1}", "") for n in range(0, 8)]
    collision_mask_layers_1_8: bpy.props.EnumProperty(name="collision layers 1-8", options={"ENUM_FLAG"}, items=mask_layers_1_8)  # type:ignore

    mask_layers_9_16 = [(f"LAYER_{n}", f"{n+1}", "") for n in range(8, 16)]
    collision_mask_layers_9_16: bpy.props.EnumProperty(name="collision layers 9-16", options={"ENUM_FLAG"}, items=mask_layers_9_16)  # type:ignore

    mask_layers_17_24 = [(f"LAYER_{n}", f"{n+1}", "") for n in range(16, 24)]
    collision_mask_layers_17_24: bpy.props.EnumProperty(name="collision layers 17-24", options={"ENUM_FLAG"}, items=mask_layers_17_24)  # type:ignore

    mask_layers_25_32 = [(f"LAYER_{n}", f"{n+1}", "") for n in range(24, 32)]
    collision_mask_layers_25_32: bpy.props.EnumProperty(name="collision layers 25-32", options={"ENUM_FLAG"}, items=mask_layers_25_32)  # type:ignore
    # endregion

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
