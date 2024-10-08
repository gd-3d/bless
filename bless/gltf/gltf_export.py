import copy
import bpy

#### constants
gltf_light_factor = 680





###### EXTENSIONS #######
#extensions are used by bless for collisions and base class objects/nodes.
core_extensions =       [
                        "KHR_audio_emitter", # AudioStreamPlayer3D
                        "EXT_mesh_gpu_instancing", # MultiMeshInstance3D
                        "KHR_xmp_json_ld", # Metadata
                        ]

physics_extensions =    [
                        "OMI_physics_body", # PhysicsBody3D
                        "OMI_physics_shape", # CollisionShape3D
                        #OMI_physics_joint, # Joint3D
                        ]

# optional extensions WILL BE included with bless and can be used as installable presets. (TODO)
bless_extensions =     [
                        "OMI_seat", # Seat3D
                        "OMI_spawn_point", # SpawnPoint3D
                        "OMI_vehicle", # Vehicle3D (NOT body?)
                        ] 



#TODO find a way to "install" these automagically from outside the file.
# glTF extensions library / package manager...
user_extensions = []



node_tree = {}


###### EXPORT #######

def bless_print(message, header=False):
    separator = "=" * 50
    if header:
        print(f"\n{separator}")
        print(f"[BLESS] {message}")
        print(f"{separator}")
    else:
        print(f"[BLESS] {message}")

class bless_glTF2Extension:

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type:ignore
        self.Extension = Extension
    
    

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}
        
        if hasattr(blender_object, "type"):
            bless_print(f"Object type: [{blender_object.type}]")
            node_tree[blender_object.name] = {}
            if blender_object.type == "MESH":
                node_tree[blender_object.name]["type"] = "mesh"

            elif blender_object.type == "LIGHT":
                node_tree[blender_object.name]["type"] = "light"

            elif blender_object.type == "CAMERA":
                node_tree[blender_object.name]["type"] = "camera"
        else:
            # its a collection.
            node_tree[blender_object.name] = {}
            node_tree[blender_object.name]["type"] = "collection"

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}

        bodies = []
        shapes = []
        node_map = {}  # To keep track of original nodes and their new body nodes

        # First pass: Create shapes and body nodes
        for i, node in enumerate(gltf_plan.nodes):
            if node.name in node_tree:
                if node_tree[node.name]["type"] == "mesh":
                    # Create shape
                    shape = build_shape_dictionary("convex", node.mesh)
                    shapes.append(shape)
                    
                    # Create body node
                    body = copy.deepcopy(node)
                    body.name = f"{node.name}_body"
                    body.extensions["OMI_physics_body"] = build_body_dictionary("static", shape_index=len(shapes) - 1)
                    node.translation = None
                    node.rotation = None
                    node.scale = None
                    
                    bodies.append(body)
                    node_map[i] = len(gltf_plan.nodes) + len(bodies) - 1  # Map original index to new body index

        # Second pass: Update parent-child relationships
        for i, node in enumerate(gltf_plan.nodes):
            if i in node_map:
                new_node = bodies[node_map[i] - len(gltf_plan.nodes)]
                
                if node.children:
                    new_node.children = []
                    for child_index in node.children:
                        if child_index in node_map:
                            new_node.children.append(node_map[child_index])
                        else:
                            new_node.children.append(child_index)
                
                # Make the original node a child of the new node
                new_node.children.append(i)
                node.children = []  # Remove children from the original node
            elif node_tree.get(node.name, {}).get("type") == "collection":
                # Handle collections
                if node.children:
                    new_children = []
                    for child_index in node.children:
                        if child_index in node_map:
                            new_children.append(node_map[child_index])
                        else:
                            new_children.append(child_index)
                    node.children = new_children

        # Update the main node list
        gltf_plan.nodes += bodies

        # Add physics extensions
        gltf_plan.extensions_used += physics_extensions
        gltf_plan.extensions["OMI_physics_shape"] = self.Extension(
            name="OMI_physics_shape",
            extension={"shapes": shapes},
            required=False
        )

        bless_print("Gather extensions finished", header=True)




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
