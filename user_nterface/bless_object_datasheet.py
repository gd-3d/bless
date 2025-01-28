import bpy


class BLESS_View3d_ObjectDataSheet(bpy.types.Panel):
    """"""

    bl_label = ""
    bl_idname = "BLESS_PT_view3d_object_data_sheet"

    bl_parent_id = "bless_PT_view3d_object_data"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.box().label(text="THIS IS TEST")
