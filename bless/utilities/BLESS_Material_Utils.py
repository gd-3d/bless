import os

import bpy


def create_materials_from_textures(texture_paths, standard_texture_channels):
    # Group textures by their common prefix
    material_groups = {}
    for texture_path in texture_paths:
        # Extract the common prefix
        prefix = "_".join(os.path.basename(texture_path).split("_")[:-1])
        if prefix not in material_groups:
            material_groups[prefix] = []
        material_groups[prefix].append(texture_path)

    # Create materials for each group
    for prefix, textures in material_groups.items():
        # Create a new material
        material = bpy.data.materials.new(name=prefix)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Add Principled BSDF and Material Output nodes
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (400, 0)
        bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_node.location = (0, 0)
        links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

        BASE_X = -400
        BASE_Y = 0
        Y_OFFSET = -300  # Space between nodes vertically
        X_OFFSET = 350  # Space between nodes horizontally
        NODE_POSITIONS = {}  # Keep track of positions for each channel type

        for texture_path in textures:
            # Determine the channel type
            channel = os.path.basename(texture_path).split("_")[-1].split(".")[0].lower()
            for channel_type, aliases in standard_texture_channels.items():
                if channel in aliases:
                    if channel_type not in {"albedo", "metallic", "roughness", "normal", "emission"}:
                        # Skip unsupported channel types
                        continue

                    # Add image texture node
                    img_node = nodes.new(type='ShaderNodeTexImage')
                    img_node.name = channel_type
                    # Set location based on channel type
                    if channel_type not in NODE_POSITIONS:
                        NODE_POSITIONS[channel_type] = BASE_Y
                        BASE_Y += Y_OFFSET
                    img_node.location = (BASE_X, NODE_POSITIONS[channel_type])

                    img_node.image = bpy.data.images.load(texture_path)

                    # Horizontal offset for additional nodes
                    current_x = BASE_X + X_OFFSET

                    # Connect to the appropriate input on the BSDF node
                    if channel_type == "albedo":
                        links.new(img_node.outputs["Color"], bsdf_node.inputs["Base Color"])

                    elif channel_type == "metallic":
                        links.new(img_node.outputs["Color"], bsdf_node.inputs["Metallic"])

                    elif channel_type == "roughness":
                        links.new(img_node.outputs["Color"], bsdf_node.inputs["Roughness"])

                    elif channel_type == "normal":
                        normal_map_node = nodes.new(type='ShaderNodeNormalMap')
                        normal_map_node.location = (current_x, NODE_POSITIONS[channel_type])
                        links.new(img_node.outputs["Color"], normal_map_node.inputs["Color"])
                        links.new(normal_map_node.outputs["Normal"], bsdf_node.inputs["Normal"])

                    elif channel_type == "emission":
                        links.new(img_node.outputs["Color"], bsdf_node.inputs["Emission"])

                    break
