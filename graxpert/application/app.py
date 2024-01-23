import logging
import os
import tkinter as tk
from tkinter import messagebox

import numpy as np
from appdirs import user_config_dir

from graxpert.ai_model_handling import ai_model_path_from_version, download_version, validate_local_version
from graxpert.app_state import INITIAL_STATE
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.astroimage import AstroImage
from graxpert.background_extraction import extract_background
from graxpert.commands import INIT_HANDLER, RESET_POINTS_HANDLER, RM_POINT_HANDLER, SEL_POINTS_HANDLER, Command
from graxpert.localization import _
from graxpert.mp_logging import logfile_name
from graxpert.preferences import fitsheader_2_app_state, load_preferences, prefs_2_app_state
from graxpert.stretch import stretch_all, StretchParameters
from graxpert.ui.loadingframe import DynamicProgressThread


class GraXpert:
    def __init__(self):
        self.initialize()

    def initialize(self):
        # app preferences
        prefs_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")
        self.prefs = load_preferences(prefs_filename)

        self.filename = ""
        self.data_type = ""

        self.images = {"Original": None, "Background": None, "Processed": None}
        self.display_type = "Original"

        self.mat_affine = np.eye(3)

        # state handling
        tmp_state = prefs_2_app_state(self.prefs, INITIAL_STATE)

        self.cmd: Command = Command(INIT_HANDLER, background_points=tmp_state.background_points)
        self.cmd.execute()

        # image loading
        eventbus.add_listener(AppEvents.OPEN_FILE_DIALOG_REQUEST, self.on_open_file_dialog_request)
        eventbus.add_listener(AppEvents.LOAD_IMAGE_REQUEST, self.on_load_image)
        # image display
        eventbus.add_listener(AppEvents.DISPLAY_TYPE_CHANGED, self.on_display_type_changed)
        # stretch options
        eventbus.add_listener(AppEvents.STRETCH_OPTION_CHANGED, self.on_stretch_option_changed)
        eventbus.add_listener(AppEvents.CHANGE_SATURATION_REQUEST, self.on_change_saturation_request)
        eventbus.add_listener(AppEvents.CHANNELS_LINKED_CHANGED, self.on_channels_linked_option_changed)
        # sample selection
        eventbus.add_listener(AppEvents.DISPLAY_PTS_CHANGED, self.on_display_pts_changed)
        eventbus.add_listener(AppEvents.BG_FLOOD_SELECTION_CHANGED, self.on_bg_floot_selection_changed)
        eventbus.add_listener(AppEvents.BG_PTS_CHANGED, self.on_bg_pts_changed)
        eventbus.add_listener(AppEvents.BG_TOL_CHANGED, self.on_bg_tol_changed)
        eventbus.add_listener(AppEvents.CREATE_GRID_REQUEST, self.on_create_grid_request)
        eventbus.add_listener(AppEvents.RESET_POITS_REQUEST, self.on_reset_points_request)
        # calculation
        eventbus.add_listener(AppEvents.INTERPOL_TYPE_CHANGED, self.on_interpol_type_changed)
        eventbus.add_listener(AppEvents.SMOTTHING_CHANGED, self.on_smoothing_changed)
        eventbus.add_listener(AppEvents.CALCULATE_REQUEST, self.on_calculate_request)
        # saving
        eventbus.add_listener(AppEvents.SAVE_AS_CHANGED, self.on_save_as_changed)
        eventbus.add_listener(AppEvents.SAVE_REQUEST, self.on_save_request)
        eventbus.add_listener(AppEvents.SAVE_BACKGROUND_REQUEST, self.on_save_background_request)
        eventbus.add_listener(AppEvents.SAVE_STRETCHED_REQUEST, self.on_save_stretched_request)
        # advanced settings
        eventbus.add_listener(AppEvents.SAMPLE_SIZE_CHANGED, self.on_sample_size_changed)
        eventbus.add_listener(AppEvents.SAMPLE_COLOR_CHANGED, self.on_sample_color_changed)
        eventbus.add_listener(AppEvents.RBF_KERNEL_CHANGED, self.on_rbf_kernel_changed)
        eventbus.add_listener(AppEvents.SPLINE_ORDER_CHANGED, self.on_spline_order_changed)
        eventbus.add_listener(AppEvents.CORRECTION_TYPE_CHANGED, self.on_correction_type_changed)
        eventbus.add_listener(AppEvents.LANGUAGE_CHANGED, self.on_language_selected)
        eventbus.add_listener(AppEvents.AI_VERSION_CHANGED, self.on_ai_version_changed)
        eventbus.add_listener(AppEvents.SCALING_CHANGED, self.on_scaling_changed)

    # event handling
    def on_ai_version_changed(self, event):
        self.prefs.ai_version = event["ai_version"]

    def on_bg_floot_selection_changed(self, event):
        self.prefs.bg_flood_selection_option = event["bg_flood_selection_option"]

    def on_bg_pts_changed(self, event):
        self.prefs.bg_pts_option = event["bg_pts_option"]

    def on_bg_tol_changed(self, event):
        self.prefs.bg_tol_option = event["bg_tol_option"]

    def on_calculate_request(self, event=None):
        if self.images["Original"] is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return

        background_points = self.cmd.app_state.background_points

        # Error messages if not enough points
        if len(background_points) == 0 and self.prefs.interpol_type_option != "AI":
            messagebox.showerror("Error", _("Please select background points with left click."))
            return

        if len(background_points) < 2 and self.prefs.interpol_type_option == "Kriging":
            messagebox.showerror("Error", _("Please select at least 2 background points with left click for the Kriging method."))
            return

        if len(background_points) < 16 and self.prefs.interpol_type_option == "Splines":
            messagebox.showerror("Error", _("Please select at least 16 background points with left click for the Splines method."))
            return

        if self.prefs.interpol_type_option == "AI":
            if not self.validate_ai_installation():
                return

        eventbus.emit(AppEvents.CALCULATE_BEGIN)

        progress = DynamicProgressThread(callback=lambda p: eventbus.emit(AppEvents.CALCULATE_PROGRESS, {"progress": p}))

        imarray = np.copy(self.images["Original"].img_array)

        downscale_factor = 1

        if self.prefs.interpol_type_option == "Kriging" or self.prefs.interpol_type_option == "RBF":
            downscale_factor = 4

        try:
            self.images["Background"] = AstroImage()
            self.images["Background"].set_from_array(
                extract_background(
                    imarray,
                    np.array(background_points),
                    self.prefs.interpol_type_option,
                    self.prefs.smoothing_option,
                    downscale_factor,
                    self.prefs.sample_size,
                    self.prefs.RBF_kernel,
                    self.prefs.spline_order,
                    self.prefs.corr_type,
                    ai_model_path_from_version(self.prefs.ai_version),
                    progress,
                )
            )

            self.images["Processed"] = AstroImage()
            self.images["Processed"].set_from_array(imarray)

            # Update fits header and metadata
            background_mean = np.mean(self.images["Background"].img_array)
            self.images["Processed"].update_fits_header(self.images["Original"].fits_header, background_mean, self.prefs, self.cmd.app_state)
            self.images["Background"].update_fits_header(self.images["Original"].fits_header, background_mean, self.prefs, self.cmd.app_state)

            self.images["Processed"].copy_metadata(self.images["Original"])
            self.images["Background"].copy_metadata(self.images["Original"])

            all_images = [self.images["Original"].img_array, self.images["Processed"].img_array, self.images["Background"].img_array]
            stretches = stretch_all(all_images, StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option))
            self.images["Original"].update_display_from_array(stretches[0], self.prefs.saturation)
            self.images["Processed"].update_display_from_array(stretches[1], self.prefs.saturation)
            self.images["Background"].update_display_from_array(stretches[2], self.prefs.saturation)

            # self.display_type = "Processed"
            eventbus.emit(AppEvents.UPDATE_DISPLAY_TYPE_REEQUEST, {"display_type": "Processed"})

        except Exception as e:
            logging.exception(e)
            eventbus.emit(AppEvents.CALCULATE_ERROR)
            messagebox.showerror("Error", _("An error occured during background calculation. Please see the log at {}.".format(logfile_name)))
        finally:
            progress.done_progress()
            eventbus.emit(AppEvents.CALCULATE_END)

    def on_change_saturation_request(self, event):
        self.prefs.saturation = event["saturation"]

        eventbus.emit(AppEvents.CHANGE_SATURATION_BEGIN)

        for img in self.images.values():
            if img is not None:
                img.update_saturation(self.prefs.saturation)

        eventbus.emit(AppEvents.CHANGE_SATURATION_END)

    def on_correction_type_changed(self, event):
        self.prefs.corr_type = event["corr_type"]

    def on_create_grid_request(self, event=None):
        if self.images["Original"] is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return

        eventbus.emit(AppEvents.CREATE_GRID_BEGIN)

        self.cmd = Command(SEL_POINTS_HANDLER, self.cmd, data=self.images["Original"].img_array, num_pts=self.prefs.bg_pts_option, tol=self.prefs.bg_tol_option, sample_size=self.prefs.sample_size)
        self.cmd.execute()

        eventbus.emit(AppEvents.CREATE_GRID_END)

    def on_display_pts_changed(self, event):
        self.prefs.display_pts = event["display_pts"]
        eventbus.emit(AppEvents.REDRAW_POINTS_REQUEST)

    def on_display_type_changed(self, event):
        self.display_type = event["display_type"]

        eventbus.emit(AppEvents.STRETCH_IMAGE_END)

    def on_interpol_type_changed(self, event):
        self.prefs.interpol_type_option = event["interpol_type_option"]

    def on_language_selected(self, event):
        self.prefs.lang = event["lang"]
        messagebox.showerror("", _("Please restart the program to change the language."))

    def on_load_image(self, event):
        eventbus.emit(AppEvents.LOAD_IMAGE_BEGIN)
        filename = event["filename"]
        self.display_type = "Original"

        try:
            image = AstroImage()
            image.set_from_file(filename, StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option), self.prefs.saturation)

        except Exception as e:
            eventbus.emit(AppEvents.LOAD_IMAGE_ERROR)
            msg = _("An error occurred while loading your picture.")
            logging.exception(msg)
            messagebox.showerror("Error", _(msg))
            return

        self.filename = os.path.splitext(os.path.basename(filename))[0]

        self.data_type = os.path.splitext(filename)[1]
        self.images["Original"] = image
        self.images["Processed"] = None
        self.images["Background"] = None
        self.prefs.working_dir = os.path.dirname(filename)

        os.chdir(os.path.dirname(filename))

        width = self.images["Original"].img_display.width
        height = self.images["Original"].img_display.height

        if self.prefs.width != width or self.prefs.height != height:
            self.reset_backgroundpts()

        self.prefs.width = width
        self.prefs.height = height

        tmp_state = fitsheader_2_app_state(self, self.cmd.app_state, self.images["Original"].fits_header)
        self.cmd: Command = Command(INIT_HANDLER, background_points=tmp_state.background_points)
        self.cmd.execute()

        eventbus.emit(AppEvents.LOAD_IMAGE_END, {"filename": filename})

    def on_open_file_dialog_request(self, evet):
        if self.prefs.working_dir != "" and os.path.exists(self.prefs.working_dir):
            initialdir = self.prefs.working_dir
        else:
            initialdir = os.getcwd()

        filename = tk.filedialog.askopenfilename(
            filetypes=[
                ("Image file", ".bmp .png .jpg .tif .tiff .fit .fits .fts .xisf"),
                ("Bitmap", ".bmp"),
                ("PNG", ".png"),
                ("JPEG", ".jpg"),
                ("Tiff", ".tif .tiff"),
                ("Fits", ".fit .fits .fts"),
                ("XISF", ".xisf"),
            ],
            initialdir=initialdir,
        )

        if filename == "":
            return

        eventbus.emit(AppEvents.LOAD_IMAGE_REQUEST, {"filename": filename})

    def on_rbf_kernel_changed(self, event):
        self.prefs.RBF_kernel = event["RBF_kernel"]

    def on_reset_points_request(self, event):
        eventbus.emit(AppEvents.RESET_POITS_BEGIN)

        if len(self.cmd.app_state.background_points) > 0:
            self.cmd = Command(RESET_POINTS_HANDLER, self.cmd)
            self.cmd.execute()

        eventbus.emit(AppEvents.RESET_POITS_END)

    def on_sample_color_changed(self, event):
        self.prefs.sample_color = event["sample_color"]
        eventbus.emit(AppEvents.REDRAW_POINTS_REQUEST)

    def on_sample_size_changed(self, event):
        self.prefs.sample_size = event["sample_size"]
        eventbus.emit(AppEvents.REDRAW_POINTS_REQUEST)

    def on_save_as_changed(self, event):
        self.prefs.saveas_option = event["saveas_option"]

    def on_smoothing_changed(self, event):
        self.prefs.smoothing_option = event["smoothing_option"]

    def on_save_request(self, event):
        if self.prefs.saveas_option == "16 bit Tiff" or self.prefs.saveas_option == "32 bit Tiff":
            dir = tk.filedialog.asksaveasfilename(initialfile=self.filename + "_GraXpert.tiff", filetypes=[("Tiff", ".tiff")], defaultextension=".tiff", initialdir=self.prefs.working_dir)
        elif self.prefs.saveas_option == "16 bit XISF" or self.prefs.saveas_option == "32 bit XISF":
            dir = tk.filedialog.asksaveasfilename(initialfile=self.filename + "_GraXpert.xisf", filetypes=[("XISF", ".xisf")], defaultextension=".xisf", initialdir=self.prefs.working_dir)
        else:
            dir = tk.filedialog.asksaveasfilename(initialfile=self.filename + "_GraXpert.fits", filetypes=[("Fits", ".fits")], defaultextension=".fits", initialdir=self.prefs.working_dir)

        if dir == "":
            return

        eventbus.emit(AppEvents.SAVE_BEGIN)

        try:
            self.images["Processed"].save(dir, self.prefs.saveas_option)
        except Exception as e:
            logging.exception(e)
            eventbus.emit(AppEvents.SAVE_ERROR)
            messagebox.showerror("Error", _("Error occured when saving the image."))

        eventbus.emit(AppEvents.SAVE_END)

    def on_save_background_request(self, event):
        if self.prefs.saveas_option == "16 bit Tiff" or self.prefs.saveas_option == "32 bit Tiff":
            dir = tk.filedialog.asksaveasfilename(initialfile=self.filename + "_background.tiff", filetypes=[("Tiff", ".tiff")], defaultextension=".tiff", initialdir=self.prefs.working_dir)
        elif self.prefs.saveas_option == "16 bit XISF" or self.prefs.saveas_option == "32 bit XISF":
            dir = tk.filedialog.asksaveasfilename(initialfile=self.filename + "_background.xisf", filetypes=[("XISF", ".xisf")], defaultextension=".xisf", initialdir=self.prefs.working_dir)
        else:
            dir = tk.filedialog.asksaveasfilename(initialfile=self.filename + "_background.fits", filetypes=[("Fits", ".fits")], defaultextension=".fits", initialdir=os.getcwd())

        if dir == "":
            return

        eventbus.emit(AppEvents.SAVE_BEGIN)

        try:
            self.images["Background"].save(dir, self.prefs.saveas_option)
        except Exception as e:
            logging.exception(e)
            eventbus.emit(AppEvents.SAVE_ERROR)
            messagebox.showerror("Error", _("Error occured when saving the image."))

        eventbus.emit(AppEvents.SAVE_END)

    def on_save_stretched_request(self, event):
        if self.prefs.saveas_option == "16 bit Tiff" or self.prefs.saveas_option == "32 bit Tiff":
            dir = tk.filedialog.asksaveasfilename(initialfile=self.filename + "_stretched_GraXpert.tiff", filetypes=[("Tiff", ".tiff")], defaultextension=".tiff", initialdir=self.prefs.working_dir)
        elif self.prefs.saveas_option == "16 bit XISF" or self.prefs.saveas_option == "32 bit XISF":
            dir = tk.filedialog.asksaveasfilename(initialfile=self.filename + "_stretched_GraXpert.xisf", filetypes=[("XISF", ".xisf")], defaultextension=".xisf", initialdir=self.prefs.working_dir)
        else:
            dir = tk.filedialog.asksaveasfilename(initialfile=self.filename + "_stretched_GraXpert.fits", filetypes=[("Fits", ".fits")], defaultextension=".fits", initialdir=self.prefs.working_dir)

        if dir == "":
            return

        eventbus.emit(AppEvents.SAVE_BEGIN)

        try:
            if self.images["Processed"] is None:
                self.images["Original"].save_stretched(dir, self.prefs.saveas_option, StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option))
            else:
                self.images["Processed"].save_stretched(dir, self.prefs.saveas_option, StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option))
        except Exception as e:
            eventbus.emit(AppEvents.SAVE_ERROR)
            logging.exception(e)
            messagebox.showerror("Error", _("Error occured when saving the image."))

        eventbus.emit(AppEvents.SAVE_END)

    def on_scaling_changed(self, event):
        self.prefs.scaling = event["scaling"]

    def on_spline_order_changed(self, event):
        self.prefs.spline_order = event["spline_order"]

    def on_stretch_option_changed(self, event):
        self.prefs.stretch_option = event["stretch_option"]
        self.do_stretch()
        
    def on_channels_linked_option_changed(self, event):
        self.prefs.channels_linked_option = event["channels_linked"]
        self.do_stretch()
        

    # application logic
    def do_stretch(self):
        eventbus.emit(AppEvents.STRETCH_IMAGE_BEGIN)

        try:
            all_images = []
            stretches = []
            for img in self.images.values():
                if img is not None:
                    all_images.append(img.img_array)
            if len(all_images) > 0:
                stretches = stretch_all(all_images, StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option))
            for idx, img in enumerate(self.images.values()):
                if img is not None:
                    img.update_display_from_array(stretches[idx], self.prefs.saturation)
        except Exception as e:
            eventbus.emit(AppEvents.STRETCH_IMAGE_ERROR)
            logging.exception(e)

        eventbus.emit(AppEvents.STRETCH_IMAGE_END)
        
    def remove_pt(self, event):
        if len(self.cmd.app_state.background_points) == 0 or not self.prefs.display_pts:
            return False

        point_im = self.to_image_point(event.x, event.y)
        if len(point_im) == 0:
            return False

        eventx_im = point_im[0]
        eventy_im = point_im[1]

        background_points = self.cmd.app_state.background_points

        min_idx = -1
        min_dist = -1

        for i in range(len(background_points)):
            x_im = background_points[i][0]
            y_im = background_points[i][1]

            dist = np.max(np.abs([x_im - eventx_im, y_im - eventy_im]))

            if min_idx == -1 or dist < min_dist:
                min_dist = dist
                min_idx = i

        if min_idx != -1 and min_dist <= self.prefs.sample_size:
            point = background_points[min_idx]
            self.cmd = Command(RM_POINT_HANDLER, self.cmd, idx=min_idx, point=point)
            self.cmd.execute()
            return True
        else:
            return False

    def reset_backgroundpts(self):
        if len(self.cmd.app_state.background_points) > 0:
            self.cmd = Command(RESET_POINTS_HANDLER, self.cmd)
            self.cmd.execute()

    def reset_transform(self):
        self.mat_affine = np.eye(3)

    def scale_at(self, scale: float, cx: float, cy: float):
        self.translate(-cx, -cy)
        self.scale(scale)
        self.translate(cx, cy)

    def scale(self, scale: float):
        mat = np.eye(3)
        mat[0, 0] = scale
        mat[1, 1] = scale
        self.mat_affine = np.dot(mat, self.mat_affine)

    def to_canvas_point(self, x, y):
        return np.dot(self.mat_affine, (x, y, 1.0))

    def to_image_point(self, x, y):
        if self.images[self.display_type] is None:
            return []

        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.0))

        width = self.images[self.display_type].width
        height = self.images[self.display_type].height

        if image_point[0] < 0 or image_point[1] < 0 or image_point[0] > width or image_point[1] > height:
            return []

        return image_point

    def to_image_point_pinned(self, x, y):
        if self.images[self.display_type] is None:
            return []

        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.0))

        width = self.images[self.display_type].width
        height = self.images[self.display_type].height

        if image_point[0] < 0:
            image_point[0] = 0
        if image_point[1] < 0:
            image_point[1] = 0
        if image_point[0] > width:
            image_point[0] = width
        if image_point[1] > height:
            image_point[1] = height

        return image_point

    def translate(self, offset_x, offset_y):
        mat = np.eye(3)
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)

        self.mat_affine = np.dot(mat, self.mat_affine)

    def validate_ai_installation(self):
        if self.prefs.ai_version is None or self.prefs.ai_version == "None":
            messagebox.showerror("Error", _("No AI-Model selected. Please select one from the Advanced panel on the right."))
            return False

        if not validate_local_version(self.prefs.ai_version):
            if not messagebox.askyesno(_("Install AI-Model?"), _("Selected AI-Model is not installed. Should I download it now?")):
                return False
            else:
                eventbus.emit(AppEvents.AI_DOWNLOAD_BEGIN)

                def callback(p):
                    eventbus.emit(AppEvents.AI_DOWNLOAD_PROGRESS, {"progress": p})

                download_version(self.prefs.ai_version, progress=callback)
                eventbus.emit(AppEvents.AI_DOWNLOAD_END)
        return True


graxpert = GraXpert()
