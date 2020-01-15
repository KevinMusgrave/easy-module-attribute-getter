# easy-module-attribute-getter

## Installation
```
pip install easy-module-attribute-getter
```

## The Problem: unmaintainable if-statements and dictionaries
It's common to specify script parameters in yaml config files. For example:
```yaml
models:
  modelA:
    densenet121:
      pretrained: True
      memory_efficient: True
  modelB:
    resnext50_32x4d:
      pretrained: True
```
Usually, the config file is loaded and then various if-statements or switches are used to instantiate objects etc. It might look something like this (depending on how the config file is organized):
```python
models = {}
for k in ["modelA", "modelB"]:
	model_name = list(args.models[k].keys())[0]
	if model_name == "densenet121":
	  models[k] = torchvision.models.densenet121(**args.models[k][model_name])
	elif model_name == "googlenet":
	  models[k] = torchvision.models.googlenet(**args.models[k][model_name])
	elif model_name == "resnet50":
	  models[k] = torchvision.models.resnet50(**args.models[k][model_name])
	elif model_name == "inception_v3":
	  models[k] = torchvision.models.inception_v3(**args.models[k][model_name])
	...
```
This is kind of annoying to do, and every time PyTorch adds new classes or functions that you want access to, you need to add new cases to your giant if-statement. An alternative is to make a dictionary:
```
model_dict = {"densenet121": torchvision.models.densenet121,
                      "googlenet": torchvision.models.googlenet,
                      "resnet50": torchvision.models.resnet50,
                      "inception_v3": torchvision.models.inception_v3
		      ...}
models = {}
for k in ["modelA", "modelB"]:
	model_name = list(args.models[k].keys())[0]
	models[k] = model_dict[model_name](**args.models[k][model_name])
```
This is shorter than the if statement, but still requires you to manually spell out all the keys and classes. And you still have to update it yourself when the package updates.

## The Solution
### Fetch and initialize multiple models in one line
With this package, the above for-loop and if-statements get reduced to this:
```python
from easy_module_attribute_getter import PytorchGetter
pytorch_getter = PytorchGetter()
models = pytorch_getter.get_multiple("model", args.models)
```
"models" is a dictionary that maps from strings ("modelA" and "modelB") to the desired objects, which have already been initialized with the parameters specified in the config file.

### Access multiple modules in one line
Say you want access to the default package (torchvision.models), as well as the pretrainedmodels package, and two other custom model modules, X and Y. You can register these:
```python
pytorch_getter.register('model', pretrainedmodels) 
pytorch_getter.register('model', X)
pytorch_getter.register('model', Y)
```
Now you can still do the 1-liner:
```python
models = pytorch_getter.get_multiple("model", args.models)
```
And pytorch_getter will try all 4 registered modules until it gets a match.

### Automatically have yaml access to new classes
If you upgrade to a new version of PyTorch which has 20 new classes, you don't have to change anything. You automatically have access to all the new classes, and you can specify them in your yaml file.

### Merge or override complex config options via the command line:
The example yaml file contains 'models' which maps to a nested dictionary containing modelA and modelB. It's easy to add another key to models at the command line, using the standard python notation for nested dictionaries.
```
python example.py --models {modelC: {googlenet: {pretrained: True}}}
```
Then in your script:
```python
import argparse
yaml_reader = YamlReader(argparse.ArgumentParser())
args, _, _ = yaml_reader.load_yamls(['models.yaml', 'losses.yaml'], max_merge_depth=1)
```
Now args.models contains 3 models.

If in general you'd like to merge config options, then in the load_yamls function, set the max_merge_depth argument to the number of sub-dictionaries you'd like the merge to apply to. 

What if you have max_merge_depth set to 1, but want to do a total override for a particular flag? In that case, just append \~OVERRIDE\~ to the flag:
```
python example.py --models~OVERRIDE~ {modelC: {googlenet: {pretrained: True}}}
```
Now args.models will contain just modelC, even though max_merge_depth is set to 1. 

### Load one or multiple yaml files into one args object
```python
from easy_module_attribute_getter import YamlReader
yaml_reader = YamlReader()
args, _, _ = yaml_reader.load_yamls(['models.yaml'])
```
Provide a list of filepaths:
```python
args, _, _ = yaml_reader.load_yamls(['models.yaml', 'optimizers.yaml', 'transforms.yaml'])
```
Or provide a root path and a dictionary mapping subfolder names to the bare filename
```python
root_path = "/where/your/yaml/subfolders/are/"
subfolder_to_name_dict = {"models": "default", "optimizers": "special_trial", "transforms": "blah"}
args, _, _ = yaml_reader.load_yamls(root_path=root_path, subfolder_to_name_dict=subfolder_to_name_dict)
```

## Pytorch-specific features
### Transforms
Specify transforms in your config file:
```yaml
transforms:
  train:
    Resize:
      size: 256
    RandomResizedCrop:
      scale: 0.16 1
      ratio: 0.75 1.33
      size: 227
    RandomHorizontalFlip:
      p: 0.5

  eval:
    Resize:
      size: 256
    CenterCrop:
      size: 227
```
Then load composed transforms in your script:
```python
transforms = {}
for k, v in args.transforms.items():
    transforms[k] = pytorch_getter.get_composed_img_transform(v, mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])
```
The transforms dict now contains:
```python
{'train': Compose(
    Resize(size=256, interpolation=PIL.Image.BILINEAR)
    RandomResizedCrop(size=(227, 227), scale=(0.16, 1), ratio=(0.75, 1.33), interpolation=PIL.Image.BILINEAR)
    RandomHorizontalFlip(p=0.5)
    ToTensor()
    Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
), 'eval': Compose(
    Resize(size=256, interpolation=PIL.Image.BILINEAR)
    CenterCrop(size=(227, 227))
    ToTensor()
    Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
)}
```


### Optimizers, schedulers, and gradient clippers
Optionally specify the scheduler and gradient clipping norm, within the optimizer parameters.
```yaml
optimizers:
  modelA:
    Adam:
      lr: 0.00001
      weight_decay: 0.00005
      scheduler:
        StepLR:
          step_size: 2
          gamma: 0.95
      clip_grad_norm: 1
  modelB:
    RMSprop:
      lr: 0.00001
      weight_decay: 0.00005
```
Create the optimizers:
```python
optimizers = {}
schedulers = {}
grad_clippers = {}
for k, v in models.items():
	optimizers[k], schedulers[k], grad_clippers[k] = pytorch_getter.get_optimizer(v, yaml_dict=args.optimizers[k])
```

### Not just for PyTorch
Note that the YamlReader and EasyModuleAttributeGetter classes are totally independent of PyTorch. I wrote the child class PyTorchGetter since that's what I'm using this package for, but the other two classes can be used in general cases and extended for your own purpose.
