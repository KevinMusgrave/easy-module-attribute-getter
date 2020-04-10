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
        self.sampler = [torch.utils.data]

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
        scheduler_types = {}
        for k in ["scheduler_by_iteration", "scheduler_by_epoch", "scheduler_by_plateau"]:
            scheduler_types[k] = yaml_dict.pop(k, None)
        clip_grad_norm = yaml_dict.pop("clip_grad_norm", None)
        optimizer = self.get(
            "optimizer", 
            class_name=class_name, 
            params=params, 
            yaml_dict=yaml_dict,
            additional_params={"params":model_parameters},
        )

        schedulers = None
        for k, v in scheduler_types.items():
            if v is not None:
                if schedulers is None: schedulers = {}
                schedulers[k] = self.get("lr_scheduler", yaml_dict=v, additional_params={"optimizer": optimizer})

        if clip_grad_norm is not None:
            grad_clipper = lambda: torch.nn.utils.clip_grad_norm_(model_parameters, clip_grad_norm)

        return optimizer, schedulers, grad_clipper