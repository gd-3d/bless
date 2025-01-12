import bpy

class AutoConvexObject(bpy.types.Operator):
    bl_idname = "object.autoconvex"
    bl_label = "Auto Convex and Separate Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Ensure the object is in object mode before switching to edit mode
        if bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Execute the node group (ensure it exists and is correctly referenced)
        try:
            bpy.ops.geometry.execute_node_group(name="ConvexSplitTool")
        except Exception as e:
            self.report({'ERROR'}, f"Tool is not available: {e}")
            return {'CANCELLED'}
        
        # Separate the mesh by loose parts
        try:
            bpy.ops.mesh.separate(type='LOOSE')
        except Exception as e:
            self.report({'ERROR'}, f"Failed to separate mesh: {e}")
            return {'CANCELLED'}
        
        # Switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return {'FINISHED'}