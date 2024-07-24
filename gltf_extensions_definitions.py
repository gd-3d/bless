

import bpy

class OMI_Physics_Shape(bpy.types.PropertyGroup):

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

class OMI_Physics_Body(bpy.types.PropertyGroup):
    
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




#### dev zone

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
    

def build_body_dictionary(body):
    body_data = {}

    if body.is_motion:


        motion_data = {"type": body.motion_types}
        shape_type = {"shape": body.shape_index}

        body_data["motion"] = motion_data
        body_data["collider"] = shape_type

    # if rigid
    # if body.motion_types is "1":
    #     body_data = {
    #         "mass": body.mass,
    #         "linearVelocity": body.linear_velocity,
    #         "angularVelocity": body.angular_velocity,
    #         "centerOfMass": body.center_of_mass,
    #     }
    
    return body_data


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