from enum import Enum, auto


class AppEvents(Enum):
    # image loading
    OPEN_FILE_DIALOG_REQUEST = auto()
    LOAD_IMAGE_REQUEST = auto()
    LOAD_IMAGE_BEGIN = auto()
    LOAD_IMAGE_END = auto()
    LOAD_IMAGE_ERROR = auto()
    # image stretching
    STRETCH_IMAGE_BEGIN = auto()
    STRETCH_IMAGE_END = auto()
    STRETCH_IMAGE_ERROR = auto()
    # image saturation
    CHANGE_SATURATION_REQUEST = auto()
    CHANGE_SATURATION_BEGIN = auto()
    CHANGE_SATURATION_END = auto()
    # image display
    UPDATE_DISPLAY_TYPE_REEQUEST = auto()
    DISPLAY_TYPE_CHANGED = auto()
    REDRAW_POINTS_REQUEST = auto()
    # stretch options
    STRETCH_OPTION_CHANGED = auto()
    CHANNELS_LINKED_CHANGED = auto()
    # sample selection
    DISPLAY_PTS_CHANGED = auto()
    BG_FLOOD_SELECTION_CHANGED = auto()
    BG_PTS_CHANGED = auto()
    BG_TOL_CHANGED = auto()
    CREATE_GRID_REQUEST = auto()
    CREATE_GRID_BEGIN = auto()
    CREATE_GRID_END = auto()
    RESET_POITS_REQUEST = auto()
    RESET_POITS_BEGIN = auto()
    RESET_POITS_END = auto()
    # calculation
    INTERPOL_TYPE_CHANGED = auto()
    SMOTTHING_CHANGED = auto()
    CALCULATE_REQUEST = auto()
    CALCULATE_BEGIN = auto()
    CALCULATE_PROGRESS = auto()
    CALCULATE_END = auto()
    CALCULATE_ERROR = auto()
    # saving
    SAVE_AS_CHANGED = auto()
    SAVE_REQUEST = auto()
    SAVE_BACKGROUND_REQUEST = auto()
    SAVE_STRETCHED_REQUEST = auto()
    SAVE_BEGIN = auto()
    SAVE_END = auto()
    SAVE_ERROR = auto()
    # ai model handling
    AI_VERSION_CHANGED = auto()
    AI_DOWNLOAD_BEGIN = auto()
    AI_DOWNLOAD_PROGRESS = auto()
    AI_DOWNLOAD_END = auto()
    AI_DOWNLOAD_ERROR = auto()
    # advanced settings
    SAMPLE_SIZE_CHANGED = auto()
    SAMPLE_COLOR_CHANGED = auto()
    RBF_KERNEL_CHANGED = auto()
    SPLINE_ORDER_CHANGED = auto()
    CORRECTION_TYPE_CHANGED = auto()
    LANGUAGE_CHANGED = auto()
    SCALING_CHANGED = auto()
