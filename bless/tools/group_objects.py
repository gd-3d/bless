# import bpy
# from mathutils import Vector

# class GroupObjects(bpy.types.Operator):
#     """Group selected objects under an Empty at their center"""
#     bl_idname = "bless.group_objects"
#     bl_label = "Group Objects"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(cls, context):
#         return len(context.selected_objects) > 0

#     def execute(self, context):
#         selected_objects = context.selected_objects

#         if not selected_objects:
#             self.report({'WARNING'}, "No objects selected")
#             return {'CANCELLED'}

#         # Calculate center point of all selected objects
#         center = Vector((0, 0, 0))
#         for obj in selected_objects:
#             center += obj.location
#         center /= len(selected_objects)

#         # Create empty at center
#         empty = bpy.data.objects.new("Group", None)
#         empty.empty_display_type = 'CUBE'
#         empty.location = center
#         context.scene.collection.objects.link(empty)

#         # Parent all selected objects to empty
#         for obj in selected_objects:
#             obj.parent = empty
#             # Keep transform
#             obj.matrix_parent_inverse = empty.matrix_world.inverted()

#         # Select empty and make it active
#         for obj in selected_objects:
#             obj.select_set(True)
#         empty.select_set(True)
#         context.view_layer.objects.active = empty

#         return {'FINISHED'}
