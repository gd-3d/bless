# NOTE : unit size is not a good idea - use grid size instead.


# a grid panel, to half or double the grid with 2 buttons, and also set the size with a property.
import bpy

# Define custom property for unit_size
bpy.types.Scene.unit_size = bpy.props.FloatProperty(
    name="Unit Size",
    description="Size of the grid units in meters",
    default=1.0,
    min=0.0625,
    max=1024.0,
    step=0.25,
    precision=2,
    update=lambda self, context: update_grid_scale(context, self.unit_size))


class GridPanel(bpy.types.Panel):
    bl_label = "Grid"
    bl_idname = "EDITOR_PT_grid"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Map"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "unit_size", text="Unit Size (m)")

        row = layout.row()
        row.operator("map_editor.double_unit_size", text="", icon="MESH_GRID")
        row.operator("map_editor.halve_unit_size", text="", icon="SNAP_GRID")

        # TODO add snap bool

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
        unit_size = context.scene.unit_size
        context.scene.unit_size = unit_size * 2
        update_grid_scale(context, unit_size * 2)
        return {'FINISHED'}


class GridHalfOperator(bpy.types.Operator):
    bl_idname = "map_editor.halve_unit_size"
    bl_label = "Halve Unit Size"

    def execute(self, context):
        unit_size = context.scene.unit_size
        context.scene.unit_size = unit_size / 2
        update_grid_scale(context, unit_size / 2)
        return {'FINISHED'}


# Setup snapping and far clipping
def setup_snapping():
    bpy.context.scene.tool_settings.snap_elements = {'INCREMENT'}
    #bpy.context.scene.tool_settings.use_snap_grid_absolute = False


def setup_far_clip():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_end = 32000  # 32k for now
