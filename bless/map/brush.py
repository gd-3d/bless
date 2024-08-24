

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
    bl_label = "Brush"
    bl_idname = "VIEW3D_PT_map"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bless"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Geometry", icon='WORLD_DATA')
        row = layout.row()
        row.operator("object.autoconvex")
        row = layout.row()
        row.operator("object.brush_mode")

## broken...
## TODO
class BrushMode(bpy.types.Operator):
    bl_idname = "object.brush_mode"
    bl_label = "Brush Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'S', 'E'}:
            return {'PASS_THROUGH'}

        obj = context.object

        if event.shift:
            if event.type == 'D':
                if obj:
                    bpy.ops.object.duplicate(linked=False)
                    self.move_brush(context)

        if event.type == 'R':
            if event.value == 'PRESS':
                if obj and obj.type == 'MESH':
                    bpy.ops.transform.rotate(constraint_axis=(False, False, True))
                return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if obj and obj.type == 'MESH':
                    self.move_brush(context)
                return {'RUNNING_MODAL'}

        if event.type == 'F5':
            pass

        if event.type == 'ESC':
            return {'FINISHED'}
        else:
            return {'RUNNING_MODAL'}
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def move_brush(self, context):
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
