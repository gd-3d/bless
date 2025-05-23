
import bpy


# TODO rework this as an operator to call
def update_camera_lock(self, context):
    bpy.ops.view3d.bless_camera_lock()


class BlessPanel(bpy.types.Panel):
    # memoryleak source ENTIRE CLASS

    bl_label = "Bless"
    bl_idname = "VIEW3D_PT_object_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'

    # Main sections
    bpy.types.WindowManager.bless_show_grid = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_view = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_collision = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_tools = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_settings = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_export = bpy.props.BoolProperty(default=False)

    # Grid subsections
    bpy.types.WindowManager.bless_show_grid_snap = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_grid_grid = bpy.props.BoolProperty(default=False)

    # View subsections
    bpy.types.WindowManager.bless_show_view_camera = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_view_grid = bpy.props.BoolProperty(default=False)

    # Bless Properties - subsection
    bpy.types.WindowManager.bless_b_show_tool_box = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_b_show_object_data = bpy.props.BoolProperty(default=False)

    # Collision Panel - subsections
    bpy.types.WindowManager.bless_b_show_collision_settings = bpy.props.BoolProperty(default=False)

    bpy.types.WindowManager.bless_show_collision_shapes = bpy.props.BoolProperty(default=False)

    # Tools subsections
    bpy.types.WindowManager.bless_show_tools_profile = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_tools_origin = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_tools_transform = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_tools_greybox = bpy.props.BoolProperty(default=False)

    # Settings subsections
    bpy.types.WindowManager.bless_show_settings_colors = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_settings_paths = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_settings_defaults = bpy.props.BoolProperty(default=False)

    # Export subsections
    bpy.types.WindowManager.bless_show_export_gltf = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_export_collisions = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.bless_show_export_settings = bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        tools = wm.bless_tools

        # Early return if no object is selected
        if not context.object:
            layout.box().label(text="No object selected!", icon="INFO")
            return

        collision_settings = context.object.bless_object_collision_settings

        collision_types = collision_settings.collision_types

        # EXPORT
        box = layout.box()
        row = box.row()
        row.prop(wm, "bless_show_export", text="Export", icon='TRIA_DOWN' if wm.bless_show_export else 'TRIA_RIGHT', emboss=False)
        if wm.bless_show_export:
            # Add export options here
            pass

        # INFO BOX
        info_box = layout.box()
        info_box.label(text="Information", icon="INFO")

        # Object class information
        obj = context.active_object
        if obj and hasattr(obj, "godot_class"):
            info_box.prop(obj, "godot_class")
            if obj.godot_class != "NONE":
                sub_box = info_box.box()
                sub_box.label(text=f"{obj.godot_class} Properties")
                props = getattr(obj, f"godot_class_{obj.godot_class.lower()}_props", None)
                if props:
                    for prop in props.bl_rna.properties:
                        if not prop.is_hidden:
                            sub_box.prop(props, prop.identifier)

        # Collision information
        if collision_types:
            info_box.label(text=f"Selected object has {str(collision_types).upper()} collision.")

    def draw_collision_layers(self, context, parent_box):
        pass
    #     collision_settings = context.object.bless_object_collision_settings
    #     box = parent_box.box()
    #     box.label(text="Collision Layers")

    #     for row_idx in range(2):
    #         row = box.row()
    #         for block in range(4):
    #             col = row.column()
    #             sub_row = col.row(align=True)
    #             for btn in range(4):
    #                 idx = (row_idx * 16) + (block * 4) + btn
    #                 sub_row.prop(collision_settings, f"layer_{idx + 1}", text=str(idx + 1), toggle=True)

    def draw_collision_mask(self, context, parent_box):
        pass
    #     collision_mask = context.object.collision_mask
    #     box = parent_box.box()
    #     box.label(text="Collision Mask")

    #     for row_idx in range(2):
    #         row = box.row()
    #         for block in range(4):
    #             col = row.column()
    #             sub_row = col.row(align=True)
    #             for btn in range(4):
    #                 idx = (row_idx * 16) + (block * 4) + btn
    #                 sub_row.prop(collision_mask, f"layer_{idx + 1}", text=str(idx + 1), toggle=True)
