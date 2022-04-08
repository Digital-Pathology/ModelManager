
"""
    A simple and generalized tool for saving and loading of ML models
"""

import json
import os
import pickle
from types import ModuleType
from typing import Any, Iterable, List

import cloudpickle

from . import config
from . import util
from . import exceptions


class ModelManager:
    """
     A system facilitating the saving/loading of ML models of any kind.

    Saved models are represented by two files: a serialized model object and a json file
    containing information about the model. These files are stored in the same directory.

    Example use:
        model_manager = ModelManager()
        model_manager.save_model(
            model_name = "my_favorite_model",
            model = model,
            model_info = {"description": "this model is simply the coolest"}
        )
        my_model = model_manager.load_model("my_favorite_model")
    """

    def __init__(self, model_dir: str = config.DEFAULT_DIR) -> None:
        """
        __init__ initializes ModelManager

        :param model_dir: the directory where model files are found, defaults to config.DEFAULT_DIR
        :type model_dir: str, optional
        """
        self.model_dir = model_dir
        if not os.path.isdir(self.model_dir):
            os.mkdir(self.model_dir)

    @property
    def models(self) -> List[str]:
        """
        models is a list of the models accessible by ModelManager

        :raises exceptions.ModelFilesCorrupted: if the model files are of unexpected structure
        :return: a list of model names
        :rtype: List[str]
        """
        models = []
        all_model_files = os.listdir(self.model_dir)
        all_model_files.sort()
        for model_files in util.iterate_by_n(all_model_files, n=2, ignore_remainder=False):
            model_file, model_info_file = model_files
            if get_model_name(model_file) != get_model_name(model_info_file):
                raise exceptions.ModelFilesCorrupted(f"Model files are not consistent: \
                    {self.model_dir=}, {model_files=}")
            models.append(get_model_name(model_file))
        return models

    def has_model(self, model_name: str) -> bool:
        """
        has_model returns whether the model manager has the model in question

        :param model_name: the name of the model in question
        :type model_name: str
        :return: True if the model manager has a model with that name
        :rtype: bool
        """
        return model_name in self.models

    def should_have_model(self, model_name: str, exception: str = None) -> None:
        """
        should_have_model throws an exception if this doesn't have model_name

        :param model_name: the name of the model in question
        :type model_name: str
        :param exception: an optional error message other than model_name, defaults to None
        :type exception: str, optional
        :raises exceptions.ShouldHaveModel: if the model manager doesn't have the model in question
        """
        if not self.has_model(model_name):
            raise exceptions.ShouldHaveModel(exception or model_name)

    def save_model(self,
                   model_name: str,
                   model: Any,
                   model_info: dict = None,
                   overwrite_model: bool = False,
                   dependency_modules: Iterable[ModuleType] = None) -> None:  # TODO - add to docstring
        """
        save_model saves a model to model_dir with info in a separate json file

        :param model_name: the name for the model to be saved
        :type model_name: str
        :param model: the model to be saved
        :type model: Any
        :param model_info: a json-serializable dictionary containing any information the user wishes to store about the model, with the model, defaults to None
        :type model_info: dict, optional
        :param overwrite_model: whether to overwrite the model's files, defaults to False
        :type overwrite_model: bool, optional
        :raises exceptions.NoOverwrite: if the model file exists can overwrite wasn't specified
        """
        # overwrite model?
        if not overwrite_model and self.has_model(model_name):
            raise exceptions.NoOverwrite(f"can't overwrite model {model_name}")
        # save model to model file
        model_file = self._make_model_filepath(model_name)
        if dependency_modules is not None:
            for m in dependency_modules:
                cloudpickle.register_pickle_by_value(m)
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
        load_model loads a model from model_dir

        :param model_name: the name of the model to be loaded
        :type model_name: str
        :return: the deserialized model
        :rtype: Any
        """
        model_file = self._make_model_filepath(model_name)
        with open(model_file, 'rb') as f:
            return pickle.load(f)

    def get_model_info(self, model_name: str) -> dict:
        """
        get_model_info gets the json information associated with the model

        :param model_name: the name of the model whose info to get
        :type model_name: str
        :return: the information associated with the model
        :rtype: dict
        """
        self.should_have_model(model_name)
        # open model_info file and read info
        model_info_file = self._make_model_info_filepath(model_name)
        with open(model_info_file, encoding='utf-8') as f:
            return json.load(f)

    def _make_model_filepath(self, model_name: str) -> str:
        """
        _make_model_filepath makes the filepath for the model file given a filename

        :param model_name: the name of the model whose filepath to create
        :type model_name: str
        :return: the filepath for the model's model file
        :rtype: str
        """
        return os.path.join(self.model_dir, model_name + config.DEFAULT_EXT_MODEL)

    def _make_model_info_filepath(self, model_name: str) -> str:
        """
        _make_model_info_filepath makes the filepath for the model's model info file

        :param model_name: the name of the model whose model filepath to create
        :type model_name: str
        :return: the model filepath for the model in question
        :rtype: str
        """
        return os.path.join(self.model_dir, model_name + config.DEFAULT_EXT_INFO)


def get_model_name(filepath: str) -> str:
    """
    get_model_name extracts the model name from model file or model info file

    :param filepath: the filepath from which to extract the model name
    :type filepath: str
    :return: the filepath's model name
    :rtype: str
    """
    return os.path.basename(filepath).split('.')[0]
