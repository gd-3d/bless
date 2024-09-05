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




###### NODES ############

# here we have some built in arrays to catch and sort nodes and process them at different steps.
# common blender-gltf objects.
mesh_nodes = []
light_nodes = []
camera_nodes = []
collection_nodes = []
#speaker_nodes = [] # TODO: KHR_audio_emitter


# these nodes are generated in this script AFTER reading the scene.
body_nodes = []
#shape_nodes = [] #--not used

convex_collections = []
trimesh_collections = []


###### EXPORT #######

def bless_print(message, is_header=False):
    separator = "=" * 50
    if is_header:
        print(f"\n{separator}")
        print(f"[BLESS] {message}")
        print(f"{separator}")
    else:
        print(f"[BLESS] {message}")

class bless_glTF2Extension:

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type:ignore
        self.Extension = Extension
    
    

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}

        bless_print(f"Processing object: [{blender_object.name}]", is_header=True)
        
        if hasattr(blender_object, "type"):
            bless_print(f"Object type: [{blender_object.type}]")
            if blender_object.type == "MESH":
                mesh_nodes.append(gltf2_object)

            elif blender_object.type == "LIGHT":
                light_nodes.append(gltf2_object)

            elif blender_object.type == "CAMERA":
                camera_nodes.append(gltf2_object)





        bless_print("Gather node finished")

    
    def gather_scene_hook(self, gltf2_scene, blender_scene, export_settings):
        bless_print("Scene objects:", is_header=True)
        for blender_object in blender_scene.collection.children:
            bless_print(f"- {blender_object.name}")

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}
        
        bless_print(f"Export setting: {export_settings.get('use_custom_props')}", is_header=True)
        ## collisions + physics.  

        gltf_plan.extensions_used += physics_extensions

        bodies = []
        shapes = []

        node_index = -1
        for mesh_node in mesh_nodes:
            node_index += 1
            shape = build_shape_dictionary("convex", node_index)
            shapes.append(shape)

            body = copy.deepcopy(mesh_node)
            # attach body to the copy.. type should be static or trimesh
            body.extensions["OMI_physics_body"] = build_body_dictionary("static", shape_index=node_index)
            body.children = [node_index]
            bodies.append(body)

            mesh_node.name = mesh_node.name + "Mesh"
            
            # TODO: this is not good. causes issues. we need to 
            mesh_node.translation = None 
            mesh_node.rotation = None
            mesh_node.scale = None


        node_index = 0

        gltf_plan.nodes += bodies
        
        gltf_plan.extensions["OMI_physics_shape"] = self.Extension(
        name="OMI_physics_shape",
        extension={"shapes": shapes},
        required=False
        )

        # lights    
        # TODO game definition: has_light_factor
        if "KHR_lights_punctual" in gltf_plan.extensions:
            for light in gltf_plan.extensions["KHR_lights_punctual"]["lights"]:
                blender_intensity = light.get("intensity", 0)
                light["intensity"] = blender_intensity / gltf_light_factor # light factor for godot

        bless_print("Gather extensions finished", is_header=True)

        # cleanup internal nodes here:
        mesh_nodes.clear()
        light_nodes.clear()
        camera_nodes.clear()
        body_nodes.clear()



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
