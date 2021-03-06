from torch.autograd import Variable
from torch.nn import Module, Parameter
from gpytorch.random_variables import RandomVariable
from gpytorch.parameters import ParameterGroup


class Distribution(Module):
    def __init__(self):
        super(Distribution, self).__init__()
        self._parameter_groups = {}

    def forward(self, *inputs, **kwargs):
        raise NotImplementedError

    def __call__(self, *inputs, **kwargs):
        for input in inputs:
            if not(isinstance(input, RandomVariable) or isinstance(input, Variable)):
                print(type(input))
                raise RuntimeError('Input must be a RandomVariable or Variable, was a %s' %
                                   input.__class__.__name__)
        outputs = self.forward(*inputs, **kwargs)
        if isinstance(outputs, Variable) or isinstance(outputs, RandomVariable):
            return outputs

        for output in outputs:
            if not (isinstance(output, RandomVariable) or isinstance(output, Variable)):
                raise RuntimeError('Output must be a RandomVariable or Variable, was a %s' %
                                   input.__class__.__name__)
        if len(outputs) == 1:
            outputs = outputs[0]
        return outputs

    def __setattr__(self, name, value):
        if isinstance(value, Parameter):
            raise RuntimeError('Observation Models expect ParameterGroups, not Parameters directly.')
        if isinstance(value, ParameterGroup):
            self._parameter_groups[name] = value
        super(Distribution, self).__setattr__(name, value)

    def __getattr__(self, name):
        for group_name, param_group in self.named_parameter_groups():
            if group_name == name:
                return param_group

        return super(Distribution, self).__getattr__(name)

    def parameter_groups(self):
        for name, param_group in self.named_parameter_groups():
            yield param_group

    def named_parameter_groups(self):
        for name, param_group in self._parameter_groups.items():
            yield name, param_group

        for child in self.children():
            if isinstance(child, Distribution):
                for name, param_group in child.named_parameter_groups():
                    yield name, param_group
