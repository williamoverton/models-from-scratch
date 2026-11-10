from torch import nn


def create_model() -> nn.Linear:
    """Create a linear neuron with one input, one output, and a learnable bias."""
    return nn.Linear(in_features=1, out_features=1)
