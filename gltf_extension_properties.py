import bpy


# Define properties for OMI_physics_body
class OMI_Physics_Body(bpy.types.PropertyGroup):
    is_motion: bpy.props.BoolProperty(default=False) #type: ignore
    is_trigger: bpy.props.BoolProperty(default=False) #type: ignore
    is_collision: bpy.props.BoolProperty(default=False) #type: ignore

    motion_types: bpy.props.EnumProperty(
        name="Body Types",
        description="enumerator",
        items=[
            ("static", "Static", ""),
            ("dynamic", "Dynamic", ""),
            ("kinematic", "Kinematic", "")
        ],
        default="static"
    ) #type: ignore

    mass: bpy.props.IntProperty(default=1) #type: ignore
    linear_velocity: bpy.props.FloatVectorProperty(default=[0.0, 0.0, 0.0]) #type: ignore
    angular_velocity: bpy.props.FloatVectorProperty(default=[0.0, 0.0, 0.0]) #type: ignore
    center_of_mass: bpy.props.FloatVectorProperty(default=[0.0, 0.0, 0.0]) #type: ignore
    shape_index: bpy.props.IntProperty(default=-1) #type: ignore



# Define properties for OMI_physics_shape
class OMI_Physics_Shape(bpy.types.PropertyGroup):
    is_collision: bpy.props.BoolProperty(default=False) #type: ignore
    index: bpy.props.IntProperty(default=0) #type: ignore

    shape_types: bpy.props.EnumProperty(
        name="Collider Types",
        description="enumerator",
        items=[
            ("box", "Box", ""),
            ("sphere", "Sphere", ""),
            ("capsule", "Capsule", ""),
            ("cylinder", "Cylinder", ""),
            ("convex", "Convex", ""),
            ("trimesh", "Trimesh", "")
        ],
        default="convex"
    ) #type: ignore

    size: bpy.props.FloatVectorProperty(default=[1.0, 1.0, 1.0]) #type: ignore
    radius: bpy.props.FloatProperty(default=0.5) #type: ignore
    height: bpy.props.FloatProperty(default=2.0) #type: ignore
    mesh: bpy.props.IntProperty(default=-1) #type: ignore
