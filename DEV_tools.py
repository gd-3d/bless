
import bpy

class ApplyProps(bpy.types.Operator):
    """Apply Props"""
    bl_idname = "object.gd3d_apply_props"
    bl_label = "Apply Props"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        for obj in context.selected_objects:
            
            # HARD CODED FOR NOW
            # implement all motion type and shape options from the OMI standards as dropdowns
            obj["OMI_physics_body"] = {
                "motion": {
                    "type": "dynamic"
                },
                "collider": {
                    "shape": 0
                }
            }
        
        return {'FINISHED'}
    

#old version

# class ApplyProps(bpy.types.Operator):
#     """Apply Props"""
#     bl_idname = "object.gd3d_apply_props"
#     bl_label = "Apply Props"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         scene = context.scene
#         body = scene.body_properties
#         shape = scene.shape_properties

        
#         # declare shapes to be used by bodies

#         # for obj in context.selected_objects:
#         #     obj["OMI_physics_shape"] = {
#         #         "type" : shape.shape_types
            
#         #     # each shape declaration goes here


#         #     }

#         for obj in context.selected_objects:
#             obj["OMI_physics_body"] = {
#                 "motion": {
#                     "type": body.motion_types
#                 },
#                 "collider": {
#                     "shape": body.shape_index # shape INDEX goes here.
#                 },
#                 "trigger": body.is_trigger
#             }

#         return {'FINISHED'}
#         ##