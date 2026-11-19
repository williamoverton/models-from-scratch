# Models from scratch

Learn how models work by building and training small ones from scratch.
This repository brings together hands-on experiments, readable implementations,
and a shared training dashboard. Understanding the concepts matters more than
model quality or production readiness.

## Model projects

| Project | What it explores |
| --- | --- |
| [Hello World](src/hello-world/) | A single linear neuron learning `y = 2x + 1`. |
| [Doggie Diffusion](src/doggie-diffusion/) | A diffusion model learning to generate dog images. |
| [Tool Calling](src/tool-calling/) | A language model learning to propose tool calls and answer from simulated results. |
| [NumPy LLM Stories](src/numpy-llm-stories/README.md) | A NumPy-only transformer for learning the math behind story generation. In design; model not implemented yet. |

Hello World, Doggie Diffusion, and Tool Calling use a terminal dashboard for training progress and loss.
Doggie Diffusion shows image previews; Tool Calling shows generated text examples.

## Getting started

You'll need Python, [uv](https://docs.astral.sh/uv/), and an NVIDIA GPU to run
the PyTorch projects. Follow the [development and setup guide](DEVELOMENT.md)
to prepare the environment, including the NixOS development shell.

From the repository root, launch a project:

```bash
uv run hello-world
```

or:

```bash
uv run doggie-diffusion
```

In Hello World, press **S** to start training and **Q** to quit.
For Tool Calling, follow its [data preparation and launch guide](src/tool-calling/README.md).

## Explore further

- [Shared tokenizer](libs/model-tokenizer/README.md): train a vocabulary for a
  text model and explore how text becomes token IDs.
- [Training dashboard](libs/model-training/README.md): shared training controls, metrics, and previews.
- [Learning experiments](scripts/): small console scripts for exploring
  individual concepts.
- [Design log](design-log/): the decisions behind the projects and shared tools.
- [Development guide](DEVELOMENT.md): environment setup, repository structure,
  and technical guidance.
