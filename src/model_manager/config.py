
"""
    Configuration and global variables for the model manager
"""

import os

# directory where this module is called from
CURRENT_DIR = os.getcwd()
# directory containing the models, their initializers, and their info
DEFAULT_DIR = os.path.join(CURRENT_DIR, "models")
# file extensions
DEFAULT_EXT_MODEL = ".model"
DEFAULT_EXT_INFO = ".model_info"

# model_info dependency requirement
MODEL_INFO_DEPENDENCY_KEY = "dependencies"
