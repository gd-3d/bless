import bpy

## this script handles all gltf extension data applied to objects.

## props

class ObjectPanel(bpy.types.Panel):
    bl_label = "Object Panel"
    bl_idname = "VIEW3D_PT_object_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'gd-3d'

    def draw(self, context):
        layout = self.layout
        motion = context.scene.motion_properties
        collision = context.scene.collision_properties
        obj = context.object

        if obj is None:
            layout.label(text="No object selected.")
        else:

            row = layout.row()
            row.operator("object.gd3d_apply_props", text="apply")
            row = layout.row()
            row.prop(motion, "is_motion")
            row = layout.row()
            row.prop(motion, "motion_types")
            row = layout.row()
            row.prop(collision, "shape_types")
            row = layout.row()
            row.prop(collision, "is_trigger")



## https://github.com/omigroup/gltf-extensions/tree/main/extensions/2.0/OMI_physics_body

class OMI_Physics_Body(bpy.types.PropertyGroup):

    ## possibly needed as internal properties to show/hide panels, not sure yet
    is_motion: bpy.props.BoolProperty(default=False)  # type: ignore
    is_trigger: bpy.props.BoolProperty(default=False)  # type: ignore
    is_collision: bpy.props.BoolProperty(default=False)  # type: ignore

    # TODO add comments here like with shape class.

    motion_types: bpy.props.EnumProperty(
        name="Body Types",
        description="enumerator",
        items=[
            ("static", "Static", ""),
            ("dynamic", "Dynamic", ""),
            ("kinematic", "Kinematic", "")
        ],
        default="static"
    )  # type: ignore


    
    mass: bpy.props.IntProperty(default=1)  # type: ignore

    linear_velocity: bpy.props.FloatVectorProperty(default=[0.0, 0.0, 0.0]) # type: ignore 
    angular_velocity: bpy.props.FloatVectorProperty(default=[0.0, 0.0, 0.0]) # type: ignore 
    center_of_mass: bpy.props.FloatVectorProperty(default=[0.0, 0.0, 0.0]) # type: ignore
    shape_index: bpy.props.IntProperty(default=-1) # type: ignore




## https://github.com/omigroup/gltf-extensions/tree/main/extensions/2.0/OMI_physics_shape

class OMI_Physics_Shape(bpy.types.PropertyGroup):
    is_collision: bpy.props.BoolProperty(default=False)  # type: ignore
    
    # the index of the shape.
    index: bpy.props.IntProperty(default=0) # type: ignore
    
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
    )  # type: ignore

    # The size of the box shape in meters.
    size: bpy.props.FloatVectorProperty(default=[1.0, 1.0, 1.0]) # type: ignore

    # The radius of the shape in meters. (Sphere, capsule, cylinder)
    radius: bpy.props.FloatProperty(default=0.5) # type: ignore 
    
    # The height of the shape in meters. (Capsule, cylinder)
    height: bpy.props.FloatProperty(default=2.0) # type: ignore
    
    # The index of the glTF mesh in the document to use as a mesh shape.
    mesh: bpy.props.IntProperty(default=-1) # type: ignore





## ops

## this is basically a dev button for applying the data manually, 
## in production this will be automatic (in most cases..)

class ApplyProps(bpy.types.Operator):
    """Apply Props"""
    bl_idname = "object.gd3d_apply_props"
    bl_label = "Apply Props"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        body = scene.body_properties
        shape = scene.shape_properties

        
        # declare shapes to be used by bodies

        for obj in context.selected_objects:
            obj["OMI_physics_shape"] = {
                "type" : shape.shape_types



            }


        for obj in context.selected_objects:
            obj["OMI_physics_body"] = {
                "motion": {
                    "type": body.motion_types
                },
                "collider": {
                    "shape": body.shape_index # shape INDEX goes here.
                },
                "trigger": body.is_trigger
            }

        return {'FINISHED'}
        ##


## io 

extension_list = [
    "OMI_physics_body",
    "OMI_physics_shape"
    # possible to add more here.
]


class glTF2ExportUserExtension:
    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type: ignore
        self.Extension = Extension

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}


        for extension in extension_list:
            
            json_include = f'"extensionsUsed":[{extension_list}]' # TODO. something better 

            if extension in blender_object:
                gltf2_object.extensions[n] = self.Extension(
                    name=n,
                    extension=blender_object[n],
                    required=False
                )