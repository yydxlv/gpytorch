import math
import torch
import numpy as np
from torch.autograd import Variable
from gpytorch.math.functions import ExactGPMarginalLogLikelihood

covar = torch.Tensor([
    [5, -3, 0],
    [-3, 5, 0],
    [0, 0, 2],
])
y = torch.randn(3)


def test_forward():
    actual = y.dot(covar.inverse().mv(y))
    actual += math.log(np.linalg.det(covar.numpy()))
    actual += math.log(2 * math.pi) * len(y)
    actual *= -0.5

    covarvar = Variable(covar)
    yvar = Variable(y)
    res = ExactGPMarginalLogLikelihood()(covarvar, yvar)
    assert(torch.norm(actual - res.data) < 1e-4)


def test_backward():
    covarvar = Variable(covar, requires_grad=True)
    yvar = Variable(y, requires_grad=True)
    actual_mat_grad = torch.ger(covar.inverse().mv(y), covar.inverse().mv(y))
    actual_mat_grad -= covar.inverse()
    actual_mat_grad *= 0.5
    actual_mat_grad *= 3  # For grad output

    actual_y_grad = -covar.inverse().mv(y)
    actual_y_grad *= 3  # For grad output

    covarvar = Variable(covar, requires_grad=True)
    yvar = Variable(y, requires_grad=True)
    output = ExactGPMarginalLogLikelihood()(covarvar, yvar) * 3
    output.backward()

    print(actual_mat_grad, covarvar.grad.data)
    assert(torch.norm(actual_mat_grad - covarvar.grad.data) < 1e-4)
    assert(torch.norm(actual_y_grad - yvar.grad.data) < 1e-4)
