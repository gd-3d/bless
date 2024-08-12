import bpy


class GameWorld_Properties(bpy.types.PropertyGroup):
    is_trimesh: bpy.props.BoolProperty(default=False)  # type: ignore
    convex_parts: bpy.props.BoolProperty(default=False)  # type: ignore

class GamePanel(bpy.types.Panel):
    bl_label = "Map"
    bl_idname = "VIEW3D_PT_map_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'
   
    def draw(self, context):
        layout = self.layout
        obj = context.object
    
        scene = context.scene
        world = context.world # world?

        #game_props = scene.game_properties

        layout = self.layout
        collection = context.collection

        row = layout.row()
        row.label(text="Game Properties")
        row = layout.row()
        row.label(text="World Properties")
        row = layout.row()
        row.label(text="Entiy Properties")

