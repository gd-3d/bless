from .. import bless
import copy

import bpy

# constants
GLTF_LIGHT_FACTOR = 680

###### EXTENSIONS #######

# extensions are used by bless for collisions and base class objects/nodes.
core_extensions = [
    "KHR_node_visibility",  # Hidden nodes
    "GODOT_node_lock",  # Locked nodes
                        "KHR_audio_emitter",  # AudioStreamPlayer3D
                        # "EXT_mesh_gpu_instancing", # MultiMeshInstance3D
                        # "KHR_xmp_json_ld", # Metadata
                        # OMI_environment_sky # WorldEnvironment sky resource.
]

physics_extensions = [
    "OMI_physics_body",  # PhysicsBody3D
    "OMI_physics_shape",  # CollisionShape3D
    # OMI_physics_joint, # Joint3D
]

# optional extensions WILL BE included with bless and can be used as installable presets. (TODO)
bless_extensions = [
    # "OMI_seat", # Seat3D
    # "OMI_spawn_point", # SpawnPoint3D
    # "OMI_vehicle", # Vehicle3D (NOT body?)
]

# TODO: allow user extensions. One day.
user_extensions = []

###### EXPORT #######


def bless_print(message, header=False):
    separator = "=" * 50
    if header:
        print(f"\n{separator}")
        print(f"[BLESS] {message}")
        print(f"{separator}")
    else:
        print(f"[BLESS] {message}")


# go up a folder and import bless


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


def build_collision_filter(obj):
    collision_systems = []
    collide_with_systems = []

    # Debug print
    bless_print(f"Building collision filter for object: {obj.name}")

    # Get the layers that are enabled
    for i in range(1, 33):
        layer_name = f"layer_{i}"

        # Debug prints
        layer_enabled = getattr(obj.collision_layers, layer_name, False)
        mask_enabled = getattr(obj.collision_mask, layer_name, False)
        bless_print(f"Layer {i}: layer={layer_enabled}, mask={mask_enabled}")

        # Only add if explicitly True
        if layer_enabled is True:  # Explicit True check
            collision_systems.append(f"Layer {i}")
        if mask_enabled is True:   # Explicit True check
            collide_with_systems.append(f"Layer {i}")

    # Debug print
    bless_print(f"Collision systems: {collision_systems}")
    bless_print(f"Collide with systems: {collide_with_systems}")

    # Only create filter if there are actually enabled layers
    if collision_systems or collide_with_systems:
        filter_data = {}
        if collision_systems:
            filter_data["collisionSystems"] = collision_systems
        if collide_with_systems:
            filter_data["collideWithSystems"] = collide_with_systems
        return filter_data

    return None
