## this script handles all gltf extension data applied to objects.

## props

import bpy

class ObjectPanel(bpy.types.Panel):
    bl_label = "Object Panel"
    bl_idname = "VIEW3D_PT_object_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'gd-3d'

    def draw(self, context):
        layout = self.layout.row()
        body_properties = context.scene.body_properties
        shape_properties = context.scene.shape_properties

        layout.separator(factor=2.0)

        indented_layout = layout.column()
        if (context.object is not None):
            indented_layout.row().operator("object.gd3d_apply_props", text="apply")

            indented_layout.label(text="Shape Properties:")
            
            
            prop_indented_layout = indented_layout.row()
            prop_indented_layout.separator(factor=2.0)

            prop_column = prop_indented_layout.column()
            row = prop_column.row()
            row.prop(shape_properties, "is_collision", text="collision object")
            row.prop(shape_properties, "index")

            prop_column.row().prop(shape_properties, "shape_types", text="")

            prop_column.row().prop(shape_properties, "size")

            row = prop_column.row()
            row.prop(shape_properties, "radius")
            row.prop(shape_properties, "height")

            prop_column.row().prop(shape_properties, "mesh")

            row = prop_column.row()
            row.prop(body_properties, "is_motion", text="motion object")
            row.prop(body_properties, "is_trigger", text="trigger object")

            prop_column.row().prop(body_properties, "motion_types")

            prop_column.row().prop(body_properties, "mass")

            prop_column.row().prop(body_properties, "linear_velocity", text="linear velocity")

            prop_column.row().prop(body_properties, "angular_velocity", text="angular velocity")
  
            prop_column.row().prop(body_properties, "center_of_mass", text="center of mass")

            prop_column.row().prop(body_properties, "shape_index", text="shape index")
