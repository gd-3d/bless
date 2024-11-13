# set the origin to the center or the bottom of the mesh

import bpy



class AutoOriginObject(bpy.types.Operator):
    bl_idname = "object.autoorigin"
    bl_label = "Auto Origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tools = context.window_manager.bless_tools
        for obj in context.selected_objects:
            origin = tools.origin_type

            if origin == "BOUNDS":
                bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
            elif origin == "BOTTOM":
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS_BOTTOM')
            elif origin == "CENTER":
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS_CENTER')
            elif origin == "TOP":
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS_TOP')
        return {'FINISHED'}
    