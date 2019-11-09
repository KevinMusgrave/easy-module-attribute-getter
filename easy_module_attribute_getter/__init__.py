__version__ = "0.9.15"
from .yaml_reader import YamlReader
from .easy_module_attribute_getter import EasyModuleAttributeGetter
try:
	from .pytorch_getter import PytorchGetter
except ModuleNotFoundError as e:
	print(e)
	print('The PytorchGetter requires torch and torchvision.')
	print('Try: pip install torch torchvision')