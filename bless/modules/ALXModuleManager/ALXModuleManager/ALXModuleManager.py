import os
from contextlib import redirect_stdout
from inspect import getmembers, isclass
from os import sep as os_separator
from pathlib import Path
from typing import Any, Optional

import bpy


class Alx_Module_Manager():

    __init_globals: dict[str, Any]

    __module_path: str = ""
    __module_folders: set[Path] = set()
    __module_files: dict[str, Path] = dict()
    __module_classes: set[str] = set()

    __folder_blacklist: set[str] = set()
    __file_blacklist: set[str] = set()

    __mute: bool = True

    def __init__(self, path: str, globals: dict[str, Any], mute: Optional[bool] = True):
        self.__mute = mute

        self.__folder_blacklist.update({"__pycache__"})
        self.__file_blacklist.update({"__init__"})

        self.__module_path = path[0]
        self.__init_globals = globals

    def developer_register_modules(self):
        self.__module_folders = self.__gather_addon_folders(self.__module_path, self.__folder_blacklist)
        self.__module_files = self.__gather_addon_files(self.__module_folders, self.__file_blacklist)
        self.__execute_locals_update(self.__module_path, self.__module_files)
        self.__module_classes = self.__gather_classes_from_files(self.__module_files)
        self.__register_addon_classes(self.__module_classes)

    def developer_unregister_modules(self):
        self.__unregister_addon_classes(self.__module_classes)

    def developer_blacklist_folder(self, folders: set[str]):
        self.__folder_blacklist.add(*folders)

    def developer_blacklist_file(self, files: set[str]):
        self.__file_blacklist.add(*files)

    def __gather_addon_folders(self, path: str, folder_blacklist: set[str] = {}):
        """
        IN path: __path__[0] from __init__ \n
        IN folder_blacklist: set[str] \n

        RETURN addon_folders: set[Path] \n
        """

        path_object: Path = Path(path)
        addon_folders: set[Path] = set()

        if (path_object.exists()) and (path_object.is_dir()):
            path_iter_queue: list[Path] = [path_object]

            for folder_path in path_iter_queue:
                if (folder_path.is_dir()) and (folder_path.exists()) and (folder_path not in addon_folders) and (folder_path.name not in folder_blacklist):
                    addon_folders.add(folder_path)

                    for subfolder_path in folder_path.iterdir():
                        if (subfolder_path.is_dir()) and (subfolder_path.exists()) and (subfolder_path not in addon_folders) and (subfolder_path.name not in folder_blacklist):
                            path_iter_queue.append(subfolder_path)
                            addon_folders.add(subfolder_path)

        return addon_folders

    def __gather_addon_files(self, folder_paths: set[Path], file_blacklist: set[str] = {}):
        """
        IN folder_paths: set[Path] \n
        IN file_blacklist: set[str] \n

        RETRUN addon_files: set[str] \n
        """

        addon_files: dict[str, Path] = dict()

        for folder_path in folder_paths:
            for file in folder_path.iterdir():
                if (file.is_file()) and (file.name not in file_blacklist) and (file.suffix == ".py"):
                    addon_files.update({file.name[0:-3]: folder_path})

        return addon_files

    def __gather_classes_from_files(self, addon_files: dict[str, Path] = None):
        addon_classes: set[str] = set()

        for file_name in addon_files.keys():
            if (file_name != __file__) and (file_name not in self.__file_blacklist):
                for addon_class in getmembers(eval(file_name, self.__init_globals), isclass):
                    addon_classes.add(addon_class[1])

        return addon_classes

    def __execute_locals_update(self, path: str, addon_files: dict[str, Path]):
        for file_name in addon_files.keys():
            if (file_name != __name__.split(".")[-1]) and (file_name not in self.__file_blacklist):
                try:
                    if ("importlib" not in self.__init_globals):
                        exec("import importlib", self.__init_globals)

                    if (file_name not in self.__init_globals):
                        relative_path = str(addon_files.get(file_name).relative_to(path)).replace(os_separator, ".")

                        import_line = f"from . {relative_path if relative_path != '.' else ''} import {file_name}"
                        exec(import_line, self.__init_globals)
                    else:
                        reload_line = f"{file_name} = importlib.reload({file_name})"
                        exec(reload_line, self.__init_globals)
                except Exception as error:
                    print(f"[{file_name}] {error}")

    def __register_addon_classes(self, addon_classes: list[object]):
        for addon_class in addon_classes:
            try:
                if (self.__mute):
                    with open(os.devnull, 'w') as print_discard_bin:
                        with redirect_stdout(print_discard_bin):
                            if ("WorkSpaceTool" in [base.__name__ for base in addon_class.__bases__]):
                                bpy.utils.register_tool(addon_class,
                                                        after=eval(addon_class.after, self.__init_globals),
                                                        separator=addon_class.separator,
                                                        group=addon_class.group)
                            else:
                                bpy.utils.register_class(addon_class)
                else:
                    if ("WorkSpaceTool" in [base.__name__ for base in addon_class.__bases__]):
                        bpy.utils.register_tool(addon_class,
                                                after=eval(addon_class.after, self.__init_globals),
                                                separator=addon_class.separator,
                                                group=addon_class.group)
                    else:
                        bpy.utils.register_class(addon_class)

            except Exception as error:
                if (self.__mute == False):
                    print(error)

    def __unregister_addon_classes(self, addon_classes: list[object]):
        for addon_class in addon_classes:
            try:
                if ("WorkSpaceTool" in [base.__name__ for base in addon_class.__bases__]):
                    bpy.utils.unregister_tool(addon_class)
                else:
                    bpy.utils.unregister_class(addon_class)

            except Exception as error:
                if (self.__mute == False):
                    print(error)
