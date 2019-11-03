from easy_module_attribute_getter import YamlReader, PytorchGetter
import os

yaml_reader = YamlReader()
args, _, _ = yaml_reader.load_yamls(['example.yaml'])
pytorch_getter = PytorchGetter()
models = pytorch_getter.get_multiple("model", args.models)
losses = pytorch_getter.get_multiple("loss", args.losses)

print(models)
print(losses)