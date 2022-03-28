
"""
    A simple and generalized model saving and loading tool
"""

import json
import os
import pickle
from typing import Any

import cloudpickle

from . import config
from . import util


class ModelManager:

    """
        Model Manager

            This class is designed to facilitate the saving and loading of ML models of any kind.

            Saved models are represented by two files: a serialized model object and a json file
            containing information about the model. These files are stored in the same directory.

            Example use:

                model_manager = ModelManager()
                model_manager.save_model(
                    model_name = "my_favorite_model",
                    model = model,
                    model_info = {
                        "description": "this model is simply the coolest"
                    }
                )
                my_model = model_manager.load_model("my_favorite_model")
    """

    def __init__(self, model_dir: str = config.DEFAULT_DIR):
        """
            ModelManager initializer

                model_dir (str): the directory where the models and model info will be stored.
                Defaults to cwd/models/

                model_dir will be created if it does not exist.
        """
        self.model_dir = model_dir
        if not os.path.isdir(self.model_dir):
            os.mkdir(self.model_dir)

    @property
    def models(self):
        """ a list of models in self.model_dir """
        models = []
        all_model_files = os.listdir(self.model_dir)
        all_model_files.sort()
        for model_files in util.iterate_by_n(all_model_files, n=2, ignore_remainder=False):
            model_file, model_info_file = model_files
            if get_model_name(model_file) != get_model_name(model_info_file):
                raise Exception(f"Model files are not consistent: \
                    {self.model_dir=}, {model_files=}")
            models.append(get_model_name(model_file))
        return models

    def has_model(self, model_name: str) -> bool:
        """ returns whether the model manager has the model in question """
        return model_name in self.models

    def should_have_model(self, model_name: str, exception: str = None) -> None:
        """ throws an exception if this doesn't have model_name """
        if not self.has_model(model_name):
            raise Exception(exception or model_name)

    def save_model(self,
                   model_name: str,
                   model: Any,
                   model_info: dict = None,
                   overwrite_model: bool = False):
        """
            ModelManager save_model

                Saves a model to model_dir with info in model_info_file

                model_name (str): A unique identifier for your model.
                model (Any): Your model.
                model_info (dict): Any other helpful information about the model.
                overwrite_model (bool): Do you want to overwrite the model if it exists? \
                                            If yes --> True
        """
        # overwrite model?
        if not overwrite_model and self.has_model(model_name):
            raise Exception(f"can't overwrite model {model_name}")
        # save model to model file
        model_file = self._make_model_filepath(model_name)
        with util.open_file(model_file) as f:
            cloudpickle.dump(model, f)
        # save model info to model_info file
        if model_info is None:
            model_info = {}
        model_info_file = self._make_model_info_filepath(model_name)
        with util.open_file(model_info_file, binary=False) as f:
            json.dump(model_info, f, indent=2)

    def load_model(self, model_name: str) -> Any:
        """
            ModelManager load_model

                loads a model from model_dir

                model_name (str): An identifier for the model to be loaded
        """
        model_file = self._make_model_filepath(model_name)
        with open(model_file, 'rb') as f:
            return pickle.load(f)

    def get_model_info(self, model_name: str) -> dict:
        """ returns the model_info for the model in question """
        self.should_have_model(model_name)
        # open model_info file and read info
        model_info_file = self._make_model_info_filepath(model_name)
        with open(model_info_file, encoding='utf-8') as f:
            return json.load(f)

    def _make_model_filepath(self, model_name: str) -> str:
        return os.path.join(self.model_dir, model_name + config.DEFAULT_EXT_MODEL)

    def _make_model_info_filepath(self, model_name: str) -> str:
        return os.path.join(self.model_dir, model_name + config.DEFAULT_EXT_INFO)


def get_model_name(filepath):
    """ extracts the model name from model file or model info file """
    return os.path.basename(filepath).split('.')[0]
