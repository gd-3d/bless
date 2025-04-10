# import copy
# import bpy

# #### constants
# GLTF_LIGHT_FACTOR = 680

# ###### EXTENSIONS #######

# # extensions are used by bless for collisions and base class objects/nodes.
# core_extensions =       [
#                         "KHR_node_visibility", # Hidden nodes
#                         "GODOT_node_lock", # Locked nodes
#                         "KHR_audio_emitter", # AudioStreamPlayer3D
#                         #"EXT_mesh_gpu_instancing", # MultiMeshInstance3D
#                         #"KHR_xmp_json_ld", # Metadata
#                         #OMI_environment_sky # WorldEnvironment sky resource.
#                         ]

# physics_extensions =    [
#                         "OMI_physics_body", # PhysicsBody3D
#                         "OMI_physics_shape", # CollisionShape3D
#                         #OMI_physics_joint, # Joint3D
#                         ]

# # optional extensions WILL BE included with bless and can be used as installable presets. (TODO)
# bless_extensions =     [
#                         #"OMI_seat", # Seat3D
#                         #"OMI_spawn_point", # SpawnPoint3D
#                         #"OMI_vehicle", # Vehicle3D (NOT body?)
#                         ]

# # TODO: allow user extensions. One day.
# user_extensions = []

# ###### EXPORT #######

# def bless_print(message, header=False):
#     separator = "=" * 50
#     if header:
#         print(f"\n{separator}")
#         print(f"[BLESS] {message}")
#         print(f"{separator}")
#     else:
#         print(f"[BLESS] {message}")

# # go up a folder and import bless
# from .. import bless

# class BlessExport:
#     def __init__(self):
#         from io_scene_gltf2.io.com.gltf2_io_extensions import Extension #type:ignore
#         self.Extension = Extension

#     def gather_node_hook(self, gltf2_object, blender_object, export_settings):
#         if gltf2_object.extensions is None:
#             gltf2_object.extensions = {}

#         if hasattr(blender_object, "godot_class"):
#             # Get the class name directly from the object
#             class_name = blender_object["class"] if "class" in blender_object else blender_object.godot_class

#             # Format the class data properly
#             class_data = {
#                 "type": class_name,
#                 "properties": {}
#             }

#             # Add class-specific properties
#             props_name = f"godot_class_{class_name.lower()}_props"
#             if hasattr(blender_object, props_name):
#                 props = getattr(blender_object, props_name)
#                 for prop_name in props.__annotations__:
#                     prop_value = getattr(props, prop_name)
#                     # Handle object references
#                     if isinstance(prop_value, bpy.types.Object):
#                         # Store the object name for now, we'll convert to node index later
#                         class_data["properties"][prop_name] = {"$ref": prop_value.name}
#                     else:
#                         class_data["properties"][prop_name] = prop_value

#             gltf2_object.extras = {"class": class_data}

#         if hasattr(blender_object, "type"):
#             bless_print(f"Object type: [{blender_object.type}]")
#             node_tree[blender_object.name] = {}

#              # Dictionary to store the node flags for each Blender object
#             node_flags = {}

#             # Collect the lock, hidden, and exclude properties for each Blender object
#             # Add these flags to a dictionary for the current node
#             node_flags["locked"] = blender_object.hide_select  # Determines if the object is locked
#             node_flags["hidden"] = blender_object.hide_get()  # Determines if the object is hidden
#             node_flags["exclude"] = blender_object.hide_render  # Determines if the object is excluded from rendering

#             # Store the lock state in node_tree for later use with the physics body
#             node_tree[blender_object.name]["locked"] = node_flags["locked"]

#             # Only add visibility extension here (not lock)
#             if node_flags["hidden"]:
#                 gltf2_object.extensions["KHR_node_visibility"] = {"visible": False}

#             # Create the final dictionary with the object name as the key and node flags as the value
#             node_tree[blender_object.name]["flags"] = node_flags

#             # Print the node flags dictionary for debugging
#             print(node_flags)

#             if blender_object.type == "MESH":
#                 node_tree[blender_object.name]["type"] = "mesh"

#             elif blender_object.type == "LIGHT":
#                 node_tree[blender_object.name]["type"] = "light"

#             elif blender_object.type == "CAMERA":
#                 node_tree[blender_object.name]["type"] = "camera"

#             elif blender_object.type == "SPEAKER":
#                 bless_print("Processing speaker object...")  # Debug print

#                 # Only add audio emitter if there's a sound file assigned
#                 if blender_object.data and blender_object.data.sound:
#                     bless_print(f"Found sound: {blender_object.data.sound.filepath}")  # Debug print
#                     audio_emitter = {
#                         "type": "spatial",
#                         "gain": blender_object.data.volume,
#                         "maxDistance": 0 if blender_object.data.distance_max > 1000000 else blender_object.data.distance_max,
#                         "refDistance": blender_object.data.distance_reference,
#                         "rolloffFactor": blender_object.data.attenuation,
#                         "sound": blender_object.data.sound.filepath if blender_object.data.sound else None,
#                         # Optional directional audio properties
#                         "coneInnerAngle": blender_object.data.cone_angle_inner,
#                         "coneOuterAngle": blender_object.data.cone_angle_outer,
#                         "coneOuterGain": blender_object.data.cone_volume_outer
#                     }

#                     gltf2_object.extensions["KHR_audio_emitter"] = audio_emitter
#                     bless_print(f"Added audio emitter for {blender_object.name}")
#                 else:
#                     bless_print("No sound file assigned to speaker")  # Debug print
#         else:
#             # its a collection.
#             node_tree[blender_object.name] = {}
#             node_tree[blender_object.name]["type"] = "collection"


#     def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
#         if gltf_plan.extensions is None:
#             gltf_plan.extensions = {}

#         # First pass: Build a map of object names to node indices
#         node_map = {}
#         for i, node in enumerate(gltf_plan.nodes):
#             if hasattr(node, "name"):
#                 node_map[node.name] = i

#         # Second pass: Update object references to use node indices
#         for node in gltf_plan.nodes:
#             if hasattr(node, "extras") and isinstance(node.extras, dict):
#                 class_data = node.extras.get("class", {})
#                 if "properties" in class_data:
#                     for prop_name, prop_value in class_data["properties"].items():
#                         if isinstance(prop_value, dict) and "$ref" in prop_value:
#                             # Convert object name reference to node index
#                             ref_name = prop_value["$ref"]
#                             if ref_name in node_map:
#                                 class_data["properties"][prop_name] = node_map[ref_name]
#                             else:
#                                 print(f"Warning: Referenced object {ref_name} not found in scene")
#                                 class_data["properties"][prop_name] = -1

#         # Clean up extras in all nodes
#         for node in gltf_plan.nodes:
#             if hasattr(node, "extras") and isinstance(node.extras, dict):
#                 if "class" in node.extras:
#                     class_data = node.extras["class"]
#                     node.extras = {"class": class_data}
#                 else:
#                     node.extras = {}

#         # Add core extensions to extensionsUsed
#         gltf_plan.extensions_used += core_extensions

#         # Check for audio emitters and explicitly add the extension
#         has_audio = False
#         for node in gltf_plan.nodes:
#             if node.extensions and "KHR_audio_emitter" in node.extensions:
#                 has_audio = True
#                 break

#         if has_audio:
#             if "KHR_audio_emitter" not in gltf_plan.extensions_used:
#                 gltf_plan.extensions_used.append("KHR_audio_emitter")
#                 bless_print("Added KHR_audio_emitter to extensionsUsed")

#         bodies = []
#         shapes = []
#         collision_filters = []  # New list to store collision filters
#         node_map = {}

#         # First pass: Create shapes, collision filters, and body nodes
#         for i, node in enumerate(gltf_plan.nodes):
#             if node.name in node_tree:
#                 if "type" in node_tree[node.name]:
#                     if node_tree[node.name]["type"] == "mesh":
#                         blender_obj = bpy.data.objects.get(node.name)
#                         if blender_obj:
#                             collision_type = blender_obj.collision_types.collision_types
#                             generate_body_node = False
#                             shape = None

#                             if collision_type == "trimesh":
#                                 shape = build_shape_dictionary("trimesh", node.mesh)
#                                 generate_body_node = True
#                             elif collision_type == "convex":
#                                 shape = build_shape_dictionary("convex", node.mesh)
#                                 generate_body_node = True
#                             elif collision_type == "none":
#                                 print("no collision type, skipping.")
#                                 continue
#                             else:
#                                 print("custom collision type, skipping.")
#                                 continue

#                             if shape is not None:
#                                 shapes.append(shape)


#                             if generate_body_node:
#                                 body = copy.deepcopy(node)
#                                 body.name = f"{node.name}Body"

#                                 physics_body_data = build_body_dictionary("static", shape_index=len(shapes) - 1)

#                                 # Add the lock extension only to the body if the original object was locked
#                                 if node_tree[node.name].get("locked", False):
#                                     body.extensions["GODOT_node_lock"] = {"locked": True}

#                                 # Create collision filter and add its index to the body
#                                 collision_filter = build_collision_filter(blender_obj)
#                                 if collision_filter:
#                                     collision_filters.append(collision_filter)
#                                     physics_body_data["collider"]["collisionFilter"] = len(collision_filters) - 1

#                                 body.extensions["OMI_physics_body"] = physics_body_data
#                                 bodies.append(body)
#                                 node_map[i] = len(gltf_plan.nodes) + len(bodies) - 1
#                                 node.translation = None
#                                 node.rotation = None
#                                 node.scale = None

#         # Second pass: Update parent-child relationships
#         for i, node in enumerate(gltf_plan.nodes):
#             if i in node_map:
#                 new_node = bodies[node_map[i] - len(gltf_plan.nodes)]

#                 if node.children:
#                     new_node.children = []
#                     for child_index in node.children:
#                         if child_index in node_map:
#                             new_node.children.append(node_map[child_index])
#                         else:
#                             new_node.children.append(child_index)

#                 # Make the original mesh node a child of the new body node
#                 new_node.children.append(i)
#                 node.children = []  # Remove children from the original node

#                 # format the extras with correct data


#                 if "godot_class" in new_node.extras:
#                     # we need to return the name, but we only get an enum.
#                     print(new_node.extras["godot_class"])

#                 node.extras = {}

#             elif node_tree.get(node.name, {}).get("type") == "collection":
#                 # Handle collections
#                 if node.children:
#                     new_children = []
#                     for child_index in node.children:
#                         if child_index in node_map:
#                             new_children.append(node_map[child_index])
#                         else:
#                             new_children.append(child_index)
#                     node.children = new_children

#         # Update the main node list
#         gltf_plan.nodes += bodies

#         # Add physics extensions
#         gltf_plan.extensions_used += physics_extensions

#         # Add shapes extension
#         gltf_plan.extensions["OMI_physics_shape"] = self.Extension(
#             name="OMI_physics_shape",
#             extension={"shapes": shapes},
#             required=False
#         )

#         # Add collision filters extension, if we have any filters
#         if collision_filters:
#             # Debug print
#             bless_print("Original collision filters:")
#             for f in collision_filters:
#                 bless_print(str(f))

#             # Deduplicate filters
#             unique_filters = []
#             seen = set()

#             for filter_data in collision_filters:
#                 if filter_data is None:
#                     continue

#                 # Convert dict to tuple for hashing
#                 filter_tuple = tuple(sorted([
#                     ('collisionSystems', tuple(sorted(filter_data.get('collisionSystems', [])))),
#                     ('collideWithSystems', tuple(sorted(filter_data.get('collideWithSystems', []))))
#                 ]))

#                 if filter_tuple not in seen:
#                     seen.add(filter_tuple)
#                     unique_filters.append(filter_data)

#             # Debug print
#             bless_print("Deduplicated collision filters:")
#             for f in unique_filters:
#                 bless_print(str(f))

#             if unique_filters:
#                 gltf_plan.extensions["OMI_physics_body"] = self.Extension(
#                     name="OMI_physics_body",
#                     extension={"collisionFilters": unique_filters},
#                     required=False
#                 )

#         # Add the audio extension data at the root level
#         if hasattr(self, 'audio_emitters') and self.audio_emitters:
#             gltf_plan.extensions["KHR_audio_emitter"] = self.Extension(
#                 name="KHR_audio_emitter",
#                 extension={
#                     "audio": self.audio_data,
#                     "sources": self.audio_sources,
#                     "emitters": self.audio_emitters
#                 },
#                 required=False
#             )

#             if "KHR_audio_emitter" not in gltf_plan.extensions_used:
#                 gltf_plan.extensions_used.append("KHR_audio_emitter")

#         bless_print("Gather extensions finished", header=True)


# def build_body_dictionary(type, mass=None, linear_velocity=None, angular_velocity=None, center_of_mass=None, shape_index=None):
#     body_data = {"type": type}

#     if mass and mass > 0:
#         body_data["mass"] = mass
#     if linear_velocity and linear_velocity != (0.0, 0.0, 0.0):
#         body_data["linearVelocity"] = linear_velocity
#     if angular_velocity and angular_velocity != (0.0, 0.0, 0.0):
#         body_data["angularVelocity"] = angular_velocity
#     if center_of_mass and center_of_mass != (0.0, 0.0, 0.0):
#         body_data["centerOfMass"] = center_of_mass
#     if shape_index is not None and shape_index >= 0:
#         body_data["collider"] = {"shape": shape_index}

#     return body_data

# def build_shape_dictionary(shape_type, mesh_index=-1, size=None, radius=None, height=None):
#     shape_data = {}

#     shape_data["type"] = shape_type

#     if shape_type in ["convex", "trimesh"]:
#         shape_data["mesh"] = mesh_index

#     elif shape_type == "box":
#         shape_data["box"] = {"size": size or [1.0, 1.0, 1.0]}
#     elif shape_type in ["sphere", "capsule", "cylinder"]:
#         shape_data[shape_type] = {"radius": radius or 0.5}
#         if shape_type in ["capsule", "cylinder"]:
#             shape_data[shape_type]["height"] = height or 2.0

#     return shape_data

# def build_collision_filter(obj):
#     collision_systems = []
#     collide_with_systems = []

#     # Debug print
#     bless_print(f"Building collision filter for object: {obj.name}")

#     # Get the layers that are enabled
#     for i in range(1, 33):
#         layer_name = f"layer_{i}"

#         # Debug prints
#         layer_enabled = getattr(obj.collision_layers, layer_name, False)
#         mask_enabled = getattr(obj.collision_mask, layer_name, False)
#         bless_print(f"Layer {i}: layer={layer_enabled}, mask={mask_enabled}")

#         # Only add if explicitly True
#         if layer_enabled is True:  # Explicit True check
#             collision_systems.append(f"Layer {i}")
#         if mask_enabled is True:   # Explicit True check
#             collide_with_systems.append(f"Layer {i}")

#     # Debug print
#     bless_print(f"Collision systems: {collision_systems}")
#     bless_print(f"Collide with systems: {collide_with_systems}")

#     # Only create filter if there are actually enabled layers
#     if collision_systems or collide_with_systems:
#         filter_data = {}
#         if collision_systems:
#             filter_data["collisionSystems"] = collision_systems
#         if collide_with_systems:
#             filter_data["collideWithSystems"] = collide_with_systems
#         return filter_data

#     return None
