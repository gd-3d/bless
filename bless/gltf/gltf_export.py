import copy
import bpy

#### constants
LIGHT_FACTOR = 680





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



#TODO find a way to "install" these automagically from outside the addon.
# glTF extensions library / package manager...
user_extensions = []



node_tree = {}
materials = {}


collision_tree = []

trimesh_collisions = []
convex_collisions = []
custom_collisions = []

# each node as a dict with each flag.
# locked (selectable)
# hidden (in)
# exclude from render...
node_flags = []

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
    
    # def gather_material_hook(self, gltf2_material, blender_material, export_settings):
    #     if gltf2_material.extensions is None:
    #         gltf2_material.extensions = {}
        
    # def gather_material_pbr_metallic_roughness_hook(self, gltf2_material, blender_material, orm_texture, export_settings):
    #     print(len(gltf2_material.extensions))


    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}
        
        if hasattr(blender_object, "type"):
            bless_print(f"Object type: [{blender_object.type}]")
            node_tree[blender_object.name] = {}
            

            
            
            
            # Dictionary to store the node flags for each Blender object
            node_flags = {}
            
            # Collect the lock, hidden, and exclude properties for each Blender object
            locked = blender_object.hide_select  # Determines if the object is locked
            hidden = blender_object.hide_get()  # Determines if the object is hidden
            exclude = blender_object.hide_render  # Determines if the object is excluded from rendering

            # Add these flags to a dictionary for the current node
            node_flags["locked"] = locked
            node_flags["hidden"] = hidden
            node_flags["exclude"] = exclude

            # Create the final dictionary with the object name as the key and node flags as the value
            node_tree[blender_object.name] = node_flags

            # Print the node flags dictionary for debugging
            print(node_flags)
            


            if blender_object.type == "MESH":
        
                node_tree[blender_object.name]["type"] = "mesh"
                
                print("node is: ",node_tree[blender_object.name], "and type: ", node_tree[blender_object.name]["type"])
            
            elif blender_object.type == "LIGHT":
                node_tree[blender_object.name]["type"] = "light"
                print("node is: ",node_tree[blender_object.name], "and type: ", node_tree[blender_object.name]["type"])

            elif blender_object.type == "CAMERA":
                node_tree[blender_object.name]["type"] = "camera"
                print("node is: ",node_tree[blender_object.name], "and type: ", node_tree[blender_object.name]["type"])
        else:
            # its a collection.
            node_tree[blender_object.name] = {}
            node_tree[blender_object.name]["type"] = "collection"
            print("collection is: ", blender_object.name)

            collection = blender_object
            
            if blender_object.get("collision"):
                if blender_object["collision"] == "":
                    # exact type value or no shape is given.
                    pass

                # otherwise, sort the tagged objects into their piles for later.

                if blender_object["collision"] == "trimesh":
                    trimesh_collisions.append(blender_object.name )
                elif blender_object["collision"] == "convex":
                    convex_collisions.append(blender_object.name )
                
                ## TODO, implement compound / custom collision setups.
                # elif blender_object["collision"] == "custom":
                #     custom_collisions.append(blender_object)   
          

    
    
    
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


        #TODO FIXME HACK MOVE TO GODOT !!!!!!

        ### gltf fixes...
        # these are issues/bugs that a little elbow grease and a few lines of code can solve :]

        # ## Lights
        # # lights are too bright, inconsistent and light units are different than blenders.
        # if "KHR_lights_punctual" in gltf_plan.extensions:
        #     for light_data in gltf_plan.extensions["KHR_lights_punctual"]["lights"]:
        #         blender_intensity = light_data["intensity"]
                
        #         # TODO, convert light intensity properly.
        #         if blender_intensity > 100.0:
        #             light_data["intensity"] = blender_intensity / 680 # light factor for godot
                
        #         # TODO, fix distances for point lights


        
        # ## Materials
        # # KHR texture transform is inconsistent / scale is incorrect
        # # https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_texture_transform
        # for material in gltf_plan.materials:
        #     print(material.name)
        #     extensions = material.pbr_metallic_roughness.extensions # FIXME - why is this empty?
        #     for ext in extensions: 
        #         print(ext)

        #TODO FIXME HACK MOVE TO GODOT !!!!!!



