import os
from contextlib import redirect_stdout
from typing import Optional

import bpy
from bpy.app.handlers import persistent

from . import ALX_AddonUpdaterOperators
from .ALX_AddonUpdaterEngine import AddonUpdaterEngine
from .ALX_AddonUpdaterOperators import (AddonUpdaterCheckNow,
                                        AddonUpdaterEndBackground,
                                        AddonUpdaterIgnore,
                                        AddonUpdaterInstallManually,
                                        AddonUpdaterInstallPopup,
                                        AddonUpdaterRestoreBackup,
                                        AddonUpdaterUpdatedSuccessful,
                                        AddonUpdaterUpdateNow,
                                        AddonUpdaterUpdateTarget)
from .ALX_AddonUpdaterUtils import get_addon_preferences

addon_updater = AddonUpdaterEngine()
ALX_AddonUpdaterOperators.addon_updater = addon_updater


@persistent
def updater_run_install_popup_handler(scene):
    global ran_auto_check_install_popup
    ran_auto_check_install_popup = True
    addon_updater.print_verbose("Running the install popup handler.")

    # in case of error importing updater
    if addon_updater.invalid_updater:
        return

    try:
        if "scene_update_post" in dir(bpy.app.handlers):
            bpy.app.handlers.scene_update_post.remove(
                updater_run_install_popup_handler)
        else:
            bpy.app.handlers.depsgraph_update_post.remove(
                updater_run_install_popup_handler)
    except:
        pass

    if "ignore" in addon_updater.json and addon_updater.json["ignore"]:
        return  # Don't do popup if ignore pressed.
    elif "version_text" in addon_updater.json and addon_updater.json["version_text"].get("version"):
        version = addon_updater.json["version_text"]["version"]
        ver_tuple = addon_updater.version_tuple_from_text(version)

        if ver_tuple < addon_updater.current_version:
            # User probably manually installed to get the up to date addon
            # in here. Clear out the update flag using this function.
            addon_updater.print_verbose(
                "{} updater: appears user updated, clearing flag".format(
                    addon_updater.addon_name))
            addon_updater.json_reset_restore()
            return
    atr = AddonUpdaterInstallPopup.bl_idname.split(".")
    getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')


def background_update_callback(update_ready):
    """Passed into the updater, background thread updater"""
    global ran_auto_check_install_popup
    addon_updater.print_verbose("Running background update callback")

    # In case of error importing updater.
    if addon_updater.invalid_updater:
        return
    if not addon_updater.show_popups:
        return
    if not update_ready:
        return

    # See if we need add to the update handler to trigger the popup.
    handlers = []
    if "scene_update_post" in dir(bpy.app.handlers):  # 2.7x
        handlers = bpy.app.handlers.scene_update_post
    else:  # 2.8+
        handlers = bpy.app.handlers.depsgraph_update_post
    in_handles = updater_run_install_popup_handler in handlers

    if in_handles or ran_auto_check_install_popup:
        return

    if "scene_update_post" in dir(bpy.app.handlers):  # 2.7x
        bpy.app.handlers.scene_update_post.append(
            updater_run_install_popup_handler)
    else:  # 2.8+
        bpy.app.handlers.depsgraph_update_post.append(
            updater_run_install_popup_handler)
    ran_auto_check_install_popup = True
    addon_updater.print_verbose("Attempted popup prompt")


def check_for_update_background():
    """Function for asynchronous background check.

    *Could* be called on register, but would be bad practice as the bare
    minimum code should run at the moment of registration (addon ticked).
    """
    if addon_updater.invalid_updater:
        return
    global ran_background_check
    if ran_background_check:
        # Global var ensures check only happens once.
        return
    elif addon_updater.update_ready is not None or addon_updater.async_checking:
        # Check already happened.
        # Used here to just avoid constant applying settings below.
        return

    # Apply the UI settings.
    settings = get_addon_preferences(bpy.context, addon_updater.addon_name)
    if (settings is None):
        return
    addon_updater.set_check_interval(enabled=settings.auto_check_update,
                                     months=settings.updater_interval_months,
                                     days=settings.updater_interval_days,
                                     hours=settings.updater_interval_hours,
                                     minutes=settings.updater_interval_minutes)

    # Input is an optional callback function. This function should take a bool
    # input, if true: update ready, if false: no update ready.
    addon_updater.check_for_update_async(background_update_callback)
    ran_background_check = True


def check_for_update_nonthreaded(self, context):
    """Can be placed in front of other operators to launch when pressed"""
    if addon_updater.invalid_updater:
        return

    # Only check if it's ready, ie after the time interval specified should
    # be the async wrapper call here.
    settings = get_addon_preferences(bpy.context)
    if not settings:
        if addon_updater.verbose:
            print("Could not get {} preferences, update check skipped".format(
                __package__))
        return
    addon_updater.set_check_interval(enabled=settings.auto_check_update,
                                     months=settings.updater_interval_months,
                                     days=settings.updater_interval_days,
                                     hours=settings.updater_interval_hours,
                                     minutes=settings.updater_interval_minutes)

    (update_ready, version, link) = addon_updater.check_for_update(now=False)
    if update_ready:
        atr = AddonUpdaterInstallPopup.bl_idname.split(".")
        getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')
    else:
        addon_updater.print_verbose("No update ready")
        self.report({'INFO'}, "No update ready")


# -----------------------------------------------------------------------------
# Example UI integrations
# -----------------------------------------------------------------------------
def update_notice_box_ui(self, context):
    """Update notice draw, to add to the end or beginning of a panel.

    After a check for update has occurred, this function will draw a box
    saying an update is ready, and give a button for: update now, open website,
    or ignore popup. Ideal to be placed at the end / beginning of a panel.
    """

    if addon_updater.invalid_updater:
        return

    saved_state = addon_updater.json
    if not addon_updater.auto_reload_post_update:
        if "just_updated" in saved_state and saved_state["just_updated"]:
            layout = self.layout
            box = layout.box()
            col = box.column()
            alert_row = col.row()
            alert_row.alert = True
            alert_row.operator(
                "wm.quit_blender",
                text="Restart blender",
                icon="ERROR")
            col.label(text="to complete update")
            return

    # If user pressed ignore, don't draw the box.
    if "ignore" in addon_updater.json and addon_updater.json["ignore"]:
        return
    if not addon_updater.update_ready:
        return

    layout = self.layout
    box = layout.box()
    col = box.column(align=True)
    col.alert = True
    col.label(text="Update ready!", icon="ERROR")
    col.alert = False
    col.separator()
    row = col.row(align=True)
    split = row.split(align=True)
    colL = split.column(align=True)
    colL.scale_y = 1.5
    colL.operator(AddonUpdaterIgnore.bl_idname, icon="X", text="Ignore")
    colR = split.column(align=True)
    colR.scale_y = 1.5
    if not addon_updater.manual_only:
        colR.operator(AddonUpdaterUpdateNow.bl_idname,
                      text="Update", icon="LOOP_FORWARDS")
        col.operator("wm.url_open", text="Open website").url = addon_updater.manual_download_website
        # ops = col.operator("wm.url_open",text="Direct download")
        # ops.url=updater.update_link
        col.operator(AddonUpdaterInstallManually.bl_idname,
                     text="Install manually")
    else:
        # ops = col.operator("wm.url_open", text="Direct download")
        # ops.url=updater.update_link
        col.operator("wm.url_open", text="Get it now").url = addon_updater.manual_download_website


def update_settings_ui_condensed(self, context, element=None):
    """Preferences - Condensed drawing within preferences.

    Alternate draw for user preferences or other places, does not draw a box.
    """

    # Element is a UI element, such as layout, a row, column, or box.
    if element is None:
        element = self.layout
    row = element.row()

    # In case of error importing updater.
    if addon_updater.invalid_updater:
        row.label(text="Error initializing updater code:")
        row.label(text=addon_updater.error_msg)
        return
    settings = get_addon_preferences(context)
    if not settings:
        row.label(text="Error getting updater preferences", icon='ERROR')
        return

    # Special case to tell user to restart blender, if set that way.
    if not addon_updater.auto_reload_post_update:
        saved_state = addon_updater.json
        if "just_updated" in saved_state and saved_state["just_updated"]:
            row.alert = True  # mark red
            row.operator(
                "wm.quit_blender",
                text="Restart blender to complete update",
                icon="ERROR")
            return

    col = row.column()
    if addon_updater.error is not None:
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.scale_y = 2
        if "ssl" in addon_updater.error_msg.lower():
            split.enabled = True
            split.operator(AddonUpdaterInstallManually.bl_idname,
                           text=addon_updater.error)
        else:
            split.enabled = False
            split.operator(AddonUpdaterCheckNow.bl_idname,
                           text=addon_updater.error)
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    elif addon_updater.update_ready is None and not addon_updater.async_checking:
        col.scale_y = 2
        col.operator(AddonUpdaterCheckNow.bl_idname)
    elif addon_updater.update_ready is None:  # Async is running.
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.enabled = False
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname, text="Checking...")
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterEndBackground.bl_idname, text="", icon="X")

    elif addon_updater.include_branches and \
            len(addon_updater.tags) == len(addon_updater.include_branch_list) and not \
            addon_updater.manual_only:
        # No releases found, but still show the appropriate branch.
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.scale_y = 2
        now_txt = "Update directly to " + str(addon_updater.include_branch_list[0])
        split.operator(AddonUpdaterUpdateNow.bl_idname, text=now_txt)
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    elif addon_updater.update_ready and not addon_updater.manual_only:
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterUpdateNow.bl_idname,
                       text="Update now to " + str(addon_updater.update_version))
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    elif addon_updater.update_ready and addon_updater.manual_only:
        col.scale_y = 2
        dl_txt = "Download " + str(addon_updater.update_version)
        col.operator("wm.url_open", text=dl_txt).url = addon_updater.manual_download_website
    else:  # i.e. that updater.update_ready == False.
        sub_col = col.row(align=True)
        sub_col.scale_y = 1
        split = sub_col.split(align=True)
        split.enabled = False
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="Addon is up to date")
        split = sub_col.split(align=True)
        split.scale_y = 2
        split.operator(AddonUpdaterCheckNow.bl_idname,
                       text="", icon="FILE_REFRESH")

    row = element.row()
    row.prop(settings, "auto_check_update")

    row = element.row()
    row.scale_y = 0.7
    last_check = addon_updater.json["last_check"]
    if addon_updater.error is not None and addon_updater.error_msg is not None:
        row.label(text=addon_updater.error_msg)
    elif last_check != "" and last_check is not None:
        last_check = last_check[0: last_check.index(".")]
        row.label(text="Last check: " + last_check)
    else:
        row.label(text="Last check: Never")


def skip_tag_function(self, tag):
    """A global function for tag skipping.

    A way to filter which tags are displayed, e.g. to limit downgrading too
    long ago.

    Args:
        self: The instance of the singleton addon update.
        tag: the text content of a tag from the repo, e.g. "v1.2.3".

    Returns:
        bool: True to skip this tag name (ie don't allow for downloading this
            version), or False if the tag is allowed.
    """

    # In case of error importing updater.
    if self.invalid_updater:
        return False

    # ---- write any custom code here, return true to disallow version ---- #
    #
    # # Filter out e.g. if 'beta' is in name of release
    # if 'beta' in tag.lower():
    # 	return True
    # ---- write any custom code above, return true to disallow version --- #

    if self.include_branches:
        for branch in self.include_branch_list:
            if tag["name"].lower() == branch:
                return False

    # Function converting string to tuple, ignoring e.g. leading 'v'.
    # Be aware that this strips out other text that you might otherwise
    # want to be kept and accounted for when checking tags (e.g. v1.1a vs 1.1b)
    tupled = self.version_tuple_from_text(tag["name"])
    if not isinstance(tupled, tuple):
        return True

    # Select the min tag version - change tuple accordingly.
    if self.version_min_update is not None:
        if tupled < self.version_min_update:
            return True  # Skip if current version below this.

    # Select the max tag version.
    if self.version_max_update is not None:
        if tupled >= self.version_max_update:
            return True  # Skip if current version at or above this.

    # In all other cases, allow showing the tag for updating/reverting.
    # To simply and always show all tags, this return False could be moved
    # to the start of the function definition so all tags are allowed.
    return False


def select_link_function(self, tag):
    """Only customize if trying to leverage "attachments" in *GitHub* releases.

    A way to select from one or multiple attached downloadable files from the
    server, instead of downloading the default release/tag source code.
    """

    # -- Default, universal case (and is the only option for GitLab/Bitbucket)
    link = tag["zipball_url"]

    # -- Example: select the first (or only) asset instead source code --
    # if "assets" in tag and "browser_download_url" in tag["assets"][0]:
    # 	link = tag["assets"][0]["browser_download_url"]

    # -- Example: select asset based on OS, where multiple builds exist --
    # # not tested/no error checking, modify to fit your own needs!
    # # assume each release has three attached builds:
    # #		release_windows.zip, release_OSX.zip, release_linux.zip
    # # This also would logically not be used with "branches" enabled
    # if platform.system() == "Darwin": # ie OSX
    # 	link = [asset for asset in tag["assets"] if 'OSX' in asset][0]
    # elif platform.system() == "Windows":
    # 	link = [asset for asset in tag["assets"] if 'windows' in asset][0]
    # elif platform.system() == "Linux":
    # 	link = [asset for asset in tag["assets"] if 'linux' in asset][0]

    return link


# -----------------------------------------------------------------------------
# Updater operators
# -----------------------------------------------------------------------------
ran_auto_check_install_popup = False
ran_update_success_popup = False

ran_background_check = False


def make_annotations(cls):
    """Add annotation attribute to fields to avoid Blender 2.8+ warnings"""
    if not hasattr(bpy.app, "version") or bpy.app.version < (2, 80):
        return cls
    if bpy.app.version < (2, 93, 0):
        bl_props = {k: v for k, v in cls.__dict__.items()
                    if isinstance(v, tuple)}
    else:
        bl_props = {k: v for k, v in cls.__dict__.items()
                    if isinstance(v, bpy.props._PropertyDeferred)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


addon_updater_classes = (
    AddonUpdaterInstallPopup,
    AddonUpdaterCheckNow,
    AddonUpdaterUpdateNow,
    AddonUpdaterUpdateTarget,
    AddonUpdaterInstallManually,
    AddonUpdaterUpdatedSuccessful,
    AddonUpdaterRestoreBackup,
    AddonUpdaterIgnore,
    AddonUpdaterEndBackground
)


class Alx_Addon_Updater():
    """"""

    def __init__(self, path=None,
                 bl_info=None,
                 engine="Github", engine_user_name="", engine_repo_name="",
                 minimum_version: Optional[tuple[int, int, int]] = None,
                 maximum_version: Optional[tuple[int, int, int]] = None,
                 manual_download_website=""):

        if (addon_updater.error is not None):
            print(f"Exiting updater registration, {addon_updater.error}")
            return
        addon_updater.clear_state()

        addon_updater.addon_name = bl_info["name"]
        addon_updater.current_version = bl_info["version"]

        addon_updater.engine = engine
        addon_updater.private_token = None
        addon_updater.engine_user_name = engine_user_name
        addon_updater.engine_repo_name = engine_repo_name

        if (minimum_version is not None):
            addon_updater.version_min_update = minimum_version
        if (maximum_version is not None):
            addon_updater.version_max_update = maximum_version

        if (manual_download_website != ""):
            addon_updater.manual_download_website = manual_download_website

        addon_updater.show_popups = True

        addon_updater.backup_current = True

        addon_updater.manual_only = False

        addon_updater.include_branches = False
        addon_updater.include_branch_list = None
        addon_updater.use_releases = True

        addon_updater.remove_pre_update_patterns = ["*.py", "*.pyc"]
        addon_updater.overwrite_patterns = ["*.png", "*.jpg", "README.md", "LICENSE.txt"]
        addon_updater.backup_ignore_patterns = [".git", "__pycache__", "*.bat", ".gitignore", "*.exe"]

        addon_updater.auto_reload_post_update = True

        addon_updater.verbose = True
        addon_updater.use_print_traces = False
        addon_updater.fake_install = False

    def register_addon_updater(self, mute: Optional[bool] = True):
        global addon_updater_classes
        for addon_class in addon_updater_classes:
            try:
                if (mute):
                    with open(os.devnull, 'w') as print_discard_bin:
                        with redirect_stdout(print_discard_bin):
                            make_annotations(addon_class)
                            bpy.utils.register_class(addon_class)
                else:
                    make_annotations(addon_class)
                    bpy.utils.register_class(addon_class)

            except Exception as error:
                print(error)

    def unregister_addon_updater(self):

        for cls in addon_updater_classes:
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass

        addon_updater.clear_state()

        global ran_auto_check_install_popup
        ran_auto_check_install_popup = False

        global ran_update_success_popup
        ran_update_success_popup = False

        global ran_background_check
        ran_background_check = False
