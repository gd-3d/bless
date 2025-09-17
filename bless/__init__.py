import bpy

from .BLESS_Properties import (BLESS_PG_ObjectCollisionSettings,
                               BLESS_PG_SessionProperties)
from .gltf.BLESS_gltf import BLESS_GLTF
from .gltf.BLESS_gltf_definitions import OMIPhysicsBody, OMIPhysicsShape
from .modules.ALXAddonUpdater.ALXAddonUpdater.ALX_AddonUpdater import \
    Alx_Addon_Updater
from .modules.ALXModuleManager.ALXModuleManager.ALX_ModuleManager import \
    Alx_Module_Manager
from .user_interface.BLESS_Object_Data_UIPresets import \
    UIPreset_ObjectDataSheet

bl_info = {
    "name": "Bless",
    "author": "michaeljared, aaronfranke, yankscally, valerie-bosco",
    "description": "",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "",
    "warning": "",
    "category": "Generic",
    "doc_url": "https://github.com/gd-3d/bless/wiki",
    "tracker_url": "https://github.com/gd-3d/bless/issues",
}


module_loader = Alx_Module_Manager(
    path=__path__,
    globals=globals(),
    mute=True
)
addon_updater = Alx_Addon_Updater(
    path=__path__,
    bl_info=bl_info,
    engine="Github",
    engine_user_name="gd-3d",
    engine_repo_name="bless",
    manual_download_website="https://github.com/gd-3d/bless/releases/"
)


# [REQUIRED] Interface class for GLTF
class glTF2ExportUserExtension(BLESS_GLTF):

    def __init__(self):
        super.__init__()

    def gather_gltf_extensions_hook(self, gltf_plan, export_settings):
        return super().gather_gltf_extensions_hook(gltf_plan, export_settings)

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        return super().gather_node_hook(gltf2_object, blender_object, export_settings)


def Properties_Register():
    # persistent-session bless properties
    try:
        bpy.utils.register_class(BLESS_PG_SessionProperties)
    except:
        pass

    bpy.types.WindowManager.bless_session_properties = bpy.props.PointerProperty(type=BLESS_PG_SessionProperties)

    # bpy.types.WindowManager.bless_tools = bpy.props.PointerProperty(type=BlessTools)

    # object properties
    try:
        bpy.utils.register_class(OMIPhysicsBody)
        bpy.utils.register_class(OMIPhysicsShape)
        bpy.utils.register_class(BLESS_PG_ObjectCollisionSettings)
    except:
        pass

    bpy.types.Object.body_properties = bpy.props.PointerProperty(type=OMIPhysicsBody)
    bpy.types.Object.shape_properties = bpy.props.PointerProperty(type=OMIPhysicsShape)

    bpy.types.Object.bless_object_collision_settings = bpy.props.PointerProperty(type=BLESS_PG_ObjectCollisionSettings)

    # Add default bless_class property
    # bpy.types.Object.bless_class = bpy.props.EnumProperty(
    #     name="Godot Class",
    #     description="Select Godot class for this object",
    #     items=[("NONE", "None", "No Godot class assigned")],
    #     default="NONE"
    # )


def Properties_Unregister():
    # persistent-session bless properties
    try:
        bpy.utils.unregister_class(BLESS_PG_SessionProperties)
    except:
        pass
    del bpy.types.WindowManager.bless_session_properties

    # object properties
    try:
        bpy.utils.unregister_class(OMIPhysicsBody)
        bpy.utils.unregister_class(OMIPhysicsShape)
        bpy.utils.unregister_class(BLESS_PG_ObjectCollisionSettings)
    except:
        pass
    del bpy.types.Object.body_properties
    del bpy.types.Object.shape_properties
    del bpy.types.Object.bless_object_collision_settings

    # del bpy.types.Object.bless_class

    # del bpy.types.WindowManager.bless_tools


def UI_Load():
    # bpy.types.VIEW3D_PT_active_tool_duplicate.prepend(UIPreset_ToolBox)
    bpy.types.OBJECT_PT_context_object.prepend(UIPreset_ObjectDataSheet)


def UI_Unload():
    # bpy.types.VIEW3D_PT_active_tool_duplicate.remove(UIPreset_ToolBox)
    bpy.types.OBJECT_PT_context_object.remove(UIPreset_ObjectDataSheet)


def register():
    Properties_Register()
    module_loader.developer_load_resources(
        [
            {
                "name": "discord_icon",
                "path": "resources\\icons\\discord_icon_white.png",
                "resource_type": "IMAGE"
            }
        ]
    )

    module_loader.developer_register_modules()
    addon_updater.register_addon_updater(mute=True)

    UI_Load()

    bpy.context.preferences.use_preferences_save = True


def unregister():
    Properties_Unregister()
    UI_Unload()

    module_loader.developer_unregister_modules()
    addon_updater.unregister_addon_updater()


if __name__ == "__main__":
    register()
