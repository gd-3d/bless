# set the origin to the center or the bottom of the mesh

import bpy
import bmesh
from mathutils import Vector


class AutoOriginObject(bpy.types.Operator):
    bl_idname = "object.autoorigin"
    bl_label = "Auto Origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tools = context.window_manager.bless_tools
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue
            
            origin = tools.origin_type
            if origin == "BOUNDS":
                bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS")
            elif origin == "BOTTOM":
                set_origin_to_bounds(obj, "BOTTOM")
            elif origin == "CENTER":
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS_CENTER')
            elif origin == "TOP":
                set_origin_to_bounds(obj, "TOP")
        return {'FINISHED'}


def set_origin_to_bounds(obj, position="BOTTOM"):
    # Save the cursor location
    cursor_loc = bpy.context.scene.cursor.location.copy()
    
    # Create bmesh from object
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    
    # Transform vertices to world space
    matrix_world = obj.matrix_world
    verts_world = [matrix_world @ v.co for v in bm.verts]
    
    # Find extreme point based on Z coordinate
    if position == "BOTTOM":
        z_coord = min(v.z for v in verts_world)
    else:  # TOP
        z_coord = max(v.z for v in verts_world)
    
    # Get all vertices at that Z level (within small tolerance)
    tolerance = 0.0001
    extreme_verts = [v for v in verts_world if abs(v.z - z_coord) < tolerance]
    
    # Calculate center point of extreme vertices
    center = sum(extreme_verts, Vector()) / len(extreme_verts)
    
    # Move cursor to calculated point
    bpy.context.scene.cursor.location = center
    
    # Set origin to cursor
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    # Restore cursor location
    bpy.context.scene.cursor.location = cursor_loc
    
    # Clean up

    bm.free()