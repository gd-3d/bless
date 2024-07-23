bl_info = {
    "name": "gd3d",
    "category": "Generic",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    'location': 'File > Export > glTF 2.0',
    'description': 'Example addon to add a custom extension to an exported glTF file.',
    'tracker_url': "https://github.com/KhronosGroup/glTF-Blender-IO/issues/",  # Replace with your issue tracker
    'isDraft': False,
    'developer': "(Your name here)", # Replace this
    'url': 'https://your_url_here',  # Replace this
}

import bpy

class TestExportPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_test_export"
    bl_label = "Test Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "Test Export"
            
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        
        row = box.row()
        row.operator("object.gd3d_apply_props", icon="NONE", text="Apply Props")

class ApplyProps(bpy.types.Operator):
    """Apply Props"""
    bl_idname = "object.gd3d_apply_props"
    bl_label = "Apply Props"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        for obj in context.selected_objects:
            
            # HARD CODED FOR NOW
            # implement all motion type and shape options from the OMI standards as dropdowns
            obj["OMI_physics_body"] = {
                "motion": {
                    "type": "dynamic"
                },
                "collider": {
                    "shape": 0
                }
            }
        
        return {'FINISHED'}


classes = [TestExportPanel, ApplyProps]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # when props are needed...
    #bpy.types.Scene.ExampleExtensionProperties = bpy.props.PointerProperty(type=ExampleExtensionProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    # props
    #del bpy.types.Scene.ExampleExtensionProperties

class glTF2ExportUserExtension:

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}
        
        # here is where you need to load up the shapes associated with the OMI_physics_body

        n = "OMI_physics_shape"
        gltf_plan.extensions[n] = self.Extension(
            name=n,
            extension={"shapes": [
                {
                    "type": "box",
                    "box": {
                        "size": [1,2,3]
                    }
                }
            ]},
            required=False
        )

        pass

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}

        # store possible options as an array, iterate, and then tag the gltf data
        n = "OMI_physics_body"
        if n in blender_object:
            gltf2_object.extensions[n] = self.Extension(
                name=n,
                extension=blender_object[n],
                required=False
            )

if __name__ == "__main__":
    register()