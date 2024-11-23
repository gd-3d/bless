import bpy
from mathutils import Vector
from bpy.props import BoolProperty, EnumProperty
import bmesh
from bpy_extras import view3d_utils

class GreyboxTransform(bpy.types.Operator):
    """Transform object in Trenchbroom style"""
    bl_idname = "bless.greybox_transform"
    bl_label = "Greybox Transform"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties to track state
    is_active: BoolProperty(default=False)
    alt_pressed: BoolProperty(default=False)
    
class GreyboxExtrude(bpy.types.Operator):
    """Extrude faces in Trenchbroom style"""
    bl_idname = "bless.greybox_extrude"
    bl_label = "Greybox Extrude"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def invoke(self, context, event):
        # if object mode:
        if context.mode == 'OBJECT':
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                bpy.data.scenes["Scene"].transform_orientation_slots[0].type = 'NORMAL'
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False})
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

    def execute(self, context):
        return {'FINISHED'}

class GreyboxSnap(bpy.types.Operator):
    """Snap to grid in Trenchbroom style"""
    bl_idname = "bless.greybox_snap"
    bl_label = "Greybox Snap"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}
