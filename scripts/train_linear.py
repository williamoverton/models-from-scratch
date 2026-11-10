"""Train a single linear neuron on y = 2x + 1, without the TUI."""

import torch
from torch import nn


# Each row is one example with one input feature.
x = torch.tensor([[0.0], [1.0], [2.0], [3.0]])
y = torch.tensor([[1.0], [3.0], [5.0], [7.0]])

model = nn.Linear(in_features=1, out_features=1)
loss_function = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

for step in range(200):
    prediction = model(x)
    loss = loss_function(prediction, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # This loss was computed before the parameter update above.
    if step % 20 == 0:
        print(f"Step {step}: loss = {loss.item():.6f}")

print(f"Weight: {model.weight.item():.4f}")
print(f"Bias:   {model.bias.item():.4f}")
