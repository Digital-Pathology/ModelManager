
import os

# directory where this module is called from
CURRENT_DIR = os.getcwd()
# directory containing the saved models and their info
DEFAULT_MODEL_DIR = os.path.join(CURRENT_DIR, "models")
# file containing information about saved models
DEFAULT_MODEL_INFO_FILE = "model_info.json"

# important static globals for intepreting model-info.json
MODEL_INFO_KEY_INITIALIZER = "initializer"
MODEL_INFO_INTIALIZER_STRING_PREFIX = "DO NOT TOUCH THIS STRING AT ALL --> "
