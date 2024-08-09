import copy


nodes = []


class bless_glTF2Extension:

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type:ignore
        self.Extension = Extension
    
    

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}

        nodes.append(gltf2_object)

        print("[BLESS]>> gather node finished")

    def gather_scene_hook(self, gltf2_scene, blender_scene, export_settings):
        total_nodes = len(gltf2_scene.nodes)
        for index in range(0, len(gltf2_scene.nodes)):
            new_object_index = index + total_nodes
            gltf2_scene.nodes.append(new_object_index)


    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}
        
        gltf_plan.extensions_used = [
                                     "OMI_physics_body",
                                     "OMI_physics_shape"
                                     ]

        bodies = []
        shapes = []

        node_index = -1
        for node in nodes:
            node_index += 1
            shape = build_shape_dictionary("convex", node_index)
            shapes.append(shape)

            body = copy.deepcopy(node)
            body.extensions["OMI_physics_body"] = build_body_dictionary("static", shape_index=node_index)
            body.children = [node_index]
            
            bodies.append(body)

        node_index = 0

        gltf_plan.nodes += bodies
        
        gltf_plan.extensions["OMI_physics_shape"] = self.Extension(
        name="OMI_physics_shape",
        extension={"shapes": shapes},
        required=False
        )




        

        total_nodes = len(nodes)
        print("total_nodes: ",total_nodes)
        print("[BLESS]>> gather extensions finished")

        nodes.clear()

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
    shape_data = {}
    
    shape_data["type"] = shape_type

    if shape_type in ["convex", "trimesh"]:
        shape_data["mesh"] = mesh_index
        
    elif shape_type == "box":
        shape_data["box"] = {"size": size or [1.0, 1.0, 1.0]}
    elif shape_type in ["sphere", "capsule", "cylinder"]:
        shape_data[shape_type] = {"radius": radius or 0.5}
        if shape_type in ["capsule", "cylinder"]:
            shape_data[shape_type]["height"] = height or 2.0

    return shape_data
