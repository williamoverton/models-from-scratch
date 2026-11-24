# Models from scratch

I build and train small AI models from scratch to investigate how they learn
under a tight compute budget. Most projects use PyTorch and target a single
NVIDIA GPU. The NumPy transformer takes a different approach: writing out the
backward pass so the gradients are visible in the code.

How far can a small model go? I use controlled examples where the expected
behavior is clear, then look at harder problems like image generation and tool
calling, where loss alone can't tell me whether the model is doing what I want.
The code, notebooks, and design notes are meant to be read and experimented with.

## Model projects

| Project | What it explores |
| --- | --- |
| [Hello World](src/hello-world/) | A single neuron fit to `y = 2x + 1`, a controlled example of gradient-based training. |
| [Doggie Diffusion](src/doggie-diffusion/README.md) | Pixel-space diffusion for 64×64 dog images, with fixed-seed comparisons of denoising steps and EMA weights. |
| [Tool Calling](src/tool-calling/README.md) | Text pretraining and synthetic tool-call training for a small language model that proposes a call and answers from the simulated result. |
| [NumPy LLM Stories](src/numpy-llm-stories/README.md) | A single-block causal transformer with hand-derived gradients, trained on three TinyStories examples in an interactive notebook. |

## Running the experiments

Start with the [development guide](DEVELOMENT.md) for Python, uv, and CUDA
setup. For a first run, follow the [Doggie Diffusion dataset preparation guide](src/doggie-diffusion/README.md#prepare-the-dataset),
then launch the training dashboard from the repository root:

```sh
uv run doggie-diffusion
```

## Shared tools and notes

- [Training dashboard](libs/model-training/README.md): terminal training controls, loss, and previews of generated images or text.
- [Tokenizer](libs/model-tokenizer/README.md): train a vocabulary and inspect how text maps to token IDs.
- [Console experiments](scripts/): smaller scripts for isolating pieces of a training run.
- [Design log](design-log/): decisions and tradeoffs behind the models and training runs.
