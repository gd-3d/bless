import bpy

# Temporary storage for colliders
OMI_colliders = []

class bless_glTF2Extension:

    def __init__(self):
        # Import the gltf2 extension module only when this class is instantiated
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type:ignore
        self.Extension = Extension

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        # Ensure the extensions dictionary exists
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}

        # Prepare to store shapes for the extension
        shapes = []

        # Iterate through the colliders
        for gltf_col_mesh in OMI_colliders:
            mesh_index = -1
            
            # Find the index of the current collider mesh in gltf_plan
            for index, gltf_mesh in enumerate(gltf_plan.meshes):
                if gltf_col_mesh == gltf_mesh:
                    mesh_index = index
                    break
            
            if mesh_index != -1:
                # Append shape details to the shapes list
                shapes.append({
                    "type": "convex",
                    "convex": {
                        "mesh": mesh_index
                    }
                })

        # Define the extension name
        extension_name = "OMI_physics_shape"
        
        # Add the extension to the gltf_plan
        gltf_plan.extensions[extension_name] = self.Extension(
            name=extension_name,
            extension={"shapes": shapes},
            required=False
        )

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        # Ensure the extensions dictionary exists
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}

        extension_name = "OMI_physics_body"

        if extension_name in blender_object:
            ext = blender_object[extension_name]

            if "collider" in ext and "shape" in ext["collider"]:
                # Check if the mesh is already in the colliders list
                if gltf2_object.mesh not in OMI_colliders:
                    OMI_colliders.append(gltf2_object.mesh)

                # Find the index of the mesh in the colliders list
                shape_index = OMI_colliders.index(gltf2_object.mesh)

                # Update the shape index in the blender object
                blender_object[extension_name]["collider"]["shape"] = shape_index

            # Add the extension to the gltf2_object
            gltf2_object.extensions[extension_name] = self.Extension(
                name=extension_name,
                extension=blender_object[extension_name],
                required=False
            )
