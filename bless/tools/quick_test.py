import bpy

#very basic for now
## TODO: use OMI_spawn_point extension
## TODO: add a property to workspace to set the spawn point as an object data type


class QuickTest(bpy.types.Operator):
    bl_idname = "map.quick_test"
    bl_label = "Quick Test"

    def execute(self, context):
        # Find the first object with the 'spawn_point' property
        spawn_obj = None
        for obj in bpy.context.scene.objects:
            if "spawn_point" in obj:
                spawn_obj = obj
                break
        
        if spawn_obj:
            self.report({'INFO'}, f"Teleporting to spawn point at {spawn_obj.location}")
            
            v3d = context.space_data
            rv3d = v3d.region_3d
            rv3d.view_location = spawn_obj.location
            rv3d.view_distance = 0.1  # Set distance to zero so the view_camera position matches view_location
            rv3d.view_rotation = spawn_obj.rotation_quaternion
            bpy.ops.view3d.walk('INVOKE_DEFAULT')
            #return {'FINISHED'}
            return {'RUNNING_MODAL'}
        else:
            self.report({'INFO'}, "No objects with 'spawn_point' found.")
            return {'FINISHED'}
