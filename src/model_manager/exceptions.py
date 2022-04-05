
"""
    Some exceptions to help with model manager debugging
"""


class ModelFilesCorrupted(Exception):
    """
    ModelFilesCorrupted indicates that files inside the models directory are not tracked properly
    """


class ShouldHaveModel(Exception):
    """
    ShouldHaveModel indicates that the model manager should have the model in question
    """


class NoOverwrite(Exception):
    """
    NoOverwrite indicates that a model file with that model name already exists and the user didn't use the overwrite parameter
    """
