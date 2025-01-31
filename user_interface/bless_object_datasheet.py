import bpy

from ..modules.Alx_Module_Manager_Utils import define_dependency


@define_dependency("BLESS_View3d_ObjectData")
class BLESS_View3d_ObjectDataSheet(bpy.types.Panel):
    """"""

    bl_label = "BLESS Object Data"
    bl_idname = "BLESS_PT_view3d_object_data_sheet"

    bl_parent_id = "bless_PT_view3d_object_data"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.label(text="AAAAAAAAA")
        if (context.object is not None) and (hasattr(context.object, "bless_object_collision_settings")):
            object_collision = context.object.bless_object_collision_settings
            layout.prop(object_collision, "collision_types")
