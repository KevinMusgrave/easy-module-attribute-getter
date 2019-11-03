from easy_module_attribute_getter import YamlReader, PytorchGetter
import os

yaml_reader = YamlReader()
args, _, _ = yaml_reader.load_yamls(['example.yaml'])
pytorch_getter = PytorchGetter()
models = pytorch_getter.get_multiple("model", args.models)
losses = pytorch_getter.get_multiple("loss", args.losses)

print(models)
print(losses)


### the modules I want to add ###
from pytorch_metric_learning import losses, miners, samplers 
pytorch_getter = PytorchGetter()
# The 'loss' key already exists, so the 'losses' module will be appended to the existing module.
pytorch_getter.register('loss', losses) 
pytorch_getter.register('miner', miners)
pytorch_getter.register('sampler', samplers)

# Both modules will be searched when get() or get_multiple() is used.
# The first loss comes from the module that was just registered.
# The second loss comes from the Pytorch library that is registered by default.
metric_loss = pytorch_getter.get('loss', class_name='TripletMarginLoss', return_uninitialized=True)
kl_div_loss = pytorch_getter.get('loss', class_name='KLDivLoss', return_uninitialized=True)
print(metric_loss)
print(kl_div_loss)