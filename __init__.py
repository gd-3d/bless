bl_info = {
    "name": "My First Addon",
    "blender": (3, 6, 0),  # Minimum Blender version
    "category": "Object",
    "version": (1, 0, 0),
    "author": "Your Name",
    "description": "A simple example addon",
}

import bpy




# Define a simple operator
class OBJECT_OT_hello_operator(bpy.types.Operator):
    bl_idname = "object.say_hello"
    bl_label = "Say Hello"
    bl_description = "Prints 'Hello World' to the console"

    def execute(self, context):
        self.report({'INFO'}, "Hello World!")  # Shows in the status bar
        print("Hello World from my addon!")    # Prints to the console
        return {'FINISHED'}


# Define a panel to access the operator in the 3D View
class OBJECT_PT_hello_panel(bpy.types.Panel):
    bl_label = "Hello Addon"
    bl_idname = "OBJECT_PT_hello_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Hello"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Click the button below:")
        layout.operator("object.say_hello")










# Registration
classes = (
    OBJECT_OT_hello_operator,
    OBJECT_PT_hello_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# For running the script directly inside Blender's text editor
if __name__ == "__main__":
    register()
