## https://github.com/omigroup/gltf-extensions/tree/main/extensions/2.0/OMI_physics_body

import bpy

class OMI_Physics_Shape(bpy.types.PropertyGroup):

    is_collision: bpy.props.BoolProperty(default=False)  # type: ignore

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


class OMI_Physics_Body(bpy.types.PropertyGroup):

    is_motion: bpy.props.BoolProperty(default=False)  # type: ignore
    is_trigger: bpy.props.BoolProperty(default=False)  # type: ignore
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
    shape_index: bpy.props.IntProperty(default=-1) # type: ignore




