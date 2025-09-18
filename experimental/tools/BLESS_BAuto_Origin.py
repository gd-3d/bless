# import bmesh
# import bpy
# from mathutils import Vector


# class BLESS_BAutoOrigin(bpy.types.Operator):
#     bl_idname = "bless.operator_boundary_auto_origin"
#     bl_label = "Bless - B-Auto Origin"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         tools = context.window_manager.bless_tools
#         origin = tools.origin_type

#         for object in context.selected_objects:
#             if (object.type == "MESH"):
#                 match origin:
#                     case "BOUNDS":
#                         bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
#                     case "BOTTOM":
#                         set_origin_to_bounds(object, "BOTTOM")
#                     case "CENTER":
#                         bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS_CENTER')
#                     case "TOP":
#                         set_origin_to_bounds(object, "TOP")
#         return {'FINISHED'}


# def set_origin_to_bounds(object: bpy.types.Object, position="BOTTOM"):
#     cursor_loc = bpy.context.scene.cursor.location.copy()

#     bm = bmesh.new()
#     bm.from_mesh(object.data)
#     bm.verts.ensure_lookup_table()

#     # Transform vertices to world space
#     matrix_world = object.matrix_world
#     verts_world = [matrix_world @ v.co for v in bm.verts]

#     # Find extreme point based on Z coordinate
#     if position == "BOTTOM":
#         z_coord = min(v.z for v in verts_world)
#     else:  # TOP
#         z_coord = max(v.z for v in verts_world)

#     # Get all vertices at that Z level (within small tolerance)
#     tolerance = 0.0001
#     extreme_verts = [v for v in verts_world if abs(v.z - z_coord) < tolerance]

#     # Calculate center point of extreme vertices
#     center = sum(extreme_verts, Vector()) / len(extreme_verts)

#     # Move cursor to calculated point
#     bpy.context.scene.cursor.location = center

#     # Set origin to cursor
#     bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

#     # Restore cursor location
#     bpy.context.scene.cursor.location = cursor_loc

#     # Clean up

#     bm.free()
