import bpy


class BLESS_View3d_Toolset(bpy.types.Panel):
    """"""

    bl_label = ""
    bl_idname = "bless_PT_view3d_toolset"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "tool"

    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def draw(self, context: bpy.types.Context):
        layout = self.layout


class BLESS_View3d_ObjectData(bpy.types.Panel):
    """"""

    bl_label = ""
    bl_idname = "bless_PT_view3d_object_data"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return True

    def draw(self, context: bpy.types.Context):
        pass
