import torch
import torchvision
from . import utils as c_f, custom_transforms
from . import EasyModuleAttributeGetter

class PytorchGetter(EasyModuleAttributeGetter):
    def __init__(self, use_pretrainedmodels_package=False):
        self.model = [torchvision.models]
        if use_pretrainedmodels_package:
            import pretrainedmodels
            self.model += [pretrainedmodels]
        self.loss = [torch.nn]
        self.optimizer = [torch.optim]
        self.lr_scheduler = [torch.optim.lr_scheduler]
        self.transform = [custom_transforms, torchvision.transforms.transforms]
        self.dataset = [torchvision.datasets]

    # modified from https://github.com/meetshah1995/pytorch-semseg  
    def get_composed_transform(self, transform_dict):
        augmentations = []
        for k, param in transform_dict.items():
            if param is None:
                param = {}
            else:
                param = c_f.try_convert_to_list_of_numbers(param)
            augmentations.append(self.get("transform", k, param))
        return torchvision.transforms.Compose(augmentations)

    def get_composed_img_transform(self, transform_dict, mean=None, std=None, input_space=None, input_range=None):
        if input_space == "BGR":
            new_dict = {"ConvertToBGR":{}}
            transform_dict = c_f.merge_two_dicts(new_dict, transform_dict)
        transform_dict["ToTensor"] = {}
        if input_range is not None and input_range[1] != 1:
            transform_dict["Multiplier"] = {"multiple": input_range[1]}
        if None not in [mean, std]:
            transform_dict["Normalize"] = {"mean": mean, "std": std}
        return self.get_composed_transform(transform_dict)

    def get_optimizer(self, input_model, class_name=None, params=None, yaml_dict=None):
        optimizer, scheduler, grad_clipper = None, None, None
        model_parameters = input_model.parameters()
        optimizer_class, opt_dict = self.get(
            "optimizer", 
            class_name=class_name, 
            params=params, 
            yaml_dict=yaml_dict,
            additional_params={"params":model_parameters},
            return_uninitialized=True
        )
        scheduler_type = opt_dict.pop("scheduler", None)
        clip_grad_norm = opt_dict.pop("clip_grad_norm", None)
        optimizer = optimizer_class(**opt_dict)

        if scheduler_type is not None:
            scheduler = self.get("lr_scheduler", yaml_dict=scheduler_type, additional_params={"optimizer": optimizer})

        if clip_grad_norm is not None:
            grad_clipper = lambda: torch.nn.utils.clip_grad_norm_(model_parameters, clip_grad_norm)

        return optimizer, scheduler, grad_clipper