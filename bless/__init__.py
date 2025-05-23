from .gltf.BLESS_gltf import BLESS_GLTF
from .modules.ALXAddonUpdater.ALXAddonUpdater.ALX_AddonUpdater import \
    Alx_Addon_Updater
from .modules.ALXModuleManager.ALXModuleManager.ALX_ModuleManager import \
    Alx_Module_Manager

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


def register():
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


def unregister():
    module_loader.developer_unregister_modules()
    addon_updater.unregister_addon_updater()


if __name__ == "__main__":
    register()
