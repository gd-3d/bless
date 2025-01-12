import os
from contextlib import redirect_stdout
from typing import Optional

import bpy
from bpy.app.handlers import persistent

from . import addon_updater_operators
from .addon_updater_engine import AddonUpdaterEngine
from .addon_updater_operators import (AddonUpdaterCheckNow,
                                      AddonUpdaterEndBackground,
                                      AddonUpdaterIgnore,
                                      AddonUpdaterInstallManually,
                                      AddonUpdaterInstallPopup,
                                      AddonUpdaterRestoreBackup,
                                      AddonUpdaterUpdatedSuccessful,
                                      AddonUpdaterUpdateNow,
                                      AddonUpdaterUpdateTarget)
from .addon_updater_utils import get_addon_preferences

addon_updater = AddonUpdaterEngine()
addon_updater_operators.addon_updater = addon_updater


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
                    addon_updater.addon))
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
    settings = get_addon_preferences(bpy.context)
    if not settings:
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
        col.operator("wm.url_open", text="Open website").url = addon_updater.website
        # ops = col.operator("wm.url_open",text="Direct download")
        # ops.url=updater.update_link
        col.operator(AddonUpdaterInstallManually.bl_idname,
                     text="Install manually")
    else:
        # ops = col.operator("wm.url_open", text="Direct download")
        # ops.url=updater.update_link
        col.operator("wm.url_open", text="Get it now").url = addon_updater.website


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
        col.operator("wm.url_open", text=dl_txt).url = addon_updater.website
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


# class SingletonUpdaterNone(object):
#     """Fake, bare minimum fields and functions for the updater object."""

#     def __init__(self):
#         self.invalid_updater = True  # Used to distinguish bad install.

#         self.addon = None
#         self.verbose = False
#         self.use_print_traces = True
#         self.error = None
#         self.error_msg = None
#         self.async_checking = None

#     def clear_state(self):
#         self.addon = None
#         self.verbose = False
#         self.invalid_updater = True
#         self.error = None
#         self.error_msg = None
#         self.async_checking = None

#     def run_update(self, force, callback, clean):
#         pass

#     def check_for_update(self, now):
#         pass

# updater = SingletonUpdaterNone()
# updater.error = "Error initializing updater module"
# updater.error_msg = str(e)

# Must declare this before classes are loaded, otherwise the bl_idname's will
# not match and have errors. Must be all lowercase and no spaces! Should also
# be unique among any other addons that could exist (using this updater code),
# to avoid clashes in operator registration.
# updater.addon = ""


# -----------------------------------------------------------------------------
# Updater operators
# -----------------------------------------------------------------------------


def update_settings_ui(context: bpy.types, layout=bpy.types.UILayout):
    """"""

    box = layout.box()

    if addon_updater.invalid_updater:
        box.label(text="Error initializing updater code:")
        box.label(text=addon_updater.error_msg)
        return
    settings = get_addon_preferences(context, addon_updater.addon)
    if not settings:
        box.label(text="Error getting updater preferences", icon='ERROR')
        return

    box.label(text="Updater Settings")
    row = box.row()

    # special case to tell user to restart blender, if set that way
    if not addon_updater.auto_reload_post_update:
        saved_state = addon_updater.json
        if "just_updated" in saved_state and saved_state["just_updated"]:
            row.alert = True
            row.operator("wm.quit_blender",
                         text="Restart blender to complete update",
                         icon="ERROR")
            return

    split = row.split(factor=0.4)
    sub_col = split.column()
    sub_col.prop(settings, "auto_check_update")
    sub_col = split.column()

    if not settings.auto_check_update:
        sub_col.enabled = False
    sub_row = sub_col.row()
    sub_row.label(text="Interval between checks")
    sub_row = sub_col.row(align=True)
    check_col = sub_row.column(align=True)
    check_col.prop(settings, "updater_interval_months")
    check_col = sub_row.column(align=True)
    check_col.prop(settings, "updater_interval_days")
    check_col = sub_row.column(align=True)

    # Consider un-commenting for local dev (e.g. to set shorter intervals)
    # check_col.prop(settings,"updater_interval_hours")
    # check_col = sub_row.column(align=True)
    # check_col.prop(settings,"updater_interval_minutes")

    # Checking / managing updates.
    row = box.row()
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
    elif addon_updater.update_ready is None:  # async is running
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
        update_now_txt = "Update directly to {}".format(
            addon_updater.include_branch_list[0])
        split.operator(AddonUpdaterUpdateNow.bl_idname, text=update_now_txt)
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
        dl_now_txt = "Download " + str(addon_updater.update_version)
        col.operator("wm.url_open",
                     text=dl_now_txt).url = addon_updater.website
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

    if not addon_updater.manual_only:
        col = row.column(align=True)
        if addon_updater.include_branches and len(addon_updater.include_branch_list) > 0:
            branch = addon_updater.include_branch_list[0]
            col.operator(AddonUpdaterUpdateTarget.bl_idname,
                         text="Install {} / old version".format(branch))
        else:
            col.operator(AddonUpdaterUpdateTarget.bl_idname,
                         text="(Re)install addon version")
        last_date = "none found"
        backup_path = os.path.join(addon_updater.stage_path, "backup")
        if "backup_date" in addon_updater.json and os.path.isdir(backup_path):
            if addon_updater.json["backup_date"] == "":
                last_date = "Date not found"
            else:
                last_date = addon_updater.json["backup_date"]
        backup_text = "Restore addon backup ({})".format(last_date)
        col.operator(AddonUpdaterRestoreBackup.bl_idname, text=backup_text)

    row = box.row()
    row.scale_y = 0.7
    last_check = addon_updater.json["last_check"]
    if addon_updater.error is not None and addon_updater.error_msg is not None:
        row.label(text=addon_updater.error_msg)
    elif last_check:
        last_check = last_check[0: last_check.index(".")]
        row.label(text="Last update check: " + last_check)
    else:
        row.label(text="Last update check: Never")


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

    bl_info = None
    engine: str = "Github"
    engine_user_name: str = "Valerie-Bosco"
    engine_repo_name: str = "AlxOverHaul"
    manual_download_website: str = "https://github.com/Valerie-Bosco/AlxOverHaul/releases"

    __addon_minimum_update_version: Optional[tuple[int, int, int]] = None

    def __init__(self, path=None,
                 bl_info=None,
                 engine="Github", engine_user_name="", engine_repo_name="",
                 manual_download_website=""):

        if (self.__addon_minimum_update_version is None):
            self.__addon_minimum_update_version = bl_info["version"]

        self.bl_info = bl_info
        self.engine = engine
        self.engine_user_name = engine_user_name
        self.engine_repo_name = engine_repo_name

        self.init_updater()

    def init_updater(self):
        global addon_updater

        if addon_updater.error:
            print(f"Exiting updater registration, {addon_updater.error}")
            return
        addon_updater.clear_state()

        addon_updater.verbose = True
        addon_updater.use_print_traces = False

        # updater settings
        addon_updater.addon = self.bl_info["name"]
        addon_updater.current_version = self.bl_info["version"]

        addon_updater.engine = self.engine
        addon_updater.private_token = None

        addon_updater.user = self.engine_user_name
        addon_updater.repo = self.engine_repo_name

        addon_updater.website = self.manual_download_website

        addon_updater.backup_current = True

        addon_updater.remove_pre_update_patterns = ["*.py", "*.pyc"]
        addon_updater.overwrite_patterns = ["*.png", "*.jpg", "README.md", "LICENSE.txt"]
        addon_updater.backup_ignore_patterns = [".git", "__pycache__", "*.bat", ".gitignore", "*.exe"]

        addon_updater.show_popups = True

        addon_updater.include_branches = False
        addon_updater.include_branch_list = None
        addon_updater.use_releases = True

        addon_updater.fake_install = False
        addon_updater.manual_only = False

        addon_updater.version_min_update = (0, 0, 0)
        addon_updater.version_max_update = None

        addon_updater.auto_reload_post_update = False

        # updater.subfolder_path = ""
        # updater.set_check_interval(enabled=False, months=0, days=0, hours=0, minutes=2)
        # updater.updater_path = # set path of updater folder, by default:
        # 			/addons/{__package__}/{__package__}_updater

    # Function defined above, customize as appropriate per repository
    # updater.skip_tag = skip_tag_function  # min and max used in this function

    # # Function defined above, optionally customize as needed per repository.
    # updater.select_link = select_link_function

    # Special situation: we just updated the addon, show a popup to tell the
    # user it worked. Could enclosed in try/catch in case other issues arise.

    # self.__addon_minimum_update_version = None
    # self.__addon_maximum_update_version = None

    # self.__engine = engine
    # self.__engine_private_token = None
    # self.__engine_user_name = engine_user_name
    # self.__engine_repo_name = engine_repo_name

    # self.__manual_download_website = manual_download_website

    # self.__updater_data_path

    # self.__verbose = False
    # self.__backup_current = True

    # self.__backup_ignore_patterns = ["__pycache__"]
    # # self.backup_ignore_patterns = [".git", "__pycache__", "*.bat", ".gitignore", "*.exe"]

    # # updater.backup_ignore_patterns = [".git", "__pycache__", "*.bat", ".gitignore", "*.exe"]

    # updater.overwrite_patterns = ["*.png", "*.jpg", "README.md", "LICENSE.txt"]
    # updater.remove_pre_update_patterns = ["*.py", "*.pyc"]
    # updater.use_releases = True
    # updater.include_branches = False

    # def init_updater(self):
    #     updater = self.__internal_updater

    #     updater.addon = self.__addon_name
    #     updater.current_version = self.__addon_current_version
    #     updater.version_min_update = self.__addon_minimum_update_version
    #     updater.version_max_update = self.__addon_maximum_update_version

    #     updater.engine = self.__engine
    #     updater.user = self.__engine_user_name
    #     updater.repo = self.__engine_repo_name
    #     updater.private_token = self.__engine_private_token

    #     updater.website = self.__manual_download_website

    #     updater.subfolder_path = ""

    #     updater.verbose = False
    #     updater.show_popups = True
    #     updater.manual_only = False
    #     updater.fake_install = False
    #     updater.backup_current = True
    #     updater.overwrite_patterns = ["*.png", "*.jpg", "README.md", "LICENSE.txt"]
    #     updater.remove_pre_update_patterns = ["*.py", "*.pyc"]
    #     updater.backup_ignore_patterns = [".git", "__pycache__", "*.bat", ".gitignore", "*.exe"]
    #     updater.set_check_interval(enabled=False, months=0, days=1, hours=0, minutes=0)

    #     updater.use_releases = True
    #     updater.include_branches = False
    #     updater.include_branch_list = ['master']

    #     updater.auto_reload_post_update = True

    # def set_version_target(self, minimum_version: Optional[tuple[int, int, int]] = None, maximum_version: Optional[tuple[int, int, int]] = None):
    #     if (minimum_version is not None):
    #         self.__addon_minimum_update_version = minimum_version
    #     if (maximum_version is not None):
    #         self.__addon_maximum_update_version = maximum_version

    # def set_check_interval(self, enabled=False, months=0, days=0, hours=0, minutes=2):
    #     updater = self.__internal_updater
    #     updater.set_check_interval(enabled, months, days, hours, minutes)

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
