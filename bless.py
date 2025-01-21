import json
import os

import bpy


class BLESS_ObjectCollisionSettings(bpy.types.PropertyGroup):
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

    def DYNAMIC_ENUM_bless_collision_layers(self, context) -> list:
        return [(f"LAYER_{n}", f"Layer {n}", "") for n in range(32)]
    collision_layers = bpy.props.EnumProperty(name="Collision Layers", options={"ENUM_FLAG"}, items=DYNAMIC_ENUM_bless_collision_layers)  # type:ignore

    def DYNAMIC_ENUM_bless_collision_mask_layers(self, context) -> list:
        return [(f"LAYER_{n}", f"Layer {n}", "") for n in range(32)]
    collision_mask_layers: bpy.props.EnumProperty(name="Collision Mask Layers", options={"ENUM_FLAG"}, items=DYNAMIC_ENUM_bless_collision_mask_layers)  # type:ignore


# https://github.com/omigroup/gltf-extensions/tree/main/extensions/2.0/OMI_physics_shape


class OMIPhysicsShape(bpy.types.PropertyGroup):
    # possibly needed for internal for gd3d
    is_collision: bpy.props.BoolProperty(default=False)  # type: ignore
    index: bpy.props.IntProperty(default=0, description="index of the physics shape")  # type: ignore
    shape_types: bpy.props.EnumProperty(
        name="",
        description="collider shape types",
        default="convex",
        items=[
            ("box", "Box", "", 1),
            ("sphere", "Sphere", "", 1 << 1),
            ("capsule", "Capsule", "", 1 << 2),
            ("cylinder", "Cylinder", "", 1 << 3),
            ("convex", "Convex", "", 1 << 4),
            ("trimesh", "Trimesh", "", 1 << 5)
        ])  # type: ignore
    size: bpy.props.FloatVectorProperty(subtype="XYZ_LENGTH", description="size of the shape in meters", default=[1.0, 1.0, 1.0])  # type: ignore
    radius: bpy.props.FloatProperty(subtype="DISTANCE", description="radius of the shape in meters", default=0.5)  # type: ignore
    height: bpy.props.FloatProperty(subtype="DISTANCE", description="height of the shape in meters", default=2.0)  # type: ignore
    # The index of the glTF mesh in the document to use as a mesh shape.
    mesh: bpy.props.IntProperty(default=-1)  # type: ignore

# https://github.com/omigroup/gltf-extensions/tree/main/extensions/2.0/OMI_physics_body


class OMIPhysicsBody(bpy.types.PropertyGroup):
    shape_index: bpy.props.IntProperty(default=-1)  # type: ignore
    # https://github.com/omigroup/gltf-extensions/blob/main/extensions/2.0/OMI_physics_body/README.motion.md
    is_motion: bpy.props.BoolProperty(default=False)  # type: ignore
    # https://github.com/omigroup/gltf-extensions/blob/main/extensions/2.0/OMI_physics_body/README.trigger.md
    is_trigger: bpy.props.BoolProperty(default=False)  # type: ignore
    # https://github.com/omigroup/gltf-extensions/blob/main/extensions/2.0/OMI_physics_body/README.collider.md
    is_collision: bpy.props.BoolProperty(default=False)  # type: ignore

    motion_types: bpy.props.EnumProperty(
        name="Body Types",
        description="physics body types",
        default="static",
        items=[
            ("static", "Static", "", 1),
            ("dynamic", "Dynamic", "", 1 << 1),
            ("kinematic", "Kinematic", "", 1 << 2)
        ])  # type: ignore
    mass: bpy.props.FloatProperty(default=1.0)  # type: ignore
    linear_velocity: bpy.props.FloatVectorProperty(subtype="VELOCITY", default=[0.0, 0.0, 0.0])  # type: ignore
    angular_velocity: bpy.props.FloatVectorProperty(subtype="VELOCITY", default=[0.0, 0.0, 0.0])  # type: ignore
    center_of_mass: bpy.props.FloatVectorProperty(default=[0.0, 0.0, 0.0])  # type: ignore


# Default collision type for new objects.
class BlessDefaultCollisionType(bpy.types.PropertyGroup):
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


# TODO rework this as an operator to call
def update_camera_lock(self, context):
    bpy.ops.view3d.bless_camera_lock()


class BlessTools(bpy.types.PropertyGroup):
    lock_camera: bpy.props.BoolProperty(
        default=False,
        update=update_camera_lock
    )  # type: ignore
    profile_filepath: bpy.props.StringProperty(
        name="Game Profile Path",
        description="Path to the game profile configuration",
        default="",
        subtype='FILE_PATH'
    )  # type: ignore
    origin_type: bpy.props.EnumProperty(
        name="Origin Type",
        description="Origin type",
        default="BOUNDS",
        items=[("BOUNDS", "Bounds", "", 1),
               ("BOTTOM", "Bottom", "", 2),
               ("CENTER", "Center", "", 3),
               ("TOP", "Top", "", 4)]
    )  # type: ignore
    trimesh_color: bpy.props.FloatVectorProperty(
        name="Trimesh Color",
        subtype='COLOR',
        default=(0.1, 0.8, 0.1, 1),  # green
        min=0.0, max=1.0,
        size=4
    )  # type: ignore
    convex_color: bpy.props.FloatVectorProperty(
        name="Convex Color",
        subtype='COLOR',
        default=(0.1, 0.1, 0.8, 1),  # blue
        min=0.0, max=1.0,
        size=4
    )  # type: ignore
    filter_glob: bpy.props.StringProperty(
        default="*.json",  # Change this to match your profile file type
        options={'HIDDEN'},
        maxlen=255,
    )  # type: ignore


class BlessClassProperties(bpy.types.PropertyGroup):
    """Base class for dynamic properties"""
    pass


def get_profile_classes(self, context):
    """Get classes from game profile for enum"""
    # Always start with None as the first option
    items = [("NONE", "None", "No Godot class assigned")]
    tools = context.window_manager.bless_tools

    try:
        if tools.profile_filepath:
            with open(tools.profile_filepath, 'r') as f:
                profile_data = json.load(f)
                for class_name in profile_data.get("classes", {}):
                    items.append((class_name.upper(), class_name, f"Godot {class_name} class"))
    except Exception as e:
        print(f"Error loading profile classes: {e}")

    return items


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


standard_texture_channels = {
    # Common PBR material texture types
    "albedo": ["albedo", "basecolor", "basecolour", "base", "color", "colour", "diffuse", "diff", "c", "d", "col", "alb", "dif"],
    "normal": ["normal", "normalgl", "local", "norm", "nor", "nor_gl", "nor_dx", "n"],  # NOTE: "normaldx" removed for now.
    "roughness": ["roughness", "rough", "rgh", "r"],
    "metallic": ["metallic", "metalness", "met", "m"],
    "ao": ["ao", "ambientocclusion", "ambient", "occlusion", "a", "o"],
    "emission": ["emission", "emissive", "glow", "luma", "g"],
    "height": ["height", "displacement", "disp", "h", "z"],

    # Combined maps
    "orm": ["orm", "arm"],

    # Less common maps
    "rim": ["rim"],
    "clearcoat": ["clearcoat"],
    "anisotropy": ["anisotropy", "aniso", "flowmap", "flow"],
    "subsurface": ["subsurface", "subsurf", "scattering", "scatter", "sss"],
    "transmission": ["transmittance", "transmission", "transmissive"],
    "backlight": ["backlighting", "backlight"],
    "refraction": ["refraction", "refract"],
    "detail": ["detail"]
}


def create_materials_from_textures(texture_paths, standard_texture_channels):
    # Group textures by their common prefix
    material_groups = {}
    for texture_path in texture_paths:
        # Extract the common prefix
        prefix = "_".join(os.path.basename(texture_path).split("_")[:-1])
        if prefix not in material_groups:
            material_groups[prefix] = []
        material_groups[prefix].append(texture_path)

    # Create materials for each group
    for prefix, textures in material_groups.items():
        # Create a new material
        material = bpy.data.materials.new(name=prefix)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Add Principled BSDF and Material Output nodes
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (400, 0)
        bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_node.location = (0, 0)
        links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

        BASE_X = -400
        BASE_Y = 0
        Y_OFFSET = -300  # Space between nodes vertically
        X_OFFSET = 350  # Space between nodes horizontally
        NODE_POSITIONS = {}  # Keep track of positions for each channel type

        for texture_path in textures:
            # Determine the channel type
            channel = os.path.basename(texture_path).split("_")[-1].split(".")[0].lower()
            for channel_type, aliases in standard_texture_channels.items():
                if channel in aliases:
                    if channel_type not in {"albedo", "metallic", "roughness", "normal", "emission"}:
                        # Skip unsupported channel types
                        continue

                    # Add image texture node
                    img_node = nodes.new(type='ShaderNodeTexImage')
                    img_node.name = channel_type
                    # Set location based on channel type
                    if channel_type not in NODE_POSITIONS:
                        NODE_POSITIONS[channel_type] = BASE_Y
                        BASE_Y += Y_OFFSET
                    img_node.location = (BASE_X, NODE_POSITIONS[channel_type])

                    img_node.image = bpy.data.images.load(texture_path)

                    # Horizontal offset for additional nodes
                    current_x = BASE_X + X_OFFSET

                    # Connect to the appropriate input on the BSDF node
                    if channel_type == "albedo":
                        links.new(img_node.outputs["Color"], bsdf_node.inputs["Base Color"])

                    elif channel_type == "metallic":
                        links.new(img_node.outputs["Color"], bsdf_node.inputs["Metallic"])

                    elif channel_type == "roughness":
                        links.new(img_node.outputs["Color"], bsdf_node.inputs["Roughness"])

                    elif channel_type == "normal":
                        normal_map_node = nodes.new(type='ShaderNodeNormalMap')
                        normal_map_node.location = (current_x, NODE_POSITIONS[channel_type])
                        links.new(img_node.outputs["Color"], normal_map_node.inputs["Color"])
                        links.new(normal_map_node.outputs["Normal"], bsdf_node.inputs["Normal"])

                    elif channel_type == "emission":
                        links.new(img_node.outputs["Color"], bsdf_node.inputs["Emission"])

                    break


class BlessLoadGameProfile(bpy.types.Operator):
    """Load Game Profile"""
    bl_idname = "object.load_game_profile"
    bl_label = "Load Game Profile"

    def execute(self, context):
        # Create dynamic classes when profile is loaded
        bpy.ops.object.create_dynamic_class()
        return {'FINISHED'}


class BlessPanel(bpy.types.Panel):
    bl_label = "Bless"
    bl_idname = "VIEW3D_PT_object_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'

    # Main sections
    bpy.types.WindowManager.bless_show_grid = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_view = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_collision = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_tools = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_settings = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_export = bpy.props.BoolProperty(default=False)

    # Grid subsections
    bpy.types.WindowManager.bless_show_grid_snap = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_grid_grid = bpy.props.BoolProperty(default=False)

    # View subsections
    bpy.types.WindowManager.bless_show_view_camera = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_view_grid = bpy.props.BoolProperty(default=False)

    # Collision subsections
    bpy.types.WindowManager.bless_show_collision_layers = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_collision_mask = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_collision_shapes = bpy.props.BoolProperty(default=False)

    # Tools subsections
    bpy.types.WindowManager.bless_show_tools_profile = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_tools_origin = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_tools_transform = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_tools_greybox = bpy.props.BoolProperty(default=False)

    # Settings subsections
    bpy.types.WindowManager.bless_show_settings_colors = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_settings_paths = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_settings_defaults = bpy.props.BoolProperty(default=False)

    # Export subsections
    bpy.types.WindowManager.bless_show_export_gltf = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_export_collisions = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_export_settings = bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        tools = wm.bless_tools

        # VIEW
        box = layout.box()
        row = box.row()
        row.prop(wm, "bless_show_view", text="View", icon='TRIA_DOWN' if wm.bless_show_view else 'TRIA_RIGHT', emboss=False)
        if wm.bless_show_view:
            sub_box = layout.box()
            row = sub_box.row()
            row.prop(wm, "bless_show_view_camera", text="Camera", icon='TRIA_DOWN' if wm.bless_show_view_camera else 'TRIA_RIGHT', emboss=False)
            if wm.bless_show_view_camera:
                row = sub_box.row()
                row.prop(tools, "lock_camera", text="Lock Camera")

            sub_box = layout.box()
            row = sub_box.row()
            row.prop(wm, "bless_show_view_grid", text="Grid", icon='TRIA_DOWN' if wm.bless_show_view_grid else 'TRIA_RIGHT', emboss=False)
            if wm.bless_show_view_grid:
                # Grid options
                row = sub_box.row()
                row.prop(context.window_manager, "unit_size", text="Unit Size (m)")
                row.operator("map_editor.double_unit_size", text="", icon="MESH_GRID")
                row.operator("map_editor.halve_unit_size", text="", icon="SNAP_GRID")
                # Add grid options here
                pass

        # Early return if no object is selected
        if not context.object:
            layout.box().label(text="No object selected!", icon="INFO")
            return

        collision_settings = context.object.bless_object_collision_settings

        collision_types = collision_settings.collision_types

        # COLLISION
        box = layout.box()
        row = box.row()
        row.prop(wm, "bless_show_collision", text="Collision", icon='TRIA_DOWN' if wm.bless_show_collision else 'TRIA_RIGHT', emboss=False)
        if wm.bless_show_collision:
            row = box.row()
            row.prop(collision_settings, "collision_types", text="")
            # Only show Apply Collision button when multiple objects are selected
            if len(context.selected_objects) > 1:
                row.operator("object.gd3d_apply_collisions", text="Apply Collision", icon="CUBE")

            if collision_types != "none":
                # Collision Layers
                sub_box = box.box()
                row = sub_box.row()
                row.prop(wm, "bless_show_collision_layers", text="Collision Layers",
                         icon='TRIA_DOWN' if wm.bless_show_collision_layers else 'TRIA_RIGHT', emboss=False)
                if wm.bless_show_collision_layers:
                    self.draw_collision_layers(context, sub_box)

                # Collision Mask
                sub_box = box.box()
                row = sub_box.row()
                row.prop(wm, "bless_show_collision_mask", text="Collision Mask",
                         icon='TRIA_DOWN' if wm.bless_show_collision_mask else 'TRIA_RIGHT', emboss=False)
                if wm.bless_show_collision_mask:
                    self.draw_collision_mask(context, sub_box)

        # TOOLS
        box = layout.box()
        row = box.row()
        row.prop(wm, "bless_show_tools", text="Tools", icon='TRIA_DOWN' if wm.bless_show_tools else 'TRIA_RIGHT', emboss=False)
        if wm.bless_show_tools:
            # Greybox Tools
            sub_box = box.box()
            row = sub_box.row()
            row.prop(wm, "bless_show_tools_greybox", text="Greybox",
                     icon='TRIA_DOWN' if wm.bless_show_tools_greybox else 'TRIA_RIGHT', emboss=False)
            if wm.bless_show_tools_greybox:
                col = sub_box.column(align=True)
                col.operator("bless.greybox_draw", text="Draw", icon="BRUSH_DATA")
                col.operator("bless.greybox_transform", text="Transform", icon="ORIENTATION_GLOBAL")
                col.operator("bless.greybox_extrude", text="Extrude", icon="ORIENTATION_NORMAL")
                col.operator("bless.greybox_snap", text="Snap to Grid", icon="SNAP_GRID")

            # Profile
            sub_box = box.box()
            row = sub_box.row()
            row.prop(wm, "bless_show_tools_profile", text="Game Profile",
                     icon='TRIA_DOWN' if wm.bless_show_tools_profile else 'TRIA_RIGHT', emboss=False)
            if wm.bless_show_tools_profile:
                row = sub_box.row(align=True)
                row.prop(tools, "profile_filepath", text="")
                row.operator("object.load_game_profile", text="Load Profile", icon='IMPORT')

            # Origin
            sub_box = box.box()
            row = sub_box.row()
            row.prop(wm, "bless_show_tools_origin", text="Origin",
                     icon='TRIA_DOWN' if wm.bless_show_tools_origin else 'TRIA_RIGHT', emboss=False)
            if wm.bless_show_tools_origin:
                row = sub_box.row()
                row.prop(tools, "origin_type", text="Type")
                row.operator("object.autoorigin", text="Auto Origin", icon="MESH_DATA")

        # SETTINGS
        box = layout.box()
        row = box.row()
        row.prop(wm, "bless_show_settings", text="Settings", icon='TRIA_DOWN' if wm.bless_show_settings else 'TRIA_RIGHT', emboss=False)
        if wm.bless_show_settings:
            # Colors
            sub_box = box.box()
            row = sub_box.row()
            row.prop(wm, "bless_show_settings_colors", text="Colors",
                     icon='TRIA_DOWN' if wm.bless_show_settings_colors else 'TRIA_RIGHT', emboss=False)
            if wm.bless_show_settings_colors:
                sub_box.prop(tools, "trimesh_color", text="Trimesh")
                sub_box.prop(tools, "convex_color", text="Convex")

        # EXPORT
        box = layout.box()
        row = box.row()
        row.prop(wm, "bless_show_export", text="Export", icon='TRIA_DOWN' if wm.bless_show_export else 'TRIA_RIGHT', emboss=False)
        if wm.bless_show_export:
            # Add export options here
            pass

        # INFO BOX
        info_box = layout.box()
        info_box.label(text="Information", icon="INFO")

        # Object class information
        obj = context.active_object
        if obj and hasattr(obj, "godot_class"):
            info_box.prop(obj, "godot_class")
            if obj.godot_class != "NONE":
                sub_box = info_box.box()
                sub_box.label(text=f"{obj.godot_class} Properties")
                props = getattr(obj, f"godot_class_{obj.godot_class.lower()}_props", None)
                if props:
                    for prop in props.bl_rna.properties:
                        if not prop.is_hidden:
                            sub_box.prop(props, prop.identifier)

        # Collision information
        if collision_types:
            info_box.label(text=f"Selected object has {str(collision_types).upper()} collision.")

    def draw_collision_layers(self, context, parent_box):
        pass
    #     collision_settings = context.object.bless_object_collision_settings
    #     box = parent_box.box()
    #     box.label(text="Collision Layers")

    #     for row_idx in range(2):
    #         row = box.row()
    #         for block in range(4):
    #             col = row.column()
    #             sub_row = col.row(align=True)
    #             for btn in range(4):
    #                 idx = (row_idx * 16) + (block * 4) + btn
    #                 sub_row.prop(collision_settings, f"layer_{idx + 1}", text=str(idx + 1), toggle=True)

    def draw_collision_mask(self, context, parent_box):
        pass
    #     collision_mask = context.object.collision_mask
    #     box = parent_box.box()
    #     box.label(text="Collision Mask")

    #     for row_idx in range(2):
    #         row = box.row()
    #         for block in range(4):
    #             col = row.column()
    #             sub_row = col.row(align=True)
    #             for btn in range(4):
    #                 idx = (row_idx * 16) + (block * 4) + btn
    #                 sub_row.prop(collision_mask, f"layer_{idx + 1}", text=str(idx + 1), toggle=True)


class BlessApplyCollisions(bpy.types.Operator):
    """Apply Props"""
    bl_idname = "object.gd3d_apply_collisions"
    bl_label = "Apply Multiple Collisions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not isinstance(context.selected_objects, list):
            self.report({'ERROR'}, "No objects selected or selection is invalid.")
            return {'CANCELLED'}

        collision_type = context.object.collision_types.collision_types
        tools = context.window_manager.bless_tools

        for obj in context.selected_objects:
            # set attribute, not custom property
            obj.collision_types.collision_types = collision_type

            # Set the visual feedback
            obj.grid_type = 'SOLID'
            obj.show_wire = True  # Optional: show wireframe for better visibility
            if collision_type == "trimesh":
                obj.color = tools.trimesh_color
            elif collision_type == "convex":
                obj.color = tools.convex_color

        return {'FINISHED'}
