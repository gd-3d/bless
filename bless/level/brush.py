

## this script is to contain code for a singular "brush", which is basically a single object in blender
## probably going to be a bunch of operators in here
## also UX for adding stairs, arches, columns... other geonodes tools and modifiers
# autoconvexing.
# patches??? [https://quark.sourceforge.io/infobase/maped.curves.html]
# if this script gets large then maybe it will be better to have some files
## brushes could be contained in a map collection. see map.py

## draws cubes but not very good.
import bpy
import mathutils
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_location_3d



class MapPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Map"
    bl_idname = "VIEW3D_PT_map"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bless"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Geometry", icon='WORLD_DATA')
        row = layout.row()
        row.operator("object.brush_mode")
        row = layout.row()
        row.operator("object.brush_draw")

## broken...
## TODO
class BrushMode(bpy.types.Operator):
    bl_idname = "object.brush_mode"
    bl_label = "Brush Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'S', 'R', 'E'}:
            return {'PASS_THROUGH'}

        obj = context.object

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if obj and obj.type == 'MESH':
                    self.brush_move(context)
                return {'RUNNING_MODAL'}

        elif event.type == 'MOUSEMOVE':
            bpy.ops.object.brush_draw('INVOKE_DEFAULT')
            return {'RUNNING_MODAL'}

        elif event.type == 'RIGHTMOUSE':
            if event.value == 'PRESS':
                self.center_origin(context)
                self.move_surface(context)
                bpy.ops.object.mode_set(mode='OBJECT')
                return {'RUNNING_MODAL'}

        elif event.type == 'G' and event.ctrl:
            self.group_brushes(context)

        elif event.type in {'TAB', 'ESC'}:
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'CANCELLED'}
    
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def brush_move(self, context):
        objects = context.selected_objects
        if context.object:
            bpy.ops.object.select_all(action='DESELECT')
            context.object.select_set(True)
            context.view_layer.objects.active = context.object
            for obj in objects:
                bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(True, True, False))

    def draw_brush(self, context):
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0.5, 0.5, 0.5), scale=(1, 1, 1))
        obj = context.active_object
        obj.name = "Brush"
        if "entity_type" not in obj:
            obj["entity_type"] = "Brush"

    def group_brushes(self, context):
        selected_objects = context.selected_objects
        if len(selected_objects) < 1:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        center = [0.0, 0.0, 0.0]
        for obj in selected_objects:
            center[0] += obj.location[0]
            center[1] += obj.location[1]
            center[2] += obj.location[2]
        center = [c / len(selected_objects) for c in center]

        bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=center, scale=(1, 1, 1))
        group = context.object
        group.name = "Group"
        for obj in selected_objects:
            if obj != group:
                obj.parent = group
                obj.matrix_parent_inverse = group.matrix_world.inverted()

    def move_surface(self, context):
        obj = context.object
        if obj and obj.type == 'MESH':
            bpy.ops.object.mode_set(mode='EDIT')
            context.tool_settings.mesh_select_mode = (False, False, True)
            bpy.ops.view3d.select('INVOKE_DEFAULT')
            context.scene.tool_settings.use_snap_grid_absolute = False
            context.scene.transform_orientation_slots[0].type = 'NORMAL'
            bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(False, False, True))
            context.tool_settings.mesh_select_mode = (False, False, True)
            bpy.ops.mesh.select_all(action='SELECT')
            unit_size = context.scene.unit_settings.scale_length
            bpy.ops.uv.cube_project(cube_size=unit_size)
            bpy.ops.mesh.select_all(action='DESELECT')

    def center_origin(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        unit_size = context.scene.unit_settings.scale_length
        bpy.ops.uv.cube_project(cube_size=unit_size)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

class BrushDraw(bpy.types.Operator):
    """Draw Brush Shapes with Mouse Click and Drag"""
    bl_idname = "object.brush_draw"
    bl_label = "Brush Tool"
    bl_options = {'REGISTER', 'UNDO'}
    
    def __init__(self):
        self.start_mouse_position = None
        self.end_mouse_position = None
        self.drawing = False
        self.start_location = None
        self.end_location = None
        self.current_brush = None

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            if self.drawing:
                self.end_mouse_position = (event.mouse_region_x, event.mouse_region_y)
                self.update_brush(context)

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if not self.drawing:
                self.start_mouse_position = (event.mouse_region_x, event.mouse_region_y)
                self.start_location = self.get_location_from_mouse(context, event.mouse_region_x, event.mouse_region_y)
                self.drawing = True
                self.current_brush = self.create_brush(context, self.start_location)
            else:
                self.finish_brush(context)
                return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            if self.drawing:
                self.cancel_brush(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
    
    def get_location_from_mouse(self, context, x, y):
        region = context.region
        rv3d = context.space_data.region_3d
        coord = (x, y)
        return region_2d_to_location_3d(region, rv3d, coord, (0, 0, 0))
    
    def create_brush(self, context, start_location):
        bpy.ops.mesh.primitive_cube_add(size=1, location=start_location)
        brush = context.active_object
        brush.location = start_location
        return brush
    
    def update_brush(self, context):
        if self.current_brush:
            self.end_location = self.get_location_from_mouse(context, *self.end_mouse_position)
            self.update_brush_geometry(self.current_brush, self.start_location, self.end_location)
    
    def update_brush_geometry(self, brush, start, end):
        min_x = min(start.x, end.x)
        max_x = max(start.x, end.x)
        min_y = min(start.y, end.y)
        max_y = max(start.y, end.y)
        min_z = min(start.z, end.z)
        max_z = max(start.z, end.z)
        
        brush.location = mathutils.Vector(((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2))
        brush.scale = mathutils.Vector(((max_x - min_x) / 2, (max_y - min_y) / 2, (max_z - min_z) / 2))
        
    def finish_brush(self, context):
        self.drawing = False
        self.current_brush = None
    
    def cancel_brush(self, context):
        if self.current_brush:
            bpy.data.objects.remove(self.current_brush, do_unlink=True)
        self.drawing = False
        self.current_brush = None

def snap_to_grid(value, grid_size):
    return round(value / grid_size) * grid_size

def snap_vector_to_grid(vector, grid_size):
    return mathutils.Vector((snap_to_grid(vector.x, grid_size), 
                             snap_to_grid(vector.y, grid_size), 
                             snap_to_grid(vector.z, grid_size)))
