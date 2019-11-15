# easy_module_attribute_getter

## Installation
```
pip install easy_module_attribute_getter
```

## The Problem: unmaintainable if-statements and switches
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

losses:
  lossA:
    CrossEntropyLoss:
  lossB:
    L1Loss:
```
Usually, the config file is loaded and then various if-statements or switches are used to instantiate objects etc:
```python
if args.models["modelA"] == "densenet121":
  modelA = torchvision.models.densenet121(pretrained = args.pretrained)
elif args.models["modelA"] == "googlenet":
  modelA = torchvision.models.googlenet(pretrained = args.pretrained)
elif args.models["modelA"] == "resnet50":
  modelA = torchvision.models.resnet50(pretrained = args.pretrained)
elif args.models["modelA"] == "inception_v3":
  modelA = torchvision.models.inception_v3(pretrained = args.pretrained)
...
if args.losses["lossA"] == "CrossEntropyLoss":
  lossA = torch.nn.CrossEntropyLoss()
elif args.losses["lossA"] == "L1Loss":
  lossA = torch.nn.L1Loss()
...
```
## The Solution
### Use this package, and get rid of all those annoying if-statements and switches:
```python
from easy_module_attribute_getter import PytorchGetter
pytorch_getter = PytorchGetter()
models = pytorch_getter.get_multiple("model", args.models)
losses = pytorch_getter.get_multiple("loss", args.losses)
```
"models" and "losses" are dictionaries that map from strings to the desired objects.

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


### Easily register your own modules into an existing getter.
```python
from pytorch_metric_learning import losses, miners, samplers 
pytorch_getter = PytorchGetter()
pytorch_getter.register('loss', losses) 
pytorch_getter.register('miner', miners)
pytorch_getter.register('sampler', samplers)
metric_loss = pytorch_getter.get('loss', class_name='ProxyNCALoss', return_uninitialized=True)
kl_div_loss = pytorch_getter.get('loss', class_name='KLDivLoss', return_uninitialized=True)
```
In the above example, the 'loss' key already exists, so the 'losses' module will be appended to the existing module.


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
