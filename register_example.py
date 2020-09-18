from easy_module_attribute_getter import YamlReader, PytorchGetter
import easy_module_attribute_getter
import pretrainedmodels
import torchvision
print("VERSION={}".format(easy_module_attribute_getter.__version__))


pg = PytorchGetter(use_pretrainedmodels_package=True)

assert torchvision.models in pg.model
assert pretrainedmodels in pg.model

pg.unregister("model", pretrainedmodels)

assert pretrainedmodels not in pg.model

pg.unregister("model", "torchvision.models")
assert torchvision.models not in pg.model

pg.unregister("model", pretrainedmodels)

class A:
    x = 5

pg.register("model", A)
assert A in pg.model

pg.unregister("model", "A")
assert A not in pg.model