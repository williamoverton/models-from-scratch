import torch
from torch import nn

from model_training.progress import ProgressCallback, TrainingProgress


def train(
    model: nn.Module,
    *,
    steps: int,
    learning_rate: float,
    report_every: int,
    on_progress: ProgressCallback,
) -> None:
    """Train on y = 2x + 1 and publish progress after selected updates."""
    device = torch.device("cuda")
    model.to(device)
    model.train()

    x = torch.tensor([[0.0], [1.0], [2.0], [3.0]], device=device)
    y = torch.tensor([[1.0], [3.0], [5.0], [7.0]], device=device)

    loss_function = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

    for step in range(1, steps + 1):
        prediction = model(x)
        loss = loss_function(prediction, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if step % report_every == 0 or step == steps:
            on_progress(
                TrainingProgress(
                    step=step,
                    total_steps=steps,
                    metrics={"loss": loss.item()},
                )
            )
