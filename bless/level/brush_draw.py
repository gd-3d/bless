import bpy

## broken...
## TODO

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
