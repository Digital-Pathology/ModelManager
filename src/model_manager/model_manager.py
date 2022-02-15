
from ast import FunctionType, literal_eval
import json
import marshal
import os
import types
from typing import Any, Callable

import torch

from . import config

class ModelManager(object):

    """
        Model Manager

            This class is designed to facilitate the saving and loading of PyTorch-based models,
            with planned generalizations to any object inheriting from a certain ManagedModel class.

            Models are stored in a directory as (currently) serialized PyTorch weights.
            In order to save a model with the ModelManager, the user must give an initialization function
            for the model. This is to ensure that dependencies are in order before loading the serialized
            weights.

            Example use:

                model_manager = ModelManager()
                my_model = model_manager.load_model("my_favorite_model")
    """

    def __init__(self, model_dir: str = config.DEFAULT_MODEL_DIR, model_info_file: str = config.DEFAULT_MODEL_INFO_FILE):
        """
            ModelManager initializer

                model_dir (str): the directory where the models and model info will be stored. Defaults to cwd/models/
                model_info_file (str): the name of the file in model_dir where model info will be stored. Defaults to model_dir/model-info.json

                Both model_dir and model_info_file will be created if they do not exist.
        """
        self.model_dir = model_dir
        if not os.path.isdir(self.model_dir):
            os.mkdir(self.model_dir)

        self.model_info_path = os.path.join(self.model_dir, model_info_file)
        self.load_model_info()

    def __del__(self, save_model_info: bool = True):
        """
            ModelManager deletion

                The ModelManager saves all model info before being deleted, unless manually deleted and specified otherwise.
        """
        if save_model_info: self.save_model_info()

    def save_model(self, model: torch.nn.Module, model_name: str, model_info: dict, overwrite_model: bool = False):
        """
            ModelManager save_model

                Saves a model to model_dir with info in model_info_file

                model (torch.nn.Module): A PyTorch model.
                model_name (str): An identifier for your model.
                model_info (str): A dictionary with any useful information about your model. Must contain an initializer function at the key [config.MODEL_INFO_KEY_INITIALIZER].
                overwrite_model (bool): Do you want to overwrite the model if it exists? If yes --> True
        """
        if not overwrite_model and model_name in self.model_info:
            raise Exception(f"can't overwrite model {model_name}")

        self.validate_model_info(model_info)

        model_info[config.MODEL_INFO_KEY_INITIALIZER] = self.convert_model_info_initializer_to_string_representation(model_info[config.MODEL_INFO_KEY_INITIALIZER])
        self.model_info[model_name] = model_info
        torch.save(model.state_dict(), self.make_model_path(model_name))

        self.save_model_info()

    def load_model(self, model_name: str) -> torch.nn.Module:
        """
            ModelManager load_model

                loads a model from model_dir using information from model_info_file

                model_name (str): An identifier for the model to be loaded
        """
        self.load_model_info()

        if model_name not in self.model_info:
            raise Exception(f"{model_name} not in model_info")
        
        model_info = self.model_info[model_name]
        model_initializer = self.convert_model_info_intializer_from_string_representation(model_info[config.MODEL_INFO_KEY_INITIALIZER], model_name)
        model: torch.nn.Module = model_initializer()
        model.load_state_dict(torch.load(self.make_model_path(model_name)))
        model.eval()
        return model

    def validate_model_info(self, model_info) -> bool:
        """
            ModelMananger validate_model_info

                Checks whether model_info contains an initializer function for the model in question and is otherwise json serializable
        """
        if config.MODEL_INFO_KEY_INITIALIZER not in model_info or not isinstance(model_info[config.MODEL_INFO_KEY_INITIALIZER], Callable):
            raise Exception(f"model_info needs to contain {config.MODEL_INFO_KEY_INITIALIZER}, a function (callable) for initializing the model. Currently {model_info.get(config.MODEL_INFO_KEY_INITIALIZER)=}")
        if not ModelManager.is_json_serializable({k:v for k,v in model_info.items() if k != config.MODEL_INFO_KEY_INITIALIZER}):
            raise Exception("model is not json serializable")

    def convert_model_info_initializer_to_string_representation(self, initializer: FunctionType):

        # TODO - make this process better? enforce no args?
        return config.MODEL_INFO_INTIALIZER_STRING_PREFIX + str(marshal.dumps(initializer.__code__))

    def convert_model_info_intializer_from_string_representation(self, initializer_string_representation, model_name):

        # TODO - make this process better?
        initializer_string_representation = initializer_string_representation.replace(config.MODEL_INFO_INTIALIZER_STRING_PREFIX, "")
        initializer = types.FunctionType(marshal.loads(literal_eval(initializer_string_representation)), globals(), f"{model_name}_initializer_from_model_info")
        return initializer

    def make_model_path(self, model_name: str):

        return f"{self.dir_path}{os.path.sep}{model_name}.model"

    def save_model_info(self):
        """
            ModelManager save_model_info

                Saves model_info to model_info_file, creating it if necessary
        """
        if not ModelManager.is_json_serializable(self.model_info):
            raise Exception("Ruh roh")
        with open(self.model_info_path, 'w' if os.path.isfile(self.model_info_path) else 'x') as f:
            json.dump(self.model_info, f)
    
    def load_model_info(self):
        """
            ModelManager load_model_info

                Loads model_info from model_info_file, initializing it if necessary
        """
        if not os.path.exists(self.model_info_path):
            open(self.model_info_path, 'x').close()
            self.model_info = {}
        else:
            with open(self.model_info_path) as f:
                self.model_info = json.load(f)

    @staticmethod
    def is_json_serializable(data: Any) -> bool:
        """
            ModelManager is_json_serializable

                A simple function for checking that something is json serializable
        """
        try:
            str = json.dumps(data)
            return True
        except Exception as e:
            return False
