import bpy


def UIPreset_ObjectDataSheet(self, context: bpy.types.Context):
    layout: bpy.types.UILayout = self.layout.box()

    window_manager = context.window_manager
    if (context.object is not None):
        layout.prop(
            window_manager,
            "bless_b_show_object_data",
            text="Bless Object Data",
            icon='TRIA_DOWN' if window_manager.bless_b_show_object_data else 'TRIA_RIGHT',
            emboss=False
        )

    if (window_manager.bless_b_show_object_data):
        row = layout.row().split(factor=0.02)
        row.separator()
        object_data_layout = row.column()

        UIPreset_ObjectCollisionSettings(object_data_layout, context)


def UIPreset_ObjectCollisionSettings(layout: bpy.types.UILayout, context: bpy.types.Context):
    if (layout is not None) and (context is not None):
        window_manager = context.window_manager

        if (context.object is not None) and (hasattr(context.object, "bless_object_collision_settings")):
            layout.prop(
                window_manager,
                "bless_b_show_collision_settings",
                text="Collision Settings",
                icon='TRIA_DOWN' if window_manager.bless_b_show_collision_settings else 'TRIA_RIGHT',
                emboss=False
            )

            row = layout.row().split(factor=0.04)
            row.separator()
            object_data_layout = row.column()

            if (window_manager.bless_b_show_collision_settings):

                object_collision = context.object.bless_object_collision_settings
                object_data_layout.prop(object_collision, "collision_types", text="Type")

                # Only show "Apply Collision" button when multiple objects are selected
                try:
                    context.selected_objects[1]
                    object_data_layout.operator("object.gd3d_apply_collisions", text="Apply Collision", icon="CUBE")
                except:
                    pass

                if (object_collision.collision_types != "none"):
                    object_data_layout.label(text="Collision Layers:")
                    collision_settings = context.object.bless_object_collision_settings
                    object_data_layout.grid_flow(columns=16, row_major=True, even_columns=True, even_rows=True, align=True).prop(collision_settings, "collision_layers")

                    object_data_layout.label(text="Collision Mask Layers:")
                    collision_settings = context.object.bless_object_collision_settings
                    object_data_layout.grid_flow(columns=16, row_major=True, even_columns=True, even_rows=True, align=True).prop(collision_settings, "collision_mask_layers")
