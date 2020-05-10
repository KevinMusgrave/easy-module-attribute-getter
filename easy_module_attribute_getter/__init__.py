__version__ = "0.9.35"
import logging
from .yaml_reader import YamlReader
from .easy_module_attribute_getter import EasyModuleAttributeGetter
try:
	from .pytorch_getter import PytorchGetter
except ModuleNotFoundError as e:
	logging.warn(e)
	logging.warn('The PytorchGetter requires torch and torchvision.')
	logging.warn('Try: pip install torch torchvision')