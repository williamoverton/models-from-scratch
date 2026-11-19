# Finding and Invoking marimo in This Repository

This skill is notebook-generic but repository-specific. Use this repository's
Nix development shell and uv workspace for every launch. Do not substitute a
global marimo install, `uvx marimo@latest`, or another environment.

## Select the notebook and discover first

1. Use a supplied notebook URL directly. Otherwise locate the notebook matching
   the user's request using repository search and its component README.
2. Discover existing servers before starting another:

   ```bash
   bash "$(realpath skill://marimo-pair)/scripts/discover-servers.sh"
   ```

3. Reuse a server hosting the requested notebook. Discovery lists servers, not
   notebook identities; use session discovery to select the correct notebook.
   With several notebooks open, pass the exact `--file` key reported by the
   execute script. Do not connect to an unrelated notebook just because it is
   the only active session.
4. If no suitable server exists, launch the selected notebook as below.

Only servers started with `--no-token` register for discovery. For an existing
authenticated server, use its supplied URL and `MARIMO_TOKEN`; do not restart
it merely to disable authentication.

## Launch through Nix and uv

Run from the repository root. Read the selected notebook's component README
and `pyproject.toml` to identify its uv package and required extras. Preserve
the documented dependency options rather than assuming every model project
uses the same package or extras.

The current NumPy LLM Stories notebooks use:

```bash
nix develop path:. --command uv run \
  --package numpy-llm-stories --extra marimo --extra notebooks \
  marimo edit <notebook-path> \
  --host 127.0.0.1 --port 2718 --no-token
```

Replace `<notebook-path>` with the selected repository-relative path; it is not
a literal argument. For example, a request for the next-token predictor selects
`src/numpy-llm-stories/notebooks/03-next-token-predictor.py`, not a default for
other requests.

Use an available local port if 2718 is already occupied; do not stop an existing
server to reclaim it. Keep the server running in a managed long-lived terminal
and observe its printed URL. Do not pass `--headless`: the browser UI must be
open before there is an active notebook session to connect to. If browser
opening fails, open the printed URL using the available browser tooling.

When the developer-in-the-loop workflow is active, show the runnable command
with the selected notebook path and ask who should run it at the first launch
of the session. Follow the developer's preference thereafter.

## Notebooks with PEP 723 metadata

Before launch, read the selected notebook's header. A `# /// script` block
declares inline dependencies and requires `--sandbox`. Add that flag to the
repository's Nix/uv launch command; do not silently ignore the metadata or
replace the repository runner. Without inline metadata, use the package's
workspace dependencies and extras without `--sandbox`.

## Connect to the live kernel

After the notebook UI is open, rediscover the server and use its reported URL.
Resolve scripts through `realpath`, and run the required first kernel command:

```bash
bash "$(realpath skill://marimo-pair)/scripts/execute-code.sh" \
  --url <discovered-url> \
  -c "import marimo._code_mode as cm; help(cm)"
```

Replace `<discovered-url>` with the actual URL. Add `--file` with the exact
reported file key when needed to select the requested notebook. Wait for
successful `help(cm)` output before any task-specific code-mode operations.
Connecting does not authorize editing cells or running training.

See [execution-context.md](execution-context.md) for authentication, session
selection, and connection errors.
