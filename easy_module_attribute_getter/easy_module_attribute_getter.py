from . import utils as c_f
import logging
import inspect

class EasyModuleAttributeGetter:
    def get(self, obj_name, class_name=None, params=None, yaml_dict=None, additional_params=None, return_uninitialized=False):
        errors = []
        for module in getattr(self, obj_name):
            if class_name is None:
                (class_name, params), = yaml_dict.items()
            if params is None:
                params = {}
            if additional_params is not None:
                params = c_f.merge_two_dicts(params, additional_params)
            try:
                if inspect.ismodule(module):
                    uninitialized = getattr(module, class_name)
                elif inspect.isclass(module) and module.__name__ == class_name:
                    uninitialized = module
                else:
                    raise AttributeError("%s does not match %s"%(module, class_name))
                if return_uninitialized:
                    return uninitialized, params
                return uninitialized(**params)
            except AttributeError as e:
                errors.append(e)
        logging.error(errors)
        raise AttributeError

    def get_multiple(self, obj_name, yaml_dict, additional_params=None, return_uninitialized=None):
        output = {}
        for k, v in yaml_dict.items():
            additional_params = additional_params.get(k, None) if additional_params else None
            return_uninitialized = return_uninitialized.get(k, None) if return_uninitialized else None
            output[k] = self.get(obj_name, yaml_dict=v, additional_params=additional_params,
                                 return_uninitialized=return_uninitialized)
        return output

    def register(self, obj_name, new_module, prepend=True):
        assert inspect.ismodule(new_module) or inspect.isclass(new_module)
        curr = getattr(self, obj_name) if hasattr(self, obj_name) else []
        module_list = [new_module] + curr if prepend else curr + [new_module]
        setattr(self, obj_name, module_list)
