# easy_module_attribute_getter

## Installation:
```
pip install easy_module_attribute_getter
```

## Simple example, using PytorchGetter which extends EasyModuleAttributeGetter:
### 1. Specify class names and arguments in your yaml config file:
```
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

### 2. Read yaml file, and get objects from modules:
```
from easy_module_attribute_getter import YamlReader, PytorchGetter
yaml_reader = YamlReader()
args, _, _ = yaml_reader.load_yamls(['example.yaml'])
pytorch_getter = PytorchGetter()
models = pytorch_getter.get_multiple("model", args.models)
losses = pytorch_getter.get_multiple("loss", args.losses)
```
"models" is a dictionary with keys "modelA" and "modelB" as specified in the yaml file. The values are the loaded objects, which in this case are PyTorch models. The same is true for "losses".


## Easily register your own modules into an existing getter.
```
from pytorch_metric_learning import losses, miners, samplers 
pytorch_getter = PytorchGetter()
pytorch_getter.register('loss', losses) 
pytorch_getter.register('miner', miners)
pytorch_getter.register('sampler', samplers)
metric_loss = pytorch_getter.get('loss', class_name='TripletMarginLoss', return_uninitialized=True)
kl_div_loss = pytorch_getter.get('loss', class_name='KLDivLoss', return_uninitialized=True)
```
In the above example, the 'loss' key already exists, so the 'losses' module will be appended to the existing module. Both modules are searched when get() or get_multiple() is used. For example, metric_loss contains an object from the pytorch_metric_learning library, whil kl_div_loss contains an object from the PyTorch library, which was registered by default.
