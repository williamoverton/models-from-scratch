# Doggie Diffusion

Keep model-specific usage and dataset preparation instructions in this
folder's README.md, not the repository-wide README.md. The global README is
for high-level repository information, not detailed model instructions.

This is a learning-first, from-scratch random dog generator targeting 64×64 RGB
images on a single RTX 2080. Preserve the developer-in-the-loop workflow:
discuss design decisions before implementation and do not treat agreement as
permission to implement.

Read README.md and the relevant design log before changing the model. The
initial decision log is ../../design-log/2026-11-10-doggy-diffusion.md; its
proposed details are not approved decisions. Use the directory spelling
`doggie-diffusion` requested by the user.

Dataset originals live in /mnt/StorageBox/datasets/SDIP_dog/data/; the generated
64×64 version lives in /mnt/StorageBox/datasets/SDIP_dog/64x64/. Never overwrite
originals. The reusable conversion script lives at
../../scripts/prepare_dog_images.py. Train on all 126,841 prepared images with
shuffled data. Measure progress and run length by optimizer steps, not epochs.
Load Parquet data in bounded portions and decode images as needed for batches;
never preload the complete dataset into RAM or GPU memory. See
../../design-log/2026-11-11-doggie-diffusion-full-dataset.md for the decision
superseding the initial 10,000-image subset.

Keep diffusion, data, model settings, and training logic in this project;
shared dashboard code must remain model-independent. Follow the root project
rules for CUDA use, simple PyTorch components, and verification permissions.
