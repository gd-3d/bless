# NOTE : unit size is not a good idea - use grid size instead.

# grid properties
import bpy

# Define custom property for unit_size
unit_size = bpy.props.FloatProperty(
    name="Unit Size",
    description="Size of the grid units in meters",
    default=1.0,
    min=0.0625,
    max=1024.0,
    step=0.25,
    precision=2,
    subtype="DISTANCE",
    update=lambda self, context: update_grid_scale(context, self.unit_size))


# Update grid scale based on unit_size
def update_grid_scale(context, unit_size):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.grid_scale = unit_size


class GridDoubleOperator(bpy.types.Operator):
    bl_idname = "map_editor.double_unit_size"
    bl_label = "Double Unit Size"

    def execute(self, context):
        unit_size = context.window_manager.unit_size
        context.window_manager.unit_size = unit_size * 2
        update_grid_scale(context, unit_size * 2)
        return {'FINISHED'}


class GridHalfOperator(bpy.types.Operator):
    bl_idname = "map_editor.halve_unit_size"
    bl_label = "Halve Unit Size"

    def execute(self, context):
        unit_size = context.window_manager.unit_size
        context.window_manager.unit_size = unit_size / 2
        update_grid_scale(context, unit_size / 2)
        return {'FINISHED'}


# Setup snapping and far clipping
def setup_snapping():
    bpy.context.scene.tool_settings.snap_elements = {'INCREMENT'}
    # bpy.context.scene.tool_settings.use_snap_grid_absolute = False


def setup_far_clip():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_end = 32000  # 32k for now
