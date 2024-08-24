import copy
import bpy


##

# default settings: 
# Full Heirarchy
# glTF + .bin
# ...



###### EXTENSIONS #######

# these extensions are used by bless for collisions and base class objects/nodes.
core_extensions =   ["OMI_physics_body", # PhysicsBody3D
                    "OMI_physics_shape", # CollisionShape3D
                    #OMI_physics_joint, # Joint3D
                    #KHR_audio_emitter, # AudioStreamPlayer3D
                    ]


# these optional extensions WILL BE included with bless and can be used as presets. (TODO)
vendor_extensions = [
                    #"OMI_seat", # Seat3D
                    #"OMI_spawn_point", # SpawnPoint3D
                    #"OMI_vehicle" # Vehicle3D (NOT body)
                    # look for some more.
                    ] 


# these are imported per "game project". for example some extensions are used in
user_extensions = []

#TODO find a way to "install" these automagically from outside the file.

# pseudo-example: 
# from .definitions import game
# user_extensions = [ game.install_extensions() ]

# if no extension exists - or one is not needed, then we can grab classes/scenes from the game engine
user_library = []
# user_library = [game.install_library()]





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

class bless_glTF2Extension:

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type:ignore
        self.Extension = Extension
    
    

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if gltf2_object.extensions is None:
            gltf2_object.extensions = {}



        
        # Check the type of blender_object and append to the appropriate array
        print("[BLESS]>> processing object : [", blender_object.name, "]")
        if hasattr(blender_object, "type"):

            print("[BLESS]>> object type : [", blender_object.type, "]")
            if blender_object.type == "MESH":
                mesh_nodes.append(gltf2_object)

            elif blender_object.type == "LIGHT":
                light_nodes.append(gltf2_object)

            elif blender_object.type == "CAMERA":
                camera_nodes.append(gltf2_object)

            elif blender_object.type == "EMPTY":
                collection_nodes.append(gltf2_object)
            
            # elif blender_object.type == "COLLECTION": # does mot work ?
            #     collection_nodes.append(gltf2_object)
        else:
            ## must be a collection.
            print("collection :", blender_object.name)
            
            for thing in blender_object:
                print(thing.name)

            if blender_object["is_trimesh"]:
                print("ITS A TRIMESH SHAPE!!!!!!!!!!!!!!!")
                trimesh_collections.append(blender_object)
            else:
                print("ITS CONVEX, HA!")
                convex_collections.append(blender_object)




        print("[BLESS]>> gather node finished")

    
    def gather_scene_hook(self, gltf2_scene, blender_scene, export_settings):
        
        # this adds indexes to scene:{nodes{[0,1,2,3]} in the gltf if required
        # total_mesh_nodes = len(mesh_nodes)
        # for index in range(0, total_mesh_nodes):
        #     new_object_index = index + total_mesh_nodes
        #     gltf2_scene.nodes.append(new_object_index)

        for blender_object in blender_scene.collection.children:
            print(blender_object.name)
        #print(blender_scene.collection.name)

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        if gltf_plan.extensions is None:
            gltf_plan.extensions = {}
        

        print("[BLESS]>> export setting ####", export_settings.get("use_custom_props"))
    ## collisions + physics.  

        gltf_plan.extensions_used = [
                                     "OMI_physics_body",
                                     "OMI_physics_shape"
                                     ]

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
            #node.rotation = None


        node_index = 0

        gltf_plan.nodes += bodies
        
        gltf_plan.extensions["OMI_physics_shape"] = self.Extension(
        name="OMI_physics_shape",
        extension={"shapes": shapes},
        required=False
        )


    ## lights.
        
        # this fixes the light scale factor from blender and godot, which is rougly 680
        # godot uses values from 0.0 to 1.0
        # blender uses watts, and shit like that.


        # for light in gltf_plan.extensions["KHR_lights_punctual"]["lights"]:
        #     blender_intensity = light["intensity"]
            
        #     # TODO, convert light intensity better.
        #     if blender_intensity > 100.0:
        #         light["intensity"] = blender_intensity / 680 # light factor for godot



        # this is already too much, do a loop
        mesh_nodes.clear()
        light_nodes.clear()
        camera_nodes.clear()
        print("[BLESS]>> gather extensions finished")

        # cleanup internal nodes here:
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
