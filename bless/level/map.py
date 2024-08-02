import bpy

# for collections:
# for the level / map organisation

class MapPanel(bpy.types.Panel):
    bl_label = "Map"
    bl_idname = "VIEW3D_PT_map_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bless'
   
    def draw(self, context):
        layout = self.layout
        obj = context.object
    
        scene = context.scene
        
        row = layout.row()
        row.operator("map.add_map")
        row = layout.row()
        # row.operator("map.add_layer")
        # row = layout.row()


class AddMap(bpy.types.Operator):
    bl_idname = "map.add_map"
    bl_label = "Add Map"
    def execute(self, context):
        map = bpy.data.collections.new("map")
        bpy.context.scene.collection.children.link(map)

