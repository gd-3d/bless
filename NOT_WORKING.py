import bpy

# Define the panel to display properties in the UI
class ObjectPanel(bpy.types.Panel):
    bl_label = "Object Panel"
    bl_idname = "VIEW3D_PT_object_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'gd-3d'

    def draw(self, context):
        layout = self.layout
        body = context.scene.body_properties
        shape = context.scene.shape_properties
        obj = context.object

        if obj is None:
            layout.label(text="No object selected.")
        else:
            row = layout.row()
            row.operator("object.gd3d_apply_props", text="apply")
            
            layout.label(text="Body Properties")
            row = layout.row()
            row.prop(body, "is_motion")
            row = layout.row()
            row.prop(body, "motion_types")
            row = layout.row()
            row.prop(body, "mass")
            row = layout.row()
            row.prop(body, "linear_velocity")
            row = layout.row()
            row.prop(body, "angular_velocity")
            row = layout.row()
            row.prop(body, "center_of_mass")
            row = layout.row()
            row.prop(body, "is_trigger")
            row = layout.row()
            row.prop(body, "shape_index")

            layout.separator()
            
            layout.label(text="Shape Properties")
            row = layout.row()
            row.prop(shape, "is_collision")
            row = layout.row()
            row.prop(shape, "index")
            row = layout.row()
            row.prop(shape, "shape_types")
            row = layout.row()
            row.prop(shape, "size")
            row = layout.row()
            row.prop(shape, "radius")
            row = layout.row()
            row.prop(shape, "height")
            row = layout.row()
            row.prop(shape, "mesh")

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

# Operator to apply properties to the object
class ApplyProps(bpy.types.Operator):
    """Apply Props"""
    bl_idname = "object.gd3d_apply_props"
    bl_label = "Apply Props"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        body = scene.body_properties
        shape = scene.shape_properties

        for obj in context.selected_objects:
            if body.is_motion or body.is_trigger:
                obj["OMI_physics_body"] = {
                    "motion": {
                        "type": body.motion_types
                    },
                    "collider": {
                        "shape": body.shape_index
                    }
                }
            if shape.is_collision:
                obj["OMI_physics_shape"] = {
                    "type": shape.shape_types,
                    "box": {"size": shape.size}
                }
        
        return {'FINISHED'}

# glTF Export User Extension
class glTF2ExportUserExtension:
    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type: ignore
        self.Extension = Extension

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}
        
        # here is where you need to load up the shapes associated with the OMI_physics_body

        n = "OMI_physics_shape"
        gltf_plan.extensions[n] = self.Extension(
            name=n,
            extension={"shapes": [
                {
                    "type": "box",
                    "box": {
                        "size": [1,2,3]
                    }
                }
            ]},
            required=False
        )

        pass

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
