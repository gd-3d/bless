bl_info = {
    "name": "Bless",
    "author": "gd-3d",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Bless",
    "description": "Blender Level Editor Software Suite",
    "category": "Game Development",
}

generator = f"{bl_info['name']} {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}"

import bpy
import bmesh
import copy
from mathutils import Vector
from bpy.types import (
    Panel,
    Operator,
    PropertyGroup,
    AddonPreferences
)
from bpy.props import (
    EnumProperty,
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
    IntProperty,
    CollectionProperty,
)

#### Constants
# NOTE: Godot needs to divide light intensity by this factor (approximate) to match Blender's lighting
GLTF_LIGHT_FACTOR = 680

#### Extensions
core_extensions = [
    "KHR_node_visibility",
    "KHR_node_selectability", 
    "KHR_audio_emitter",
]

physics_extensions = [
    "OMI_physics_body",
    "OMI_physics_shape",
]

bless_extensions = [
    "BLESS_animation_default",
    "BLESS_animation_looping",
]

node_tree = {}
materials = {}

# ============================================================================
# Utility Functions
# ============================================================================



class BlessExportSettings(PropertyGroup):
    optimise_shapes: BoolProperty(
        name="Optimise Collision Shapes",
        description="Check if each trimesh shape can be a convex hull instead",
        default=False
    ) #type: ignore

class BlessCollisionTypes(PropertyGroup):
    collision_types: EnumProperty(
        name="Collision Type",
        description="Type of collision shape",
        items=[
            ('none', "None", "No collision"),
            ('trimesh', "Trimesh", "Triangle mesh collision (static only)"),
            ('convex', "Convex", "Convex hull collision"),
            ('box', "Box", "Box collision shape"),
            ('sphere', "Sphere", "Sphere collision shape"),
            ('capsule', "Capsule", "Capsule collision shape"),
            ('cylinder', "Cylinder", "Cylinder collision shape"),
        ],
        default='none'
    ) #type: ignore

class BlessPhysicsBody(PropertyGroup):
    body_type: EnumProperty(
        name="Body Type",
        description="Physics body type",
        items=[
            ('static', "Static", "Static body (doesn't move)"),
            ('kinematic', "Animatable", "Animatable body (moves via animation)"),
            ('rigid', "Rigid", "Rigid body (physics simulation)"),
        ],
        default='static'
    ) #type: ignore
    
    discard_mesh: BoolProperty(
        name="Discard Mesh",
        description="If true, the mesh data will be discarded",
        default=False
    ) #type: ignore

    is_trigger: BoolProperty(
        name="Is Trigger",
        description="If true, the shape is a trigger volume (non-solid)",
        default=False
    ) #type: ignore
    
    mass: FloatProperty(
        name="Mass",
        description="Mass of the body (kg)",
        default=1.0,
        min=0.0,
        soft_max=1000.0
    ) #type: ignore
    
    linear_velocity: FloatVectorProperty(
        name="Linear Velocity",
        description="Initial linear velocity",
        default=(0.0, 0.0, 0.0),
        size=3
    ) #type: ignore
    
    angular_velocity: FloatVectorProperty(
        name="Angular Velocity",
        description="Initial angular velocity",
        default=(0.0, 0.0, 0.0),
        size=3
    ) #type: ignore
    
    center_of_mass: FloatVectorProperty(
        name="Center of Mass",
        description="Center of mass offset",
        default=(0.0, 0.0, 0.0),
        size=3
    ) #type: ignore
    
    # Shape properties
    box_size: FloatVectorProperty(
        name="Box Size",
        description="Size of the box shape",
        default=(1.0, 1.0, 1.0),
        min=0.001,
        size=3
    ) #type: ignore
    
    sphere_radius: FloatProperty(
        name="Radius",
        description="Radius of the sphere",
        default=0.5,
        min=0.001
    ) #type: ignore
    
    capsule_radius: FloatProperty(
        name="Radius",
        description="Radius of the capsule",
        default=0.5,
        min=0.001
    ) #type: ignore
    
    capsule_height: FloatProperty(
        name="Height",
        description="Height of the capsule",
        default=2.0,
        min=0.001
    ) #type: ignore
    
    cylinder_radius: FloatProperty(
        name="Radius",
        description="Radius of the cylinder",
        default=0.5,
        min=0.001
    ) #type: ignore
    
    cylinder_height: FloatProperty(
        name="Height",
        description="Height of the cylinder",
        default=2.0,
        min=0.001
    ) #type: ignore

class BlessCollisionLayer(PropertyGroup):
    """Single collision layer property"""
    layer_1: BoolProperty(name="Layer 1", default=False) #type: ignore
    layer_2: BoolProperty(name="Layer 2", default=False) #type: ignore
    layer_3: BoolProperty(name="Layer 3", default=False) #type: ignore
    layer_4: BoolProperty(name="Layer 4", default=False) #type: ignore
    layer_5: BoolProperty(name="Layer 5", default=False) #type: ignore
    layer_6: BoolProperty(name="Layer 6", default=False) #type: ignore
    layer_7: BoolProperty(name="Layer 7", default=False) #type: ignore
    layer_8: BoolProperty(name="Layer 8", default=False) #type: ignore
    layer_9: BoolProperty(name="Layer 9", default=False) #type: ignore
    layer_10: BoolProperty(name="Layer 10", default=False) #type: ignore
    layer_11: BoolProperty(name="Layer 11", default=False) #type: ignore
    layer_12: BoolProperty(name="Layer 12", default=False) #type: ignore
    layer_13: BoolProperty(name="Layer 13", default=False) #type: ignore
    layer_14: BoolProperty(name="Layer 14", default=False) #type: ignore
    layer_15: BoolProperty(name="Layer 15", default=False) #type: ignore
    layer_16: BoolProperty(name="Layer 16", default=False) #type: ignore
    layer_17: BoolProperty(name="Layer 17", default=False) #type: ignore
    layer_18: BoolProperty(name="Layer 18", default=False) #type: ignore
    layer_19: BoolProperty(name="Layer 19", default=False) #type: ignore
    layer_20: BoolProperty(name="Layer 20", default=False) #type: ignore
    layer_21: BoolProperty(name="Layer 21", default=False) #type: ignore
    layer_22: BoolProperty(name="Layer 22", default=False) #type: ignore
    layer_23: BoolProperty(name="Layer 23", default=False) #type: ignore
    layer_24: BoolProperty(name="Layer 24", default=False) #type: ignore
    layer_25: BoolProperty(name="Layer 25", default=False) #type: ignore
    layer_26: BoolProperty(name="Layer 26", default=False) #type: ignore
    layer_27: BoolProperty(name="Layer 27", default=False) #type: ignore
    layer_28: BoolProperty(name="Layer 28", default=False) #type: ignore
    layer_29: BoolProperty(name="Layer 29", default=False) #type: ignore
    layer_30: BoolProperty(name="Layer 30", default=False) #type: ignore
    layer_31: BoolProperty(name="Layer 31", default=False) #type: ignore
    layer_32: BoolProperty(name="Layer 32", default=False) #type: ignore

class BlessAnimationSettings(PropertyGroup):
    """Animation settings for objects"""
    default_animation: StringProperty(
        name="Default Animation",
        description="Default animation to play on load",
        default=""
    ) #type: ignore

# ============================================================================
# Operators
# ============================================================================

class BLESS_OT_apply_to_selected(Operator):
    """Apply current collision settings to all selected objects"""
    bl_idname = "bless.apply_to_selected"
    bl_label = "Apply to Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        active = context.active_object
        if not active:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}
        
        selected = [obj for obj in context.selected_objects if obj != active]
        if not selected:
            self.report({'WARNING'}, "No other objects selected")
            return {'CANCELLED'}
        
        count = 0
        for obj in selected:
            if hasattr(obj, 'collision_types'):
                obj.collision_types.collision_types = active.collision_types.collision_types
                for i in range(1, 33):
                    layer_name = f"layer_{i}"
                    setattr(obj.collision_layers, layer_name, getattr(active.collision_layers, layer_name))
                    setattr(obj.collision_mask, layer_name, getattr(active.collision_mask, layer_name))
                if hasattr(obj, 'physics_body') and hasattr(active, 'physics_body'):
                    obj.physics_body.body_type = active.physics_body.body_type
                    obj.physics_body.is_trigger = active.physics_body.is_trigger
                    obj.physics_body.mass = active.physics_body.mass
                    
                count += 1
        
        self.report({'INFO'}, f"Applied settings to {count} object(s)")
        return {'FINISHED'}

class BLESS_OT_copy_collision_layers(Operator):
    """Copy collision layers from active to selected objects"""
    bl_idname = "bless.copy_collision_layers"
    bl_label = "Copy Layers to Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        active = context.active_object
        if not active:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}
        
        selected = [obj for obj in context.selected_objects if obj != active]
        if not selected:
            self.report({'WARNING'}, "No other objects selected")
            return {'CANCELLED'}
        
        count = 0
        for obj in selected:
            if hasattr(obj, 'collision_layers') and hasattr(active, 'collision_layers'):
                for i in range(1, 33):
                    layer_name = f"layer_{i}"
                    setattr(obj.collision_layers, layer_name, 
                           getattr(active.collision_layers, layer_name))
                    setattr(obj.collision_mask, layer_name, 
                           getattr(active.collision_mask, layer_name))
                count += 1
        
        self.report({'INFO'}, f"Copied layers to {count} object(s)")
        return {'FINISHED'}

# ============================================================================
# UI Panels
# ============================================================================

class BLESS_PT_main_panel(Panel):
    """Main Bless panel"""
    bl_label = "Bless Export"
    bl_idname = "BLESS_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Bless")
        
        if context.active_object:
            obj = context.active_object
            layout.label(text=f"Active: {obj.name}", icon='OBJECT_DATA')
        else:
            layout.label(text="No active object", icon='ERROR')
        
        # Add export settings
        layout.separator()
        scene = context.scene
        if hasattr(scene, 'bless_export_settings'):
            box = layout.box()
            box.label(text="Export Settings", icon='SETTINGS')
            box.prop(scene.bless_export_settings, "optimise_shapes")
            
            ## ?? Add game profile button
            box.separator()
            #box.label(text="Game Profile", icon='GAME')

        

class BLESS_PT_physics_panel(Panel):
    """Physics body settings panel"""
    bl_label = "Physics Body"
    bl_idname = "BLESS_PT_physics_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'
    bl_parent_id = "BLESS_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return False
        if not hasattr(obj, 'collision_types'):
            return False
        return obj.collision_types.collision_types != 'none'
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        physics = obj.physics_body
        collision = obj.collision_types
        
        layout.prop(physics, "body_type")
        layout.prop(physics, "is_trigger")
        
        # Only show physics properties for non-trigger rigid bodies
        if not physics.is_trigger and physics.body_type == 'rigid':
            layout.separator()
            layout.label(text="Physics Properties:", icon='PHYSICS')
            layout.prop(physics, "mass")
            layout.prop(physics, "linear_velocity")
            layout.prop(physics, "angular_velocity")
            layout.prop(physics, "center_of_mass")
        
        # Shape-specific properties
        col_type = collision.collision_types
        
        if col_type == 'box':
            layout.separator()
            layout.label(text="Box Shape:", icon='MESH_CUBE')
            layout.prop(physics, "box_size")
            
        elif col_type == 'sphere':
            layout.separator()
            layout.label(text="Sphere Shape:", icon='MESH_UVSPHERE')
            layout.prop(physics, "sphere_radius")
            
        elif col_type == 'capsule':
            layout.separator()
            layout.label(text="Capsule Shape:", icon='MESH_CAPSULE')
            layout.prop(physics, "capsule_radius")
            layout.prop(physics, "capsule_height")
            
        elif col_type == 'cylinder':
            layout.separator()
            layout.label(text="Cylinder Shape:", icon='MESH_CYLINDER')
            layout.prop(physics, "cylinder_radius")
            layout.prop(physics, "cylinder_height")

class BLESS_PT_collision_panel(Panel):
    """Collision settings panel"""
    bl_label = "Collision Settings"
    bl_idname = "BLESS_PT_collision_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'
    bl_parent_id = "BLESS_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if not hasattr(obj, 'collision_types'):
            layout.label(text="Error: Properties not found", icon='ERROR')
            return
        
        collision = obj.collision_types
        
        layout.prop(collision, "collision_types")
        
        # Show apply button if multiple objects selected
        if len(context.selected_objects) > 1:
            layout.separator()
            layout.operator("bless.apply_to_selected", icon='PASTEDOWN')

class BLESS_PT_animation_panel(Panel):
    """Animation settings panel"""
    bl_label = "Animation Settings"
    bl_idname = "BLESS_PT_animation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'
    bl_parent_id = "BLESS_PT_main_panel"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj:
            return False
        return obj.animation_data is not None and obj.animation_data.action is not None
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        anim_settings = obj.animation_settings
        
        if obj.animation_data and obj.animation_data.action:
            box = layout.box()
            action = obj.animation_data.action
            box.label(text=f"Current Action: {action.name}", icon='ACTION')
            box.prop(action, "use_cyclic", text="Loop Animation")
        
        layout.separator()
        layout.label(text="Default Animation:")
        
        if bpy.data.actions:
            layout.prop_search(anim_settings, "default_animation", bpy.data, "actions", text="")
        else:
            layout.label(text="No actions available", icon='INFO')

class BLESS_PT_collision_layers_panel(Panel):
    """Collision layers panel"""
    bl_label = "Collision Layers"
    bl_idname = "BLESS_PT_collision_layers_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'
    bl_parent_id = "BLESS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return False
        if not hasattr(obj, 'collision_types'):
            return False
        return obj.collision_types.collision_types != 'none'
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if len(context.selected_objects) > 1:
            layout.operator("bless.copy_collision_layers", icon='PASTEDOWN')
            layout.separator()
        
        box = layout.box()
        box.label(text="This Object Is On:", icon='LAYER_ACTIVE')
        self.draw_layer_grid(box, obj.collision_layers)
        
        box = layout.box()
        box.label(text="Collides With:", icon='LAYER_USED')
        self.draw_layer_grid(box, obj.collision_mask)
    
    def draw_layer_grid(self, layout, layer_prop):
        num_layers = 32
        layers_per_row = 16
        num_rows = 2

        for row in range(num_rows):
            row_layout = layout.row(align=True)
            for i in range(layers_per_row):
                layer_num = row * layers_per_row + i + 1
                if layer_num > num_layers:
                    break
                layer_name = f"layer_{layer_num}"
                row_layout.prop(layer_prop, layer_name, text=str(layer_num), toggle=True)

class BLESS_PT_audio_panel(Panel):
    """Audio settings panel"""
    bl_label = "Audio Settings"
    bl_idname = "BLESS_PT_audio_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'
    bl_parent_id = "BLESS_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'SPEAKER'
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        speaker = obj.data
        
        layout.label(text="Audio properties are exported", icon='SPEAKER')
        layout.label(text="from Blender's speaker settings.")
        
        if speaker.sound:
            box = layout.box()
            box.label(text=f"Sound: {speaker.sound.name}", icon='FILE_SOUND')
        else:
            layout.label(text="No sound assigned", icon='ERROR')

# ============================================================================
# Export Hook Functions
# ============================================================================

def bless_print(message, header=False):
    separator = "=" * 50
    if header:
        print(f"\n{separator}")
        print(f"[BLESS] {message}")
        print(f"{separator}")
    else:
        print(f"[BLESS] {message}")

class BlessExport:
    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension
        self.animation_target_map = {}
        self.optimization_stats = {"trimesh_to_convex": 0, "total_trimesh": 0}
        self.default_animation = None

    def gather_animation_hook(self, gltf2_animation, blender_action, blender_object, export_settings):
        bless_print(f"========== gather_animation_hook called ==========", header=True)
        bless_print(f"Animation: {blender_action.name}")
        bless_print(f"Object: {blender_object.name}")
        bless_print(f"Action use_cyclic: {getattr(blender_action, 'use_cyclic', 'N/A')}")
        
        if not hasattr(gltf2_animation, 'extensions') or gltf2_animation.extensions is None:
            gltf2_animation.extensions = {}
            bless_print("Initialized empty extensions dict")
        
        added_extensions = False
        
        if hasattr(blender_object, 'animation_settings'):
            anim_settings = blender_object.animation_settings
            bless_print(f"Object has animation_settings, default_animation: '{anim_settings.default_animation}'")
            
            if anim_settings.default_animation == blender_action.name:
                self.default_animation = blender_action.name
                bless_print(f"✓ Marked as default animation: {blender_action.name}")
        
        if hasattr(blender_action, 'use_cyclic') and blender_action.use_cyclic:
            gltf2_animation.extensions["BLESS_animation_looping"] = self.Extension(
                name="BLESS_animation_looping",
                extension={"loop": True},
                required=False
            )
            bless_print(f"✓ Added looping extension: {blender_action.name}")
            added_extensions = True
        else:
            bless_print(f"✗ Action is not cyclic or use_cyclic not found")
        
        if added_extensions:
            bless_print(f"✓✓ Animation '{blender_action.name}' has extensions: {list(gltf2_animation.extensions.keys())}")
        else:
            bless_print(f"✗✗ No extensions added to animation '{blender_action.name}'")
        
        bless_print(f"========== gather_animation_hook finished ==========")
        
        if hasattr(blender_object, 'collision_types') and blender_object.collision_types.collision_types != 'none':
            body_name = f"{blender_object.name}Body"
            bless_print(f"Object has physics body, will redirect animation to: {body_name}")
            
            if blender_object.name not in self.animation_target_map:
                self.animation_target_map[blender_object.name] = []
            self.animation_target_map[blender_object.name].append(gltf2_animation)

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}
        
        if hasattr(blender_object, "type"):
            bless_print(f"Object type: [{blender_object.type}]")
            node_tree[blender_object.name] = {}
            
            node_flags = {}
            node_flags["locked"] = blender_object.hide_select
            node_flags["hidden"] = blender_object.hide_get()
            node_flags["exclude"] = blender_object.hide_render

            node_tree[blender_object.name]["locked"] = node_flags["locked"]

            if node_flags["hidden"]:
                gltf2_object.extensions["KHR_node_visibility"] = {"visible": False}

            node_tree[blender_object.name]["flags"] = node_flags
            print(node_flags)
    
            if blender_object.type == "MESH":
                node_tree[blender_object.name]["type"] = "mesh"

            elif blender_object.type == "LIGHT":
                node_tree[blender_object.name]["type"] = "light"

            elif blender_object.type == "CAMERA":
                node_tree[blender_object.name]["type"] = "camera"

            elif blender_object.type == "SPEAKER":
                bless_print("Processing speaker object...")
                
                if blender_object.data and blender_object.data.sound:
                    bless_print(f"Found sound: {blender_object.data.sound.filepath}")
                    audio_emitter = {
                        "type": "spatial",
                        "gain": blender_object.data.volume,
                        "maxDistance": 0 if blender_object.data.distance_max > 1000000 else blender_object.data.distance_max,
                        "refDistance": blender_object.data.distance_reference,
                        "rolloffFactor": blender_object.data.attenuation,
                        "sound": blender_object.data.sound.filepath if blender_object.data.sound else None,
                        "coneInnerAngle": blender_object.data.cone_angle_inner,
                        "coneOuterAngle": blender_object.data.cone_angle_outer,
                        "coneOuterGain": blender_object.data.cone_volume_outer
                    }
                    
                    gltf2_object.extensions["KHR_audio_emitter"] = audio_emitter
                    bless_print(f"Added audio emitter for {blender_object.name}")
                else:
                    bless_print("No sound file assigned to speaker")
        else:
            node_tree[blender_object.name] = {}
            node_tree[blender_object.name]["type"] = "collection"

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        gltf_plan.asset.generator = generator
        
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}

        optimize_shapes = bpy.context.scene.bless_export_settings.optimise_shapes
        if optimize_shapes:
            bless_print("Shape optimization is ENABLED", header=True)
        else:
            bless_print("Shape optimization is DISABLED", header=True)

        gltf_plan.extensions_used += core_extensions
        
        has_audio = False
        for node in gltf_plan.nodes:
            if node.extensions and "KHR_audio_emitter" in node.extensions:
                has_audio = True
                break
        
        if has_audio:
            if "KHR_audio_emitter" not in gltf_plan.extensions_used:
                gltf_plan.extensions_used.append("KHR_audio_emitter")
                bless_print("Added KHR_audio_emitter to extensionsUsed")
        
        has_default_anim = False
        has_looping = False
        
        if self.default_animation:
            gltf_plan.extensions["BLESS_animation_default"] = self.Extension(
                name="BLESS_animation_default",
                extension={"defaultAnimation": self.default_animation},
                required=False
            )
            has_default_anim = True
            bless_print(f"Added BLESS_animation_default to root extensions: {self.default_animation}")
        
        if hasattr(gltf_plan, 'animations') and gltf_plan.animations:
            for animation in gltf_plan.animations:
                if hasattr(animation, 'extensions') and animation.extensions:
                    if "BLESS_animation_looping" in animation.extensions:
                        has_looping = True
                        break
        
        if has_default_anim and "BLESS_animation_default" not in gltf_plan.extensions_used:
            gltf_plan.extensions_used.append("BLESS_animation_default")
            bless_print("Added BLESS_animation_default to extensionsUsed")
        
        if has_looping and "BLESS_animation_looping" not in gltf_plan.extensions_used:
            gltf_plan.extensions_used.append("BLESS_animation_looping")
            bless_print("Added BLESS_animation_looping to extensionsUsed")

        bodies = []
        shapes = []
        collision_filters = []
        collision_filter_map = {}
        node_map = {}

        # First pass: Create shapes and body nodes
        for i, node in enumerate(gltf_plan.nodes):
            if node.name in node_tree:
                if "type" in node_tree[node.name]:
                    if node_tree[node.name]["type"] == "mesh":
                        blender_obj = bpy.data.objects.get(node.name)
                        if blender_obj:
                            collision_type = blender_obj.collision_types.collision_types
                            generate_body_node = False
                            shape = None

                            if collision_type == "trimesh":
                                if optimize_shapes:
                                    self.optimization_stats["total_trimesh"] += 1
                                    bless_print(f"Checking if trimesh '{blender_obj.name}' can be optimized to convex...")
                                    try:
                                        if is_mesh_convex(blender_obj):
                                            bless_print(f"✓ Optimized '{blender_obj.name}': trimesh → convex")
                                            shape = build_shape_dictionary("convex", node.mesh)
                                            self.optimization_stats["trimesh_to_convex"] += 1
                                        else:
                                            bless_print(f"✗ '{blender_obj.name}' is not convex, keeping as trimesh")
                                            shape = build_shape_dictionary("trimesh", node.mesh)
                                    except Exception as e:
                                        bless_print(f"✗ Error checking convexity for '{blender_obj.name}': {e}")
                                        shape = build_shape_dictionary("trimesh", node.mesh)
                                else:
                                    shape = build_shape_dictionary("trimesh", node.mesh)
                                generate_body_node = True
                                
                            elif collision_type == "convex":
                                shape = build_shape_dictionary("convex", node.mesh)
                                generate_body_node = True
                            elif collision_type == "none":
                                print("no collision type, skipping.")
                                continue
                            else:
                                physics = blender_obj.physics_body
                                if collision_type == "box":
                                    shape = build_shape_dictionary("box", size=list(physics.box_size))
                                elif collision_type == "sphere":
                                    shape = build_shape_dictionary("sphere", radius=physics.sphere_radius)
                                elif collision_type == "capsule":
                                    shape = build_shape_dictionary("capsule", 
                                        radius=physics.capsule_radius, 
                                        height=physics.capsule_height)
                                elif collision_type == "cylinder":
                                    shape = build_shape_dictionary("cylinder",
                                        radius=physics.cylinder_radius,
                                        height=physics.cylinder_height)
                                
                                if shape:
                                    generate_body_node = True

                            if shape is not None:
                                shapes.append(shape)
                            
                            if generate_body_node:
                                body = copy.deepcopy(node)
                                body.name = f"{node.name}Body"

                                is_trigger = blender_obj.physics_body.is_trigger
                                
                                physics_body_data = build_body_dictionary(
                                    blender_obj.physics_body.body_type,
                                    mass=blender_obj.physics_body.mass if blender_obj.physics_body.body_type == 'rigid' and not is_trigger else None,
                                    linear_velocity=tuple(blender_obj.physics_body.linear_velocity) if not is_trigger else None,
                                    angular_velocity=tuple(blender_obj.physics_body.angular_velocity) if not is_trigger else None,
                                    center_of_mass=tuple(blender_obj.physics_body.center_of_mass) if not is_trigger else None,
                                    shape_index=len(shapes) - 1,
                                    is_trigger=is_trigger
                                )
                                
                                if node_tree[node.name].get("locked", False):
                                    body.extensions["KHR_node_selectability"] = {"selectable": False}
                                
                                # Create collision filter
                                collision_filter = build_collision_filter(blender_obj)
                                if collision_filter:
                                    body_index = len(bodies)
                                    collision_filter_map[body_index] = collision_filter
                                
                                body.extensions["OMI_physics_body"] = physics_body_data
                                bodies.append(body)
                                node_map[i] = len(gltf_plan.nodes) + len(bodies) - 1
                                node.translation = None
                                node.rotation = None
                                node.scale = None
                                

        # Print optimization statistics
        if optimize_shapes and self.optimization_stats["total_trimesh"] > 0:
            optimized = self.optimization_stats["trimesh_to_convex"]
            total = self.optimization_stats["total_trimesh"]
            bless_print(f"Optimization Results: {optimized}/{total} trimesh shapes converted to convex", header=True)

        # Second pass: Update parent-child relationships
        for i, node in enumerate(gltf_plan.nodes):
            if i in node_map:
                new_node = bodies[node_map[i] - len(gltf_plan.nodes)]
                
                if node.children:
                    new_node.children = []
                    for child_index in node.children:
                        if child_index in node_map:
                            new_node.children.append(node_map[child_index])
                        else:
                            new_node.children.append(child_index)
                
                new_node.children.append(i)
                node.children = []
                
            elif node_tree.get(node.name, {}).get("type") == "collection":
                if node.children:
                    new_children = []
                    for child_index in node.children:
                        if child_index in node_map:
                            new_children.append(node_map[child_index])
                        else:
                            new_children.append(child_index)
                    node.children = new_children


        # Third pass: Update animation targets
        if gltf_plan.animations:
            bless_print("Processing animations for body node redirection...")
            for animation in gltf_plan.animations:
                for channel in animation.channels:
                    if channel.target and channel.target.node is not None:
                        original_node_index = channel.target.node
                        if original_node_index in node_map:
                            body_node_index = node_map[original_node_index]
                            bless_print(f"Redirecting animation channel from node {original_node_index} to body node {body_node_index}")
                            channel.target.node = body_node_index

        gltf_plan.nodes += bodies

        # Transfer collision filter map to collision_filters list
        for body_idx, filter_data in collision_filter_map.items():
            collision_filters.append(filter_data)
            bless_print(f"Added collision filter for body {body_idx}: {filter_data}")

        gltf_plan.extensions_used += physics_extensions
        
        gltf_plan.extensions["OMI_physics_shape"] = self.Extension(
            name="OMI_physics_shape",
            extension={"shapes": shapes},
            required=False
        )

        if collision_filters:
            bless_print("Original collision filters:")
            for f in collision_filters:
                bless_print(str(f))

            unique_filters = []
            seen = set()
            
            for filter_data in collision_filters:
                if filter_data is None:
                    continue
                
                filter_tuple = tuple(sorted([
                    ('collisionSystems', tuple(sorted(filter_data.get('collisionSystems', [])))),
                    ('collideWithSystems', tuple(sorted(filter_data.get('collideWithSystems', [])))),
                ]))
                
                if filter_tuple not in seen:
                    seen.add(filter_tuple)
                    unique_filters.append(filter_data)

            bless_print("Deduplicated collision filters:")
            for f in unique_filters:
                bless_print(str(f))

            if unique_filters:
                gltf_plan.extensions["OMI_physics_body"] = self.Extension(
                    name="OMI_physics_body",
                    extension={"collisionFilters": unique_filters},
                    required=False
                )

        bless_print("Gather extensions finished", header=True)

    def gather_gltf_hook(self, active_scene_idx, scenes, animations, export_settings):
        bless_print("Processing animations in gather_gltf_hook", header=True)
        
        if animations:
            bless_print(f"Found {len(animations)} animations")
            
            for anim in animations:
                bless_print(f"Processing animation: {anim.name}")
                
                if not hasattr(anim, 'extensions') or anim.extensions is None:
                    anim.extensions = {}
                
                blender_action = bpy.data.actions.get(anim.name)
                if not blender_action:
                    bless_print(f"  Could not find Blender action for '{anim.name}'")
                    continue
                
                bless_print(f"  Found Blender action: {blender_action.name}")
                bless_print(f"  Action use_cyclic: {getattr(blender_action, 'use_cyclic', False)}")
                
                if hasattr(blender_action, 'use_cyclic') and blender_action.use_cyclic:
                    anim.extensions["BLESS_animation_looping"] = self.Extension(
                        name="BLESS_animation_looping",
                        extension={"loop": True},
                        required=False
                    )
                    bless_print(f"  ✓ Added looping extension")
                
                for obj in bpy.data.objects:
                    if hasattr(obj, 'animation_settings'):
                        anim_settings = obj.animation_settings
                        if anim_settings.default_animation == blender_action.name:
                            self.default_animation = blender_action.name
                            bless_print(f"  ✓ Marked as default animation (set by {obj.name})")
                            break
                
                if hasattr(anim, 'extensions') and anim.extensions:
                    bless_print(f"  Final extensions: {list(anim.extensions.keys())}")
                else:
                    bless_print(f"  No extensions added")
        
        bless_print("gather_gltf_hook finished", header=True)

class glTF2ExportUserExtension(BlessExport):
    def __init__(self):
        super().__init__()

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        return super().gather_gltf_extensions_hook(gltf_plan, export_settings)

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        return super().gather_node_hook(gltf2_object, blender_object, export_settings)
    
    def gather_animation_hook(self, gltf2_animation, blender_action, blender_object, export_settings):
        return super().gather_animation_hook(gltf2_animation, blender_action, blender_object, export_settings)
    
    def gather_gltf_hook(self, active_scene_idx, scenes, animations, export_settings):
        return super().gather_gltf_hook(active_scene_idx, scenes, animations, export_settings)

def build_body_dictionary(type, mass=None, linear_velocity=None, angular_velocity=None, center_of_mass=None, shape_index=None, is_trigger=False):
    if is_trigger:
        # For triggers, we only create the trigger property
        trigger_data = {}
        if shape_index is not None and shape_index >= 0:
            trigger_data["shape"] = shape_index
        return {"trigger": trigger_data}
    else:
        # For regular bodies, create the full body data
        body_data = {"type": type}

        if mass and mass > 0:
            body_data["mass"] = mass
        if linear_velocity and linear_velocity != (0.0, 0.0, 0.0):
            body_data["linearVelocity"] = linear_velocity
        if angular_velocity and angular_velocity != (0.0, 0.0, 0.0):
            body_data["angularVelocity"] = angular_velocity
        if center_of_mass and center_of_mass != (0.0, 0.0, 0.0):
            body_data["centerOfMass"] = center_of_mass
        if shape_index is not None and shape_index >= 0:
            body_data["collider"] = {"shape": shape_index}

        return body_data

def build_shape_dictionary(shape_type, mesh_index=-1, size=None, radius=None, height=None):
    shape_data = {}
    
    shape_data["type"] = shape_type

    if shape_type in ["convex", "trimesh"]:
        shape_data["mesh"] = mesh_index
        
    elif shape_type == "box":
        shape_data["box"] = {"size": size or [1.0, 1.0, 1.0]}
    elif shape_type in ["sphere", "capsule", "cylinder"]:
        shape_data[shape_type] = {"radius": radius or 0.5}
        if shape_type in ["capsule", "cylinder"]:
            shape_data[shape_type]["height"] = height or 2.0

    return shape_data

def build_collision_filter(obj):
    collision_systems = []
    collide_with_systems = []
    not_collide_with_systems = []  # Currently not used in Blender UI
    
    bless_print(f"Building collision filter for object: {obj.name}")
    
    # Get the layers that are enabled
    for i in range(1, 33):
        layer_name = f"layer_{i}"
        
        layer_enabled = getattr(obj.collision_layers, layer_name, False)
        mask_enabled = getattr(obj.collision_mask, layer_name, False)

        if layer_enabled is True:
            collision_systems.append(f"Layer {i}")
        if mask_enabled is True:
            collide_with_systems.append(f"Layer {i}")

    bless_print(f"Collision systems: {collision_systems}")
    bless_print(f"Collide with systems: {collide_with_systems}")

    if collision_systems or collide_with_systems or not_collide_with_systems:
        filter_data = {}
        if collision_systems:
            filter_data["collisionSystems"] = collision_systems
        if collide_with_systems:
            filter_data["collideWithSystems"] = collide_with_systems
        if not_collide_with_systems:
            filter_data["notCollideWithSystems"] = not_collide_with_systems
        return filter_data
    
    return None

# ============================================================================
# Registration
# ============================================================================

classes = (
    BlessExportSettings,
    BlessCollisionTypes,
    BlessPhysicsBody,
    BlessCollisionLayer,
    BlessAnimationSettings,
    BLESS_OT_apply_to_selected,
    BLESS_OT_copy_collision_layers,
    BLESS_PT_main_panel,
    BLESS_PT_physics_panel,
    BLESS_PT_collision_panel,
    BLESS_PT_animation_panel,
    BLESS_PT_collision_layers_panel,
    BLESS_PT_audio_panel,
)

bless_export_instance = None
bless_gltf_wrapper_instance = None
bless_gltf_registration = None

def register():
    global bless_export_instance, bless_gltf_wrapper_instance, bless_gltf_registration
    
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bless_export_settings = bpy.props.PointerProperty(type=BlessExportSettings)
    bpy.types.Object.collision_types = bpy.props.PointerProperty(type=BlessCollisionTypes)
    bpy.types.Object.physics_body = bpy.props.PointerProperty(type=BlessPhysicsBody)
    bpy.types.Object.collision_layers = bpy.props.PointerProperty(type=BlessCollisionLayer)
    bpy.types.Object.collision_mask = bpy.props.PointerProperty(type=BlessCollisionLayer)
    bpy.types.Object.animation_settings = bpy.props.PointerProperty(type=BlessAnimationSettings)
    
    try:
        bless_export_instance = glTF2ExportUserExtension()
        
        try:
            import io_scene_gltf2 as gltf_module
            
            available_attrs = [
                'export_user_extensions',
                'gltf2_addon',
            ]
            found = {}
            for a in available_attrs:
                found[a] = hasattr(gltf_module, a)

            print(f"[BLESS] glTF module detected. available attributes: {found}")

            if hasattr(gltf_module, 'export_user_extensions') and isinstance(getattr(gltf_module, 'export_user_extensions'), list):
                gltf_module.export_user_extensions.append(bless_export_instance)
                bless_gltf_wrapper_instance = bless_export_instance
                bless_gltf_registration = ('module_list', gltf_module, 'export_user_extensions')
                print('[BLESS] Registered glTF export hooks via gltf_module.export_user_extensions')
                print(f'[BLESS] Registered hooks: gather_node_hook, gather_gltf_extensions_hook, gather_animation_hook, gather_gltf_hook')
                
            elif hasattr(gltf_module, 'gltf2_addon') and hasattr(gltf_module.gltf2_addon, 'register_user_extensions'):
                try:
                    print('[BLESS] Found gltf_module.gltf2_addon.register_user_extensions, attempting to call it')
                    gltf_module.gltf2_addon.register_user_extensions(bless_export_instance)
                    bless_gltf_wrapper_instance = bless_export_instance
                    bless_gltf_registration = ('gltf2_addon_api', gltf_module.gltf2_addon, 'register_user_extensions')
                    print('[BLESS] Registered glTF export hooks via gltf2_addon.register_user_extensions')
                except Exception as e:
                    print(f'[BLESS] Error calling gltf2_addon.register_user_extensions: {e}')
                    raise
            else:
                bpy.types.Scene.bless_gltf_extension = bless_export_instance
                bless_gltf_wrapper_instance = bless_export_instance
                bless_gltf_registration = ('scene_attr', None, 'bless_gltf_extension')
                print('[BLESS] Stored glTF extension on Scene.bless_gltf_extension (fallback)')
                
        except ImportError:
            bpy.types.Scene.bless_gltf_extension = bless_export_instance
            bless_gltf_wrapper_instance = bless_export_instance
            bless_gltf_registration = ('scene_attr', None, 'bless_gltf_extension')
            print('[BLESS] glTF addon not found; stored extension on Scene.bless_gltf_extension')
            
    except Exception as e:
        print(f"[BLESS] Error registering export hooks: {e}")
        import traceback
        traceback.print_exc()
    
    print("[BLESS] Addon registered successfully")

def unregister():
    global bless_export_instance
    
    global bless_gltf_wrapper_instance, bless_gltf_registration

    if bless_gltf_registration:
        method = bless_gltf_registration[0]
        try:
            if method == 'module_list':
                _, module, attr = bless_gltf_registration
                if module and hasattr(module, attr):
                    try:
                        getattr(module, attr).remove(bless_gltf_wrapper_instance)
                    except ValueError:
                        pass
            elif method == 'gltf2_addon_api':
                _, api_module, func = bless_gltf_registration
                if api_module and hasattr(api_module, 'unregister_user_extensions'):
                    try:
                        api_module.unregister_user_extensions(bless_gltf_wrapper_instance)
                    except Exception:
                        pass
            elif method == 'scene_attr':
                if hasattr(bpy.types.Scene, 'bless_gltf_extension'):
                    del bpy.types.Scene.bless_gltf_extension
        except Exception:
            pass
        bless_gltf_wrapper_instance = None
        bless_gltf_registration = None
    
    del bpy.types.Scene.bless_export_settings
    del bpy.types.Object.collision_types
    del bpy.types.Object.physics_body
    del bpy.types.Object.collision_layers
    del bpy.types.Object.collision_mask
    del bpy.types.Object.animation_settings
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    bless_export_instance = None
    print("[BLESS] Addon unregistered")

if __name__ == "__main__":
    register()
    