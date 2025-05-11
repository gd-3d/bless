import os
import re

import bpy

from .ALX_AddonUpdaterEngine import AddonUpdaterEngine
from .ALX_AddonUpdaterUtils import get_addon_preferences, ui_refresh

addon_updater: AddonUpdaterEngine = None
addon_name = re.sub(r"\\|\/|-|\.", "_", str.lower(__package__).split(".")[0])


class AddonUpdaterCheckNow(bpy.types.Operator):
    bl_label = f"Check now for {addon_name} update"
    bl_idname = f"{addon_name}.updater_check_now"
    bl_description = f"Check now for an update to the {addon_name} addon"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        if addon_updater.invalid_updater:
            print(f"{addon_name} invalid updater")
            return {'CANCELLED'}

        if addon_updater.async_checking and addon_updater.error is None:
            print(f"{addon_name} updater async")
            # Check already happened.
            # Used here to just avoid constant applying settings below.
            # Ignoring if error, to prevent being stuck on the error screen.
            return {'CANCELLED'}

        # apply the UI settings
        settings = get_addon_preferences(context, addon_updater.addon_name)
        if settings is None:
            addon_updater.print_verbose(
                f"Could not get {__package__} preferences, update check skipped"
            )
            return {'CANCELLED'}

        addon_updater.set_check_interval(
            enabled=settings.auto_check_update,
            months=settings.updater_interval_months,
            days=settings.updater_interval_days,
            hours=settings.updater_interval_hours,
            minutes=settings.updater_interval_minutes)

        # Input is an optional callback function. This function should take a
        # bool input. If true: update ready, if false: no update ready.
        addon_updater.check_for_update_now(ui_refresh)

        return {'FINISHED'}


###


class AddonUpdaterUpdateTarget(bpy.types.Operator):
    bl_label = f"{addon_name} version target"
    bl_idname = f"{addon_name}.updater_update_target"
    bl_description = f"Install a targeted version of the {addon_name} addon"
    bl_options = {'REGISTER', 'INTERNAL'}

    def target_version(self, context):
        # In case of error importing updater.
        if addon_updater.invalid_updater:
            ret = []

        ret = []
        i = 0
        for tag in addon_updater.tags:
            ret.append((tag, tag, "Select to install " + tag))
            i += 1
        return ret

    target = bpy.props.EnumProperty(
        name="Target version to install",
        description="Select the version to install",
        items=target_version
    )

    # If true, run clean install - ie remove all files before adding new
    # equivalent to deleting the addon and reinstalling, except the
    # updater folder/backup folder remains.
    clean_install = bpy.props.BoolProperty(
        name="Clean install",
        description=("If enabled, completely clear the addon's folder before "
                     "installing new update, creating a fresh install"),
        default=False,
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        if addon_updater.invalid_updater:
            return False
        return addon_updater.update_ready is not None and len(addon_updater.tags) > 0

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if addon_updater.invalid_updater:
            layout.label(text="Updater error")
            return
        split = layout.split(factor=0.5)
        sub_col = split.column()
        sub_col.label(text="Select install version")
        sub_col = split.column()
        sub_col.prop(self, "target", text="")

    def execute(self, context):
        # In case of error importing updater.
        if addon_updater.invalid_updater:
            return {'CANCELLED'}

        res = addon_updater.run_update(
            force=False,
            revert_tag=self.target,
            callback=post_update_callback,
            clean=self.clean_install)

        # Should return 0, if not something happened.
        if res == 0:
            addon_updater.print_verbose("Updater returned successful")
        else:
            addon_updater.print_verbose(
                "Updater returned {}, , error occurred".format(res))
            return {'CANCELLED'}

        return {'FINISHED'}


class AddonUpdaterInstallManually(bpy.types.Operator):
    """As a fallback, direct the user to download the addon manually"""
    bl_label = "Install update manually"
    bl_idname = f"{addon_name}.updater_install_manually"
    bl_description = "Proceed to manually install update"
    bl_options = {'REGISTER', 'INTERNAL'}

    error = bpy.props.StringProperty(
        name="Error Occurred",
        default="",
        options={'HIDDEN'}
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout

        if addon_updater.invalid_updater:
            layout.label(text="Updater error")
            return

        # Display error if a prior autoamted install failed.
        if self.error != "":
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="There was an issue trying to auto-install",
                      icon="ERROR")
            col.label(text="Press the download button below and install",
                      icon="BLANK1")
            col.label(text="the zip file like a normal addon.", icon="BLANK1")
        else:
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="Install the addon manually")
            col.label(text="Press the download button below and install")
            col.label(text="the zip file like a normal addon.")

        # If check hasn't happened, i.e. accidentally called this menu,
        # allow to check here.

        row = layout.row()

        if addon_updater.update_link is not None:
            row.operator(
                "wm.url_open",
                text="Direct download").url = addon_updater.update_link
        else:
            row.operator(
                "wm.url_open",
                text="(failed to retrieve direct download)")
            row.enabled = False

            if addon_updater.manual_download_website is not None:
                row = layout.row()
                ops = row.operator("wm.url_open", text="Open website")
                ops.url = addon_updater.manual_download_website
            else:
                row = layout.row()
                row.label(text="See source website to download the update")

    def execute(self, context):
        return {'FINISHED'}


class AddonUpdaterUpdatedSuccessful(bpy.types.Operator):
    """Addon in place, popup telling user it completed or what went wrong"""
    bl_label = "Installation Report"
    bl_idname = f"{addon_name}.updater_update_successful"
    bl_description = "Update installation response"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    error = bpy.props.StringProperty(
        name="Error Occurred",
        default="",
        options={'HIDDEN'}
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)

    def draw(self, context):
        layout = self.layout

        if addon_updater.invalid_updater:
            layout.label(text="Updater error")
            return

        saved = addon_updater.json
        if self.error != "":
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="Error occurred, did not install", icon="ERROR")
            if addon_updater.error_msg:
                msg = addon_updater.error_msg
            else:
                msg = self.error
            col.label(text=str(msg), icon="BLANK1")
            rw = col.row()
            rw.scale_y = 2
            rw.operator(
                "wm.url_open",
                text="Click for manual download.",
                icon="BLANK1").url = addon_updater.manual_download_website
        elif not addon_updater.auto_reload_post_update:
            # Tell user to restart blender after an update/restore!
            if "just_restored" in saved and saved["just_restored"]:
                col = layout.column()
                col.label(text="Addon restored", icon="RECOVER_LAST")
                alert_row = col.row()
                alert_row.alert = True
                alert_row.operator(
                    "wm.quit_blender",
                    text="Restart blender to reload",
                    icon="BLANK1")
                addon_updater.json_reset_restore()
            else:
                col = layout.column()
                col.label(
                    text="Addon successfully installed", icon="FILE_TICK")
                alert_row = col.row()
                alert_row.alert = True
                alert_row.operator(
                    "wm.quit_blender",
                    text="Restart blender to reload",
                    icon="BLANK1")

        else:
            # reload addon, but still recommend they restart blender
            if "just_restored" in saved and saved["just_restored"]:
                col = layout.column()
                col.scale_y = 0.7
                col.label(text="Addon restored", icon="RECOVER_LAST")
                col.label(
                    text="Consider restarting blender to fully reload.",
                    icon="BLANK1")
                addon_updater.json_reset_restore()
            else:
                col = layout.column()
                col.scale_y = 0.7
                col.label(
                    text="Addon successfully installed", icon="FILE_TICK")
                col.label(
                    text="Consider restarting blender to fully reload.",
                    icon="BLANK1")

    def execute(self, context):
        return {'FINISHED'}


class AddonUpdaterRestoreBackup(bpy.types.Operator):
    """Restore addon from backup"""
    bl_label = "Restore backup"
    bl_idname = f"{addon_name}.updater_restore_backup"
    bl_description = "Restore addon from backup"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        try:
            return os.path.isdir(os.path.join(addon_updater.stage_path, "backup"))
        except:
            return False

    def execute(self, context):
        # in case of error importing updater
        if addon_updater.invalid_updater:
            return {'CANCELLED'}
        addon_updater.restore_backup()
        return {'FINISHED'}


class AddonUpdaterIgnore(bpy.types.Operator):
    """Ignore update to prevent future popups"""
    bl_label = "Ignore update"
    bl_idname = f"{addon_name}.updater_ignore"
    bl_description = "Ignore update to prevent future popups"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if addon_updater.invalid_updater:
            return False
        elif addon_updater.update_ready:
            return True
        else:
            return False

    def execute(self, context):
        # in case of error importing updater
        if addon_updater.invalid_updater:
            return {'CANCELLED'}
        addon_updater.ignore_update()
        self.report({"INFO"}, "Open addon preferences for updater options")
        return {'FINISHED'}


class AddonUpdaterEndBackground(bpy.types.Operator):
    """Stop checking for update in the background"""
    bl_label = "End background check"
    bl_idname = f"{addon_name}.end_background_check"
    bl_description = "Stop checking for update in the background"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        # in case of error importing updater
        if addon_updater.invalid_updater:
            return {'CANCELLED'}
        addon_updater.stop_async_check_update()
        return {'FINISHED'}


class AddonUpdaterInstallPopup(bpy.types.Operator):
    """Check and install update if available"""
    bl_label = f"Update {addon_name} addon"
    bl_idname = f"{addon_name}.updater_install_popup"
    bl_description = "Popup to check and display current updates available"
    bl_options = {'REGISTER', 'INTERNAL'}

    # if true, run clean install - ie remove all files before adding new
    # equivalent to deleting the addon and reinstalling, except the
    # updater folder/backup folder remains
    clean_install = bpy.props.BoolProperty(
        name="Clean install",
        description=("If enabled, completely clear the addon's folder before "
                     "installing new update, creating a fresh install"),
        default=False,
        options={'HIDDEN'}
    )

    ignore_enum = bpy.props.EnumProperty(
        name="Process update",
        description="Decide to install, ignore, or defer new addon update",
        items=[
            ("install", "Update Now", "Install update now"),
            ("ignore", "Ignore", "Ignore this update to prevent future popups"),
            ("defer", "Defer", "Defer choice till next blender session")
        ],
        options={'HIDDEN'}
    )

    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if addon_updater.invalid_updater:
            layout.label(text="Updater module error")
            return
        elif addon_updater.update_ready:
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="Update {} ready!".format(addon_updater.update_version),
                      icon="LOOP_FORWARDS")
            col.label(text="Choose 'Update Now' & press OK to install, ",
                      icon="BLANK1")
            col.label(text="or click outside window to defer", icon="BLANK1")
            row = col.row()
            row.prop(self, "ignore_enum", expand=True)
            col.split()
        elif not addon_updater.update_ready:
            col = layout.column()
            col.scale_y = 0.7
            col.label(text="No updates available")
            col.label(text="Press okay to dismiss dialog")
            # add option to force install
        else:
            # Case: updater.update_ready = None
            # we have not yet checked for the update.
            layout.label(text="Check for update now?")

        # Potentially in future, UI to 'check to select/revert to old version'.

    def execute(self, context):
        # In case of error importing updater.
        if addon_updater.invalid_updater:
            return {'CANCELLED'}

        if addon_updater.manual_only:
            bpy.ops.wm.url_open(url=addon_updater.manual_download_website)
        elif addon_updater.update_ready:

            # Action based on enum selection.
            if self.ignore_enum == 'defer':
                return {'FINISHED'}
            elif self.ignore_enum == 'ignore':
                addon_updater.ignore_update()
                return {'FINISHED'}

            res = addon_updater.run_update(force=False,
                                           callback=post_update_callback,
                                           clean=self.clean_install)

            # Should return 0, if not something happened.
            if addon_updater.verbose:
                if res == 0:
                    print("Updater returned successful")
                else:
                    print("Updater returned {}, error occurred".format(res))
        elif addon_updater.update_ready is None:
            _ = addon_updater.check_for_update(now=True)

            # Re-launch this dialog.
            atr = AddonUpdaterInstallPopup.bl_idname.split(".")
            getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')
        else:
            addon_updater.print_verbose("Doing nothing, not ready for update")
        return {'FINISHED'}


class AddonUpdaterUpdateNow(bpy.types.Operator):
    bl_label = f"Update {addon_name} addon now"
    bl_idname = f"{addon_name}.updater_update_now"
    bl_description = f"Update to the latest version of the {addon_name} addon"
    bl_options = {'REGISTER', 'INTERNAL'}

    # If true, run clean install - ie remove all files before adding new
    # equivalent to deleting the addon and reinstalling, except the updater
    # folder/backup folder remains.
    clean_install = bpy.props.BoolProperty(
        name="Clean install",
        description=("If enabled, completely clear the addon's folder before "
                     "installing new update, creating a fresh install"),
        default=False,
        options={'HIDDEN'}
    )

    def execute(self, context):

        # in case of error importing updater
        if addon_updater.invalid_updater:
            return {'CANCELLED'}

        if addon_updater.manual_only:
            bpy.ops.wm.url_open(url=addon_updater.manual_download_website)
        if addon_updater.update_ready:
            # if it fails, offer to open the website instead
            try:
                res = addon_updater.run_update(force=False,
                                               callback=post_update_callback,
                                               clean=self.clean_install)

                # Should return 0, if not something happened.
                if addon_updater.verbose:
                    if res == 0:
                        print("Updater returned successful")
                    else:
                        print("Updater error response: {}".format(res))
            except Exception as expt:
                addon_updater._error = "Error trying to run update"
                addon_updater._error_msg = str(expt)
                addon_updater.print_trace()
                atr = AddonUpdaterInstallManually.bl_idname.split(".")
                getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')
        elif addon_updater.update_ready is None:
            (update_ready, version, link) = addon_updater.check_for_update(now=True)
            # Re-launch this dialog.
            atr = AddonUpdaterInstallPopup.bl_idname.split(".")
            getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')

        elif not addon_updater.update_ready:
            self.report({'INFO'}, "Nothing to update")
            return {'CANCELLED'}
        else:
            self.report(
                {'ERROR'}, "Encountered a problem while trying to update")
            return {'CANCELLED'}

        return {'FINISHED'}


def post_update_callback(module_name, res=None):
    """Callback for once the run_update function has completed.

    Only makes sense to use this if "auto_reload_post_update" == False,
    i.e. don't auto-restart the addon.

    Arguments:
        module_name: returns the module name from updater, but unused here.
        res: If an error occurred, this is the detail string.
    """

    # In case of error importing updater.
    if addon_updater.invalid_updater:
        return

    if res is None:
        # This is the same code as in conditional at the end of the register
        # function, ie if "auto_reload_post_update" == True, skip code.
        addon_updater.print_verbose(
            "{} updater: Running post update callback".format(addon_updater.addon_name))

        atr = AddonUpdaterUpdatedSuccessful.bl_idname.split(".")
        getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT')
        global ran_update_success_popup
        ran_update_success_popup = True
    else:
        # Some kind of error occurred and it was unable to install, offer
        # manual download instead.
        atr = AddonUpdaterUpdatedSuccessful.bl_idname.split(".")
        getattr(getattr(bpy.ops, atr[0]), atr[1])('INVOKE_DEFAULT', error=res)
    return
