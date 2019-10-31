# easy_module_attribute_getter

## Installation:
```
pip install easy_module_attribute_getter
```

## Example usage:
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
```

### 2. Setup your argparser:
```
import argparse
from easy_module_attribute_getter import YamlReader

parser = argparse.ArgumentParser()
# (optional) add arguments to your argparser
YR = YamlReader(argparser=parser)

...

```
