def update_grid_scale(context, unit_size):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.grid_scale = unit_size


def setup_snapping(context):
    context.scene.tool_settings.snap_elements = {'INCREMENT'}


def setup_far_clip(context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_end = 32000  # 32k for now
