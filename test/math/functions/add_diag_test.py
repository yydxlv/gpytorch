import math
import torch
from torch.autograd import Variable
from torch.nn import Parameter
from gpytorch.math.functions import AddDiag


def test_forward():
    a = Parameter(torch.Tensor([5]))
    b = Variable(torch.ones(3, 3))
    output = AddDiag()(b, a)

    actual = torch.Tensor([
        [6, 1, 1],
        [1, 6, 1],
        [1, 1, 6],
    ])
    assert(torch.norm(output.data - actual) < 1e-7)


def test_backward():
    grad = torch.randn(3, 3)

    a = Parameter(torch.Tensor([3]))
    b = Variable(torch.ones(3, 3), requires_grad=True)
    output = AddDiag()(b, a)
    output.backward(gradient=grad)

    assert(math.fabs(a.grad.data[0] - grad.trace()) < 1e-6)
    assert(torch.norm(b.grad.data - grad) < 1e-6)
