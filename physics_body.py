import bpy

## this script handles all collision data

## props

class CollisionPanel(bpy.types.Panel):
    bl_label = "Collision Panel"
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

class MotionBodyProperties(bpy.types.PropertyGroup):
    is_motion: bpy.props.BoolProperty(default=False)  # type: ignore
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

class CollisionBodyProperties(bpy.types.PropertyGroup):
    is_collision: bpy.props.BoolProperty(default=False)  # type: ignore
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
    is_trigger: bpy.props.BoolProperty(default=False)  # type: ignore


## ops

## NOTE: I was thinking that this operator could be applied 
## when any collision property is changed:


class ApplyProps(bpy.types.Operator):
    """Apply Props"""
    bl_idname = "object.gd3d_apply_props"
    bl_label = "Apply Props"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        scene = context.scene
        motion = scene.motion_properties
        collision = scene.collision_properties


        ## just an idea. but I think I got something wrong here.

        for obj in context.selected_objects:
            obj["OMI_physics_body"] = {
                "motion": {
                    "type": motion.motion_types
                },
                "collider": {
                    "shape": collision.shape_types
                },
                "trigger": collision.is_trigger
            }

        return {'FINISHED'}
        ##


## io 

class glTF2ExportUserExtension:
    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type: ignore
        self.Extension = Extension

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}

        n = "OMI_physics_body"
        if n in blender_object:
            gltf2_object.extensions[n] = self.Extension(
                name=n,
                extension=blender_object[n],
                required=False
            )