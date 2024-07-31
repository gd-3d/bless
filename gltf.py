

import bpy



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
        
        extension_name = "OMI_physics_shape"
        shape_array = []

        for obj in bpy.context.scene.objects:
            try:
                shape_data = obj[extension_name]
            except KeyError:
                continue
            else:
                shape_array.append(shape_data)

        gltf_plan.extensions[extension_name] = self.Extension(
            name=extension_name,
            extension={"shapes": shape_array},
            required=False
        )


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

# TODO expand...

class OMI_physics_shape(bpy.types.PropertyGroup):

    # possibly needed for internal for gd3d
    is_collision: bpy.props.BoolProperty(default=False)  # type: ignore

    # 
    index: bpy.props.IntProperty(default=0, description="index of the physics shape") # type: ignore

    shape_types: bpy.props.EnumProperty(
        name="",
        description="collider shape types",
        default="convex",
        items=[
            ("box", "Box", "", 1),
            ("sphere", "Sphere", "", 1<<1),
            ("capsule", "Capsule", "", 1<<2),
            ("cylinder", "Cylinder", "", 1<<3),
            ("convex", "Convex", "", 1<<4),
            ("trimesh", "Trimesh", "", 1<<5)
            ])  # type: ignore
    
    
    size: bpy.props.FloatVectorProperty(subtype="XYZ_LENGTH", description="size of the shape in meters", default=[1.0, 1.0, 1.0]) # type: ignore
    radius: bpy.props.FloatProperty(subtype="DISTANCE", description="radius of the shape in meters", default=0.5) # type: ignore 
    height: bpy.props.FloatProperty(subtype="DISTANCE", description="height of the shape in meters", default=2.0) # type: ignore
    
    # The index of the glTF mesh in the document to use as a mesh shape.
    mesh: bpy.props.IntProperty(default=-1) # type: ignore
    


## https://github.com/omigroup/gltf-extensions/tree/main/extensions/2.0/OMI_physics_body

class OMI_physics_body(bpy.types.PropertyGroup):
    shape_index: bpy.props.IntProperty(default=-1) # type: ignore

    # https://github.com/omigroup/gltf-extensions/blob/main/extensions/2.0/OMI_physics_body/README.motion.md
    is_motion: bpy.props.BoolProperty(default=False)  # type: ignore

    # https://github.com/omigroup/gltf-extensions/blob/main/extensions/2.0/OMI_physics_body/README.trigger.md
    is_trigger: bpy.props.BoolProperty(default=False)  # type: ignore
    
    #https://github.com/omigroup/gltf-extensions/blob/main/extensions/2.0/OMI_physics_body/README.collider.md
    is_collision: bpy.props.BoolProperty(default=False)  # type: ignore


    motion_types: bpy.props.EnumProperty(
        name="Body Types",
        description="physics body types",
        default="static",
        items=[
            ("static", "Static", "", 1),
            ("dynamic", "Dynamic", "", 1<<1),
            ("kinematic", "Kinematic", "", 1<<2)
        ])  # type: ignore

    mass: bpy.props.FloatProperty(default=1.0)  # type: ignore

    linear_velocity: bpy.props.FloatVectorProperty(subtype="VELOCITY", default=[0.0, 0.0, 0.0]) # type: ignore 
    angular_velocity: bpy.props.FloatVectorProperty(subtype="VELOCITY", default=[0.0, 0.0, 0.0]) # type: ignore 
    center_of_mass: bpy.props.FloatVectorProperty(default=[0.0, 0.0, 0.0]) # type: ignore



## NOTE temporary operator.

class ApplyProps(bpy.types.Operator):
    """Apply Props"""
    bl_idname = "object.gd3d_apply_props"
    bl_label = "Apply Props"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        objects = context.selected_objects
        scene = context.scene
        body = scene.body_properties
        shape = scene.shape_properties
        

        for obj in objects:
            if body.is_motion:
                body_data = build_body_dictionary(body)
                obj["OMI_physics_body"] = body_data
        for obj in objects:

            shape_data = build_shape_dictionary(body, shape)
            obj["OMI_physics_shape"] = shape_data

        return {'FINISHED'}
    
# TODO stub
def build_body_dictionary(body):
    body_data = {}
    if body.is_motion:
        motion_data = {"type": body.motion_types}
        shape_type = {"shape": body.shape_index}
       
        body_data["motion"] = motion_data
        body_data["collider"] = shape_type
    return body_data


# TODO stub
def build_shape_dictionary(body, shape):
    subdata = {}

    if shape.shape_types == "box":
        subdata["size"] = shape.size
    elif shape.shape_types in ["sphere", "capsule", "cylinder"]:
        subdata["radius"] = shape.radius
    
    if shape.shape_types in ["capsule", "cylinder"]:
        subdata["height"] = shape.height
    
    if shape.shape_types in ["trimesh", "convex"]:
        subdata["mesh"] = shape.mesh

    shape_data = {"type": shape.shape_types}

    shape_data[shape.shape_types] = subdata
    return shape_data



class PhysicsPanel(bpy.types.Panel):
    bl_label = "Physics Panel"
    bl_idname = "VIEW3D_PT_object_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Collision'

    def draw(self, context):
        layout = self.layout.row()
        body_properties = context.scene.body_properties
        shape_properties = context.scene.shape_properties

        layout.separator(factor=2.0)

        indented_layout = layout.column()
        if (context.object is not None):
            indented_layout.row().operator("object.gd3d_apply_props", text="apply")

            indented_layout.label(text="Shape Properties:")
            
            
            prop_indented_layout = indented_layout.row()
            prop_indented_layout.separator(factor=2.0)

            prop_column = prop_indented_layout.column()
            row = prop_column.row()
            row.prop(shape_properties, "is_collision", text="collision object")
            row.prop(shape_properties, "index")

            prop_column.row().prop(shape_properties, "shape_types", text="")

            prop_column.row().prop(shape_properties, "size")

            row = prop_column.row()
            row.prop(shape_properties, "radius")
            row.prop(shape_properties, "height")

            prop_column.row().prop(shape_properties, "mesh")

            row = prop_column.row()
            row.prop(body_properties, "is_motion", text="motion object")
            row.prop(body_properties, "is_trigger", text="trigger object")

            prop_column.row().prop(body_properties, "motion_types")

            prop_column.row().prop(body_properties, "mass")

            prop_column.row().prop(body_properties, "linear_velocity", text="linear velocity")

            prop_column.row().prop(body_properties, "angular_velocity", text="angular velocity")
  
            prop_column.row().prop(body_properties, "center_of_mass", text="center of mass")

            prop_column.row().prop(body_properties, "shape_index", text="shape index")
