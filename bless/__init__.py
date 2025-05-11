

from .modules.ALXAddonUpdater.ALXAddonUpdater.ALX_AddonUpdater import \
    ALX_Addon_Updater
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


module_loader = ALX_Module_Manager(ADDON_PATH, globals())
addon_updater = ALX_Addon_Updater(ADDON_PATH[0], bl_info, "Github", "gd-3d", "bless", "https://github.com/gd-3d/bless/releases/")


def register():
    module_loader.developer_register_modules(mute=True)
    addon_updater.register_addon_updater(mute=True)


def unregister():
    module_loader.developer_unregister_modules()
    addon_updater.unregister_addon_updater()


if __name__ == "__main__":
    register()
