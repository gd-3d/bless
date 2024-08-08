OMI_colliders = []

class bless_glTF2Extension:

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type:ignore
        self.Extension = Extension

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}
        
        # iterate through the temporarily stored shapes
        shapes = []
        for gltf_col_mesh in OMI_colliders:
            mesh_index = -1
            
            i = 0
            
            # get the gltf index of this mesh
            for gltf_mesh in gltf_plan.meshes:
                if gltf_col_mesh == gltf_mesh:
                    mesh_index = i
                    break
                i += 1
            
            if mesh_index != -1:
                # good - we found a gltf index corresponding to this mesh
                shapes.append({
                
                    # this hardcodes convex - make sure you expose as an option
                    "type": "convex",
                    "convex": {
                        "mesh": mesh_index
                    }
                })
        
        # error handling - what if mesh_index is -1 ? should not just gen the extension anyways...
        n = "OMI_physics_shape"
        gltf_plan.extensions[n] = self.Extension(
            name=n,
            extension={"shapes": shapes},
            required=False
        )
        print("[BLESS]>> gather extensions finished")



    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}

        # future work: store possible options as an array, iterate, and then tag the gltf data
        n = "OMI_physics_body"
        if n in blender_object:
            
            ext = blender_object[n]
            if "collider" in ext:
                if "shape" in ext["collider"]:
                    # if using a mesh as a shape, add the GLTF mesh object to the OMI_colliders array
                    # this will be used at a later step to generate the collision nodes
                    
                    # add shape
                    if gltf2_object.mesh not in OMI_colliders:
                        OMI_colliders.append(gltf2_object.mesh)
                    
                    # find index
                    i = 0
                    shape_index = -1
                    for col in OMI_colliders:
                        if gltf2_object.mesh == col:
                            shape_index = i
                            break
                        i += 1 
                    
                    # if shape index is -1 we have a problem, need to actually do something with that error
                    blender_object[n]["collider"]["shape"] = shape_index
                
            gltf2_object.extensions[n] = self.Extension(
                name=n,
                extension=blender_object[n],
                required=False
            )

            print("[BLESS]>> gather node finished")


    def gather_scene_hook(self, gltf2_scene, blender_scene, export_settings):
        if gltf2_scene.extensions is None:
            gltf2_scene.extensions = {}

        og_nodes = []
        
        total_nodes = len(gltf2_scene.nodes)

        for node in gltf2_scene.nodes:
            og_nodes.append(node)
        
        print(og_nodes)

        #gltf2_scene.nodes += og_nodes
        print(gltf2_scene)
        print(blender_scene)
        print("[BLESS]>> gather scene finished")




def build_body_dictionary(type, mass=None, linear_velocity=None, angular_velocity=None, center_of_mass=None, shape_index=None):
    body_data = {"type": type}

    if mass and mass > 0:
        body_data["mass"] = mass
    if linear_velocity and linear_velocity != (0.0, 0.0, 0.0):
        body_data["linearVelocity"] = linear_velocity
    if angular_velocity and angular_velocity != (0.0, 0.0, 0.0):
        body_data["angularVelocity"] = angular_velocity
    if center_of_mass and center_of_mass != (0.0, 0.0, 0.0):
        body_data["centerOfMass"] = center_of_mass
    if shape_index is not None and shape_index >= 0:
        body_data["collider"] = {"shape": shape_index}

    return body_data


def build_shape_dictionary(shape_type, mesh_index=-1, size=None, radius=None, height=None):
    shape_data = {"type": shape_type}

    if shape_type in ["convex", "trimesh"]:
        shape_data[shape_type] = {"mesh": mesh_index}
    elif shape_type == "box":
        shape_data["box"] = {"size": size or [1.0, 1.0, 1.0]}
    elif shape_type in ["sphere", "capsule", "cylinder"]:
        shape_data[shape_type] = {"radius": radius or 0.5}
        if shape_type in ["capsule", "cylinder"]:
            shape_data[shape_type]["height"] = height or 2.0

    return shape_data
