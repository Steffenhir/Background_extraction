import tkinter as tk

from customtkinter import StringVar, ThemeManager

import graxpert.ui.tooltip as tooltip
from graxpert.application.app import graxpert
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.localization import _
from graxpert.ui.ui_events import UiEvents
from graxpert.ui.widgets import (
    CollapsibleMenuFrame,
    ExtractionStep,
    GraXpertButton,
    GraXpertCheckbox,
    GraXpertLabel,
    GraXpertOptionMenu,
    GraXpertScrollableFrame,
    ValueSlider,
    default_label_width,
    padx,
    pady,
)


class CropMenu(CollapsibleMenuFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title=_("Crop"), show=False, **kwargs)
        self.create_children()
        self.setup_layout()
        self.place_children()

    def create_children(self):
        super().create_children()
        self.cropmode_button = GraXpertButton(self.sub_frame, text=_("Crop mode on/off"), command=lambda: eventbus.emit(UiEvents.TOGGLE_CROP_REQUEST))
        self.cropapply_button = GraXpertButton(self.sub_frame, text=_("Apply crop"), command=lambda: eventbus.emit(UiEvents.APPLY_CROP_REQUEST))

    def setup_layout(self):
        super().setup_layout()

    def place_children(self):
        super().place_children()
        self.cropmode_button.grid(column=1, row=0, pady=pady, sticky=tk.NSEW)
        self.cropapply_button.grid(column=1, row=1, pady=pady, sticky=tk.NSEW)


class ExtractionMenu(CollapsibleMenuFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title=_("Background Extraction"), **kwargs)

        # stretch options
        self.stretch_options = ["No Stretch", "10% Bg, 3 sigma", "15% Bg, 3 sigma", "20% Bg, 3 sigma", "30% Bg, 2 sigma"]
        self.stretch_option_current = StringVar()
        self.stretch_option_current.set(graxpert.prefs.stretch_option)
        self.stretch_option_current.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.STRETCH_OPTION_CHANGED, {"stretch_option": self.stretch_option_current.get()}))

        self.saturation = tk.DoubleVar()
        self.saturation.set(graxpert.prefs.saturation)
        self.saturation.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.CHANGE_SATURATION_REQUEST, {"saturation": self.saturation.get()}))
        
        self.channels_linked = tk.BooleanVar()
        self.channels_linked.set(graxpert.prefs.channels_linked_option)
        self.channels_linked.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.CHANNELS_LINKED_CHANGED, {"channels_linked": self.channels_linked.get()}))

        # sample selection
        self.display_pts = tk.BooleanVar()
        self.display_pts.set(graxpert.prefs.display_pts)
        self.display_pts.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.DISPLAY_PTS_CHANGED, {"display_pts": self.display_pts.get()}))

        self.flood_select_pts = tk.BooleanVar()
        self.flood_select_pts.set(graxpert.prefs.bg_flood_selection_option)
        self.flood_select_pts.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.BG_FLOOD_SELECTION_CHANGED, {"bg_flood_selection_option": self.flood_select_pts.get()}))

        self.bg_pts = tk.IntVar()
        self.bg_pts.set(graxpert.prefs.bg_pts_option)
        self.bg_pts.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.BG_PTS_CHANGED, {"bg_pts_option": self.bg_pts.get()}))

        self.bg_tol = tk.DoubleVar()
        self.bg_tol.set(graxpert.prefs.bg_tol_option)
        self.bg_tol.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.BG_TOL_CHANGED, {"bg_tol_option": self.bg_tol.get()}))

        # calculation
        self.interpol_options = ["RBF", "Splines", "Kriging", "AI"]
        self.interpol_type = tk.StringVar()
        self.interpol_type.set(graxpert.prefs.interpol_type_option)
        self.interpol_type.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.INTERPOL_TYPE_CHANGED, {"interpol_type_option": self.interpol_type.get()}))

        self.smoothing = tk.DoubleVar()
        self.smoothing.set(graxpert.prefs.smoothing_option)
        self.smoothing.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SMOTTHING_CHANGED, {"smoothing_option": self.smoothing.get()}))

        # saving
        self.saveas_options = ["16 bit Tiff", "32 bit Tiff", "16 bit Fits", "32 bit Fits", "16 bit XISF", "32 bit XISF"]
        self.saveas_type = tk.StringVar()
        self.saveas_type.set(graxpert.prefs.saveas_option)
        self.saveas_type.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SAVE_AS_CHANGED, {"saveas_option": self.saveas_type.get()}))

        self.create_children()
        self.setup_layout()
        self.place_children()

    def create_children(self):
        super().create_children()

        # image loading
        self.loading_title = ExtractionStep(self.sub_frame, 1, _(" Loading"))
        self.load_image_button = GraXpertButton(
            self.sub_frame,
            text=_("Load Image"),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
            command=self.menu_open_clicked,
        )
        self.tt_load = tooltip.Tooltip(self.load_image_button, text=tooltip.load_text)

        # stretch options
        self.stretch_options_title = ExtractionStep(self.sub_frame, 2, _(" Stretch Options"))
        self.stretch_menu = GraXpertOptionMenu(
            self.sub_frame,
            variable=self.stretch_option_current,
            values=self.stretch_options,
        )
        tooltip.Tooltip(self.stretch_menu, text=tooltip.stretch_text)
        self.saturation_slider = ValueSlider(
            self.sub_frame,
            width=default_label_width,
            variable_name=_("Saturation"),
            variable=self.saturation,
            min_value=0,
            max_value=3,
            precision=1,
        )
        self.channels_linked_switch = GraXpertCheckbox(self.sub_frame, width=default_label_width, text=_("Channels linked"), variable=self.channels_linked)

        # sample selection
        self.sample_selection_title = ExtractionStep(self.sub_frame, 3, _(" Sample Selection"))
        self.display_pts_switch = GraXpertCheckbox(self.sub_frame, width=default_label_width, text=_("Display points"), variable=self.display_pts)
        self.flood_select_pts_switch = GraXpertCheckbox(self.sub_frame, width=default_label_width, text=_("Flooded generation"), variable=self.flood_select_pts)
        tooltip.Tooltip(self.flood_select_pts_switch, text=tooltip.bg_flood_text)
        self.bg_pts_slider = ValueSlider(self.sub_frame, width=default_label_width, variable_name=_("Points per row"), variable=self.bg_pts, min_value=4, max_value=25, precision=0)
        tooltip.Tooltip(self.bg_pts_slider, text=tooltip.num_points_text)
        self.bg_tol_slider = ValueSlider(self.sub_frame, width=default_label_width, variable_name=_("Grid Tolerance"), variable=self.bg_tol, min_value=-2, max_value=10, precision=1)
        tooltip.Tooltip(self.bg_tol_slider, text=tooltip.bg_tol_text)
        self.bg_selection_button = GraXpertButton(self.sub_frame, text=_("Create Grid"), command=lambda: eventbus.emit(AppEvents.CREATE_GRID_REQUEST))
        tooltip.Tooltip(self.bg_selection_button, text=tooltip.bg_select_text)
        self.reset_button = GraXpertButton(self.sub_frame, text=_("Reset Sample Points"), command=lambda: eventbus.emit(AppEvents.RESET_POITS_REQUEST))
        tooltip.Tooltip(self.reset_button, text=tooltip.reset_text)

        # calculation
        self.calculation_title = ExtractionStep(self.sub_frame, 4, _(" Calculation"))
        self.intp_type_text = GraXpertLabel(self.sub_frame, text=_("Interpolation Method:"))
        self.interpol_menu = GraXpertOptionMenu(self.sub_frame, variable=self.interpol_type, values=self.interpol_options)
        tooltip.Tooltip(self.interpol_menu, text=tooltip.interpol_type_text)
        self.smoothing_slider = ValueSlider(self.sub_frame, width=default_label_width, variable_name=_("Smoothing"), variable=self.smoothing, min_value=0, max_value=1, precision=1)
        tooltip.Tooltip(self.smoothing_slider, text=tooltip.smoothing_text)
        self.calculate_button = GraXpertButton(
            self.sub_frame,
            text=_("Calculate Background"),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
            command=lambda: eventbus.emit(AppEvents.CALCULATE_REQUEST),
        )
        tooltip.Tooltip(self.calculate_button, text=tooltip.calculate_text)

        # saving
        self.saving_title = ExtractionStep(self.sub_frame, 5, _(" Saving"))
        self.saveas_menu = GraXpertOptionMenu(self.sub_frame, variable=self.saveas_type, values=self.saveas_options)
        tooltip.Tooltip(self.saveas_menu, text=tooltip.saveas_text)
        self.save_button = GraXpertButton(
            self.sub_frame,
            text=_("Save Processed"),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
            command=lambda: eventbus.emit(AppEvents.SAVE_REQUEST),
        )
        tooltip.Tooltip(self.save_button, text=tooltip.save_pic_text)
        self.save_background_button = GraXpertButton(self.sub_frame, text=_("Save Background"), command=lambda: eventbus.emit(AppEvents.SAVE_BACKGROUND_REQUEST))
        tooltip.Tooltip(self.save_background_button, text=tooltip.save_bg_text)
        self.save_stretched_button = GraXpertButton(self.sub_frame, text=_("Save Stretched & Processed"), command=lambda: eventbus.emit(AppEvents.SAVE_STRETCHED_REQUEST))
        tooltip.Tooltip(self.save_stretched_button, text=tooltip.save_stretched_pic_text)

    def setup_layout(self):
        super().setup_layout()

    def place_children(self):
        super().place_children()

        # image loading
        self.loading_title.grid(column=0, row=0, columnspan=2, pady=pady, sticky=tk.EW)
        self.load_image_button.grid(column=1, row=1, pady=pady, sticky=tk.EW)

        # stretch options
        self.stretch_options_title.grid(column=0, row=2, columnspan=2, pady=pady, sticky=tk.EW)
        self.stretch_menu.grid(column=1, row=3, pady=pady, sticky=tk.EW)
        self.saturation_slider.grid(column=1, row=4, pady=pady, sticky=tk.EW)
        self.channels_linked_switch.grid(column=1, row=5, pady=pady, sticky=tk.EW)

        # sample selection
        self.sample_selection_title.grid(column=0, row=6, columnspan=2, pady=pady, sticky=tk.EW)
        self.display_pts_switch.grid(column=1, row=7, pady=pady, sticky=tk.EW)
        self.flood_select_pts_switch.grid(column=1, row=8, pady=pady, sticky=tk.EW)
        self.bg_pts_slider.grid(column=1, row=9, pady=pady, sticky=tk.EW)
        self.bg_tol_slider.grid(column=1, row=10, pady=pady, sticky=tk.EW)
        self.bg_selection_button.grid(column=1, row=11, pady=pady, sticky=tk.EW)
        self.reset_button.grid(column=1, row=12, pady=pady, sticky=tk.EW)

        # calculation
        self.calculation_title.grid(column=0, row=13, pady=pady, columnspan=2, sticky=tk.EW)
        self.intp_type_text.grid(column=1, row=14, pady=pady, sticky=tk.EW)
        self.interpol_menu.grid(column=1, row=15, pady=pady, sticky=tk.EW)
        self.smoothing_slider.grid(column=1, row=16, pady=pady, sticky=tk.EW)
        self.calculate_button.grid(column=1, row=17, pady=pady, sticky=tk.EW)

        # saving
        self.saving_title.grid(column=0, row=18, pady=pady, columnspan=2, sticky=tk.EW)
        self.saveas_menu.grid(column=1, row=19, pady=pady, sticky=tk.EW)
        self.save_button.grid(column=1, row=20, pady=pady, sticky=tk.EW)
        self.save_background_button.grid(column=1, row=21, pady=pady, sticky=tk.EW)
        self.save_stretched_button.grid(column=1, row=22, pady=pady, sticky=tk.EW)

    def menu_open_clicked(self, event=None):
        eventbus.emit(AppEvents.OPEN_FILE_DIALOG_REQUEST)


class LeftMenu(GraXpertScrollableFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.create_children()
        self.setup_layout()
        self.place_children()

    def create_children(self):
        self.crop_menu = CropMenu(self, fg_color="transparent")
        self.extraction_menu = ExtractionMenu(self, fg_color="transparent")

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def place_children(self):
        self.crop_menu.grid(column=0, row=0, ipadx=padx, sticky=tk.N)
        self.extraction_menu.grid(column=0, row=1, ipadx=padx, sticky=tk.N)
