import bpy
from mathutils import Vector
from bpy.props import BoolProperty, EnumProperty

class GreyboxTransform(bpy.types.Operator):
    """Transform object in Trenchbroom style"""
    bl_idname = "bless.greybox_transform"
    bl_label = "Greybox Transform"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties to track state
    is_active: BoolProperty(default=False)
    alt_pressed: BoolProperty(default=False)
    
    def modal(self, context, event):
        if not self.is_active:
            return {'CANCELLED'}

        if event.type == 'ESC':
            self.is_active = False
            return {'CANCELLED'}

        if event.type == 'LEFT_ALT':
            self.alt_pressed = event.value == 'PRESS'

        if context.mode == 'OBJECT':
            # Object mode transformations
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                if context.active_object:
                    # Set appropriate transform orientation
                    if self.alt_pressed:
                        # Z-axis only movement
                        context.scene.transform_orientation_slots[0].type = 'GLOBAL'
                        bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(False, False, True))
                    else:
                        # XY plane movement
                        context.scene.transform_orientation_slots[0].type = 'GLOBAL'
                        bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(True, True, False))
                    
        elif context.mode == 'EDIT_MESH':
            # Edit mode transformations
            if self.alt_pressed and event.type == 'E' and event.value == 'PRESS':
                # Extrude along face normal
                bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT')
                context.scene.transform_orientation_slots[0].type = 'NORMAL'
                bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(False, False, True))

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            self.is_active = True
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}

    def execute(self, context):
        return {'FINISHED'}

class GreyboxExtrude(bpy.types.Operator):
    """Extrude faces in Trenchbroom style"""
    bl_idname = "bless.greybox_extrude"
    bl_label = "Greybox Extrude"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'  # Only available in Edit mode

    def execute(self, context):
        return {'FINISHED'}

class GreyboxSnap(bpy.types.Operator):
    """Snap to grid in Trenchbroom style"""
    bl_idname = "bless.greybox_snap"
    bl_label = "Greybox Snap"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}
