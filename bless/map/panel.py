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

        map_props = scene.map_properties

        layout = self.layout
        collection = context.collection

        if obj:
            if map_props["lock_camera"] == True:
                bpy.context.space_data.lock_object = bpy.data.objects[obj.name]
            else:
                bpy.context.space_data.lock_object = None

        # Check if the collection has the custom property "is_map"
        if "is_map" in collection:
            row = layout.row()
            row.label(text="Collection Properties")
            row = layout.row()
            row.operator("map.quick_test")
            # Iterate over the custom properties of the collection and display them
            row = layout.row()
            row.prop(map_props, "lock_camera")
            row = layout.row()
        else:
            row = layout.row()
            row.operator("map.add_map")
            

class AddMap(bpy.types.Operator):
    bl_idname = "map.add_map"
    bl_label = "Add Map"
    def execute(self, context):
        map = bpy.data.collections.new("map")
        map["is_map"] = True
        bpy.context.scene.collection.children.link(map)
        return{'FINISHED'}


class MapProperties(bpy.types.PropertyGroup):
    lock_camera: bpy.props.BoolProperty(default=False) # type: ignore