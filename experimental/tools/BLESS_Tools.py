import bpy


class BlessApplyCollisions(bpy.types.Operator):
    """Apply Props"""
    bl_idname = "object.gd3d_apply_collisions"
    bl_label = "Apply Multiple Collisions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not isinstance(context.selected_objects, list):
            self.report({'ERROR'}, "No objects selected or selection is invalid.")
            return {'CANCELLED'}

        collision_type = context.object.collision_types.collision_types
        tools = context.window_manager.bless_tools

        for obj in context.selected_objects:
            # set attribute, not custom property
            obj.collision_types.collision_types = collision_type

            # Set the visual feedback
            obj.grid_type = 'SOLID'
            obj.show_wire = True  # Optional: show wireframe for better visibility
            if collision_type == "trimesh":
                obj.color = tools.trimesh_color
            elif collision_type == "convex":
                obj.color = tools.convex_color

        return {'FINISHED'}
