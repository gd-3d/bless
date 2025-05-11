import os

import bpy

from .ALX_AddonUpdater import addon_updater
from .ALX_AddonUpdaterOperators import (AddonUpdaterCheckNow,
                                        AddonUpdaterEndBackground,
                                        AddonUpdaterInstallManually,
                                        AddonUpdaterRestoreBackup,
                                        AddonUpdaterUpdateNow,
                                        AddonUpdaterUpdateTarget)
from .ALX_AddonUpdaterUtils import get_addon_preferences


def update_settings_ui(context: bpy.types, layout=bpy.types.UILayout):
    settings = get_addon_preferences(context, addon_updater.addon_name)

    box: bpy.types.UILayout = layout.box()

    if (addon_updater.invalid_updater == False) and (settings is not None):
        box.label(text="Updater Settings")
        row = box.row()

        # Require Restart if auto reaload post update is off
        if (addon_updater.auto_reload_post_update == False):
            saved_state = addon_updater.json
            if ("just_updated" in saved_state) and (saved_state.get("just_updated")):
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
                         text=dl_now_txt).url = addon_updater.manual_download_website
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

    else:
        print("ERROR")
        if (addon_updater.invalid_updater == True):
            box.label(text="Error initializing updater code:")
            box.label(text=addon_updater.error_msg)
            return

        if (settings is None):
            box.label(text="Error getting updater preferences", icon='ERROR')
            return
