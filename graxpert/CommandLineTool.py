import logging
import os
import sys
from pathlib import Path
import numpy as np

from appdirs import user_config_dir

from graxpert.ai_model_handling import (ai_model_path_from_version,
                                        download_version, latest_version,
                                        list_local_versions)
from graxpert.astroimage import AstroImage
from graxpert.background_extraction import extract_background
from graxpert.preferences import load_preferences, save_preferences
import json

class CommandLineTool:
    def __init__(self, args):
        self.args = args

    def execute(self):
        astro_Image = AstroImage(do_update_display=False)
        astro_Image.set_from_file(self.args.filename, None, None)
        
        processed_Astro_Image = AstroImage(do_update_display=False)
        background_Astro_Image = AstroImage(do_update_display=False)
        
        processed_Astro_Image.fits_header = astro_Image.fits_header
        background_Astro_Image.fits_header = astro_Image.fits_header
        
        interpol_type_option="AI"
        RBF_kernel = "RBF"
        background_points=[]
        sample_size=50
        downscale_factor = 1
        spline_order=0

        if (self.args.preferencesfile):
            try:
                preferencesfile = Path(self.args.preferencesfile)
                if preferencesfile.is_file() and preferencesfile.suffix == ".json":
                    prefs=json.load(preferencesfile.open("r"))
                    background_points=prefs["background_points"]
                    sample_size=prefs["sample_size"]
                    spline_order=prefs["spline_order"]
                    RBF_kernel=prefs["RBF_kernel"]
                    interpol_type_option=prefs["interpol_type_option"]
                    if interpol_type_option == "Kriging" or interpol_type_option == "RBF":
                        downscale_factor = 4

            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)

        if interpol_type_option == "AI":
            ai_model_path_from_version(self.get_ai_version())
        else:
            ai_model_path=None

        background_Astro_Image.set_from_array(
            extract_background(
                astro_Image.img_array,
                np.array(background_points),
                interpol_type_option,
                self.args.smoothing,
                downscale_factor,
                sample_size,
                RBF_kernel,
                spline_order,
                self.args.correction,
                ai_model_path
            )
        )

        processed_Astro_Image.set_from_array(astro_Image.img_array)

        processed_Astro_Image.save(self.get_save_path(), self.get_output_file_format())
        if (self.args.bg):
            background_Astro_Image.save(self.get_background_save_path(), self.get_output_file_format())

    
    def get_ai_version(self):
        prefs_filename = os.path.join(
            user_config_dir(appname="GraXpert"), "preferences.json"
        )
        prefs = load_preferences(prefs_filename)

        ai_version = None
        if self.args.ai_version:
            ai_version = self.args.ai_version
        else:
            ai_version = prefs.ai_version

        if ai_version is None:
            ai_version = latest_version()

        logging.info(
            "using AI version {}. you can change this by providing the argument '-ai_version'".format(
                ai_version
            )
        )

        if not ai_version in [v["version"] for v in list_local_versions()]:
            try:
                logging.info(
                    "AI version {} not found locally, downloading...".format(ai_version)
                )
                download_version(ai_version)
                logging.info("download successful".format(ai_version))
            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)

        prefs.ai_version = ai_version
        save_preferences(prefs_filename, prefs)
        
        return ai_version
    
    def get_output_file_ending(self):
        file_ending = os.path.splitext(self.args.filename)[-1]
        
        if file_ending.lower() == ".xisf":
            return ".xisf"
        else:
            return ".fits"
        
    def get_output_file_format(self):
        output_file_ending = self.get_output_file_ending()
        if (output_file_ending) == ".xisf":
            return "32 bit XISF"
        else:
            return "32 bit Fits"
        
    def get_save_path(self):
        if (self.args.output is not None):
            base_path = os.path.dirname(self.args.filename)
            output_file_name = self.args.output + self.get_output_file_ending()
            return os.path.join(base_path, output_file_name)
            
        else:
            return os.path.splitext(self.args.filename)[0] + "_GraXpert" + self.get_output_file_ending()
        
    def get_background_save_path(self):
        save_path = self.get_save_path()
        return os.path.splitext(save_path)[0] + "_background" + self.get_output_file_ending()
