import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    from pathlib import Path
    from model_tokenizer import Tokenizer
    from html import escape
    from numpy_llm_stories.transformer import Transformer
    from numpy_llm_stories.stories import load_stories, encode_stories, training_batches

    return (
        Path,
        Tokenizer,
        Transformer,
        encode_stories,
        escape,
        load_stories,
        mo,
        np,
        training_batches,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Teach a tiny transformer three complete stories

    Train on the **first three complete stories from the real TinyStories training
    split**, then follow a prediction and generate a continuation. This is a small
    memorization experiment, not a full-dataset training run.

    **Tokens + positions → causal attention → feed-forward network → next token → repeat.**
    One NumPy decoder block, one head, 32 coordinates, up to 32 context tokens.
    All gradients remain explicit; model and dataset code live in
    `numpy_llm_stories/transformer.py` and `numpy_llm_stories/stories.py`.
    """)
    return


@app.cell(hide_code=True)
def _(Path, mo):
    mo.vstack([
        mo.md("## Transformer at a glance"),
        mo.image(
            Path(__file__).resolve().parents[1] / "transformer-block.png",
            alt="Transformer overview: token and position embeddings, one pre-norm decoder block with causal self-attention and feed-forward residual paths, final normalization, last-position readout, vocabulary scores and softmax.",
        ),
        mo.md("**Top:** one next-token prediction. **Bottom:** inside the decoder block; the two bypass arrows are residual additions. Causal attention cannot read future tokens. During generation, the chosen token is appended to the context and the top path repeats."),
        mo.md("Editable source: `diagrams/numpy-llm-transformer-block.tldraw`. The image describes the implemented architecture, not live attention values or training results."),
    ])
    return


@app.cell(hide_code=True)
def _(Path, Tokenizer, load_stories):
    tokenizer = Tokenizer.load(
        Path(__file__).resolve().parents[3] / "trained-models/tokenizers/simple-english.json"
    )
    context_size = 32
    embedding_width = 32
    end_of_document = tokenizer.control_token_ids["<END_OF_DOCUMENT>"]
    training_path = Path("/mnt/StorageBox/datasets/TinyStories/TinyStoriesV2-GPT4-train.txt")
    training_stories = load_stories(training_path, count=3)

    return (
        context_size,
        embedding_width,
        end_of_document,
        tokenizer,
        training_path,
        training_stories,
    )


@app.cell(hide_code=True)
def _(encode_stories, tokenizer, training_stories):
    story_sequences = encode_stories(training_stories, tokenizer)
    example_count = sum(len(sequence) - 1 for sequence in story_sequences)

    return example_count, story_sequences


@app.cell(hide_code=True)
def _(
    Transformer,
    context_size,
    embedding_width,
    epochs,
    example_count,
    learning_rate,
    mo,
    np,
    story_sequences,
    tokenizer,
    training_batches,
):
    initial_model = Transformer(tokenizer.vocab_size, context_size, embedding_width, seed=42)
    model = Transformer(tokenizer.vocab_size, context_size, embedding_width, seed=42)
    losses = []
    training_updates = 0
    _rng = np.random.default_rng(42)

    def _measure_loss():
        """Measure teacher-forced loss with the current fixed model over every target."""
        total = 0.0
        for inputs, labels in training_batches(story_sequences, context_size, 32, np.random.default_rng(0)):
            logits = model.forward(inputs)["logits"]
            shifted = logits - logits.max(axis=-1, keepdims=True)
            total += float((np.log(np.exp(shifted).sum(axis=-1)) - shifted[np.arange(len(labels)), labels]).sum())
        return total / example_count

    losses.append(_measure_loss())
    # Each epoch covers every target once; equal-length batches need no padding.
    for _epoch in mo.status.progress_bar(range(epochs.value), title="Learning three complete stories"):
        for _inputs, _labels in training_batches(story_sequences, context_size, 16, _rng):
            _loss, _gradients = model.loss_and_gradients(_inputs, _labels)
            model.step(_gradients, learning_rate.value)
            training_updates += 1
        losses.append(_measure_loss())

    return initial_model, losses, model, training_updates


@app.cell(hide_code=True)
def _(mo, training_stories):
    prompt = mo.ui.text_area(value=training_stories[0].split(".", 1)[0] + ".", label="Story prompt", full_width=True, debounce=True)
    mo.vstack([mo.md("## 1. Start a story\n\nThe initial prompt is an exact prefix of the first training story. Try a longer prefix copied from a story, then compare with a new opening. An empty prompt starts at the story boundary."), prompt])
    return (prompt,)


@app.cell(hide_code=True)
def _(
    context_size,
    end_of_document,
    initial_model,
    model,
    np,
    prompt,
    tokenizer,
):
    prompt_ids = [end_of_document] + tokenizer.encode(prompt.value)
    selected_ids = np.array(prompt_ids[-context_size:], dtype=np.int64)
    prediction = model.forward(selected_ids[None, :])
    trained_probabilities = prediction["probabilities"]
    initial_probabilities = initial_model.forward(selected_ids[None, :])["probabilities"]
    ranking = np.argsort(trained_probabilities[0])[::-1][:8]

    return (
        initial_probabilities,
        prediction,
        ranking,
        selected_ids,
        trained_probabilities,
    )


@app.cell(hide_code=True)
def _(
    escape,
    mo,
    prompt,
    ranking,
    tokenizer,
    trained_probabilities,
    training_updates,
):
    _suggested_id = int(ranking[0])
    _suggested_token = tokenizer.decode([_suggested_id])
    _probability = float(trained_probabilities[0, _suggested_id])
    mo.vstack([
        mo.md(f"### The model’s live suggestion\n\nNext token: **`{_suggested_token!r}`** · probability **{_probability:.2%}** · after **{training_updates} training updates**"),
        mo.Html(
            '<div style="border-left:4px solid #2563eb;padding:16px;font-size:22px;white-space:pre-wrap;overflow-wrap:anywhere">'
            + escape(prompt.value)
            + '<mark style="background:rgba(37,99,235,.18);color:inherit;border-bottom:2px solid #2563eb">'
            + escape(_suggested_token) + '</mark></div>'
        ),
        mo.md("The highlighted continuation is **one token**, chosen by highest probability—not a generated sentence. Its quoted spelling above makes whitespace visible. Edit the prompt or training controls to update it."),
    ])
    return


@app.cell(hide_code=True)
def _(escape, mo):
    def vector_heatmap(values, labels, scale):
        """Render signed coordinates using a shared symmetric color scale."""
        rows = []
        for label, vector in zip(labels, values):
            tiles = []
            for j, value in enumerate(vector):
                strength = min(abs(float(value)) / scale, 1.0)
                color = "37,99,235" if value >= 0 else "234,88,12"
                tiles.append(
                    f'<td title="coordinate {j}: {value:.5f}" '
                    f'style="background:rgba({color},{0.08 + 0.92 * strength:.3f});'
                    'min-width:22px;height:24px;border:2px solid var(--background);"></td>'
                )
            rows.append(f'<tr><th style="text-align:right;padding-right:12px;font-family:monospace;white-space:nowrap">{escape(label)}</th>{"".join(tiles)}</tr>')
        return mo.Html('<div style="overflow:auto;max-height:320px"><table style="border-collapse:collapse"><thead><tr><th></th>' + ''.join(f'<th style="font-size:10px">{j}</th>' for j in range(values.shape[1])) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')


    return (vector_heatmap,)


@app.cell(hide_code=True)
def _(context_size, escape, mo, selected_ids, tokenizer):
    _chips = []
    for _position, _id in enumerate(selected_ids):
        _label = escape(repr(tokenizer.decode([int(_id)])))
        _chips.append(f'<div style="border:1px solid #93c5fd;border-radius:10px;padding:10px 14px;background:rgba(37,99,235,.08)"><strong style="font-family:monospace">{_label}</strong><br><small>position {_position} · ID {int(_id)}</small></div>')
    mo.vstack([
        mo.md(f"### The model sees {len(selected_ids)} tokens, not words"),
        mo.Html('<div style="display:flex;flex-wrap:wrap;gap:8px;max-height:220px;overflow:auto">' + ''.join(_chips) + '</div>'),
        mo.md(f"Only the **last {context_size} tokens** are kept. Quotes make spaces and punctuation visible. A boundary token marks a fresh story before the prompt; it falls out of the window for long prompts. Spaces are real tokens too."),
    ])
    return


@app.cell(hide_code=True)
def _(mo, np, prediction, selected_ids, tokenizer, vector_heatmap):
    _tokens = prediction["token_embeddings"][0]
    _positioned = prediction["positioned_embeddings"][0]
    _scale = max(float(np.abs(_tokens).max()), float(np.abs(_positioned).max()), 1e-12)
    _labels = [f"{p}: {tokenizer.decode([int(i)])!r}" for p, i in enumerate(selected_ids)]
    mo.vstack([
        mo.md("## 2. Give each token a position\n\nThe same token ID selects the same token embedding. A **learned position embedding** is added to each row, so the model can distinguish where a token occurs."),
        mo.md("**Token embeddings**"),
        vector_heatmap(_tokens, _labels, _scale),
        mo.md(f"Orange = negative · blue = positive. Both grids share scale ±{_scale:.3f}; hover for values. Columns are the 32 learned coordinates, not named meanings."),
        mo.accordion({"See the embedding calculation": mo.md("```python\nx = token_embeddings[ids] + position_embeddings[:length]\n```")}),
    ])
    return


@app.cell(hide_code=True)
def _(mo, np, prediction, selected_ids, tokenizer, vector_heatmap):
    _tokens = prediction["token_embeddings"][0]
    _positioned = prediction["positioned_embeddings"][0]
    _scale = max(float(np.abs(_tokens).max()), float(np.abs(_positioned).max()), 1e-12)
    _labels = [f"{p}: {tokenizer.decode([int(i)])!r}" for p, i in enumerate(selected_ids)]
    mo.vstack([
        mo.md("### Add position information\n\nCompare these rows with the token-only rows above. Repeated spaces can now have different representations because their positions differ."),
        vector_heatmap(_positioned, _labels, _scale),
        mo.md(f"Token + position embeddings. Shared input-grid scale: ±{_scale:.3f}."),
    ])
    return


@app.cell(hide_code=True)
def _(escape, mo, prediction, selected_ids, tokenizer):
    _attention = prediction["attention"][0]
    _rows = []
    for _q, _weights in enumerate(_attention):
        _tiles = []
        for _k, _weight in enumerate(_weights):
            _masked = _k > _q
            _color = "rgba(128,128,128,.12)" if _masked else f"rgba(37,99,235,{0.05 + .95 * float(_weight):.3f})"
            _text = "×" if _masked else f"{_weight:.0%}"
            _tiles.append(f'<td title="query {_q}, key {_k}: {_weight:.5f}" style="background:{_color};padding:5px;min-width:42px;text-align:center">{_text}</td>')
        _label = escape(f"{_q}: {tokenizer.decode([int(selected_ids[_q])])!r}")
        _rows.append(f'<tr><th style="text-align:right;padding-right:8px;font-family:monospace">{_label}</th>{"".join(_tiles)}</tr>')
    _head = ''.join(f'<th>{p}</th>' for p in range(len(selected_ids)))
    mo.vstack([
        mo.md("## 3. Mix information with causal self-attention\n\n**Rows ask; columns supply information.** Each row sums to 100%. A token can attend to itself and earlier positions, never future positions (×). These are learned mixing weights—not explanations of word meaning."),
        mo.Html('<div style="overflow:auto;max-height:320px"><table><thead><tr><th>query ↓ / key →</th>' + _head + '</tr></thead><tbody>' + ''.join(_rows) + '</tbody></table></div>'),
        mo.accordion({"See the attention calculation": mo.md("```python\nz = layer_norm(x)\nq, k, v = z @ Wq, z @ Wk, z @ Wv\nscores = q @ k.swapaxes(-1, -2) / np.sqrt(width)\nscores[..., future_positions] = -np.inf\nattention = softmax(scores)\nx = x + (attention @ v) @ Wo\nx = x + feed_forward(layer_norm(x))\nhidden = final_layer_norm(x)\n```\nThe feed-forward network acts on each row independently: 32 → 128 → 32 coordinates with tanh activation. Residual additions preserve a path for the incoming information; layer normalization stabilizes each row's scale.")}),
    ])
    return


@app.cell(hide_code=True)
def _(mo, np, prediction, vector_heatmap):
    _last = prediction["hidden"][:, -1, :]
    _scale = max(float(np.abs(_last).max()), 1e-12)
    mo.vstack([
        mo.md("### Read the final position\n\nAfter attention, the residual feed-forward network, and final normalization, the **last row** summarizes the available context for the next-token prediction. We do not average the rows."),
        vector_heatmap(_last, ["last position"], _scale),
        mo.md(f"Signed scale ±{_scale:.3f}, separate from the input grids. This 32-coordinate vector feeds the vocabulary output layer."),
    ])
    return


@app.cell(hide_code=True)
def _(
    escape,
    initial_probabilities,
    mo,
    ranking,
    tokenizer,
    trained_probabilities,
):
    _bars = []
    for _id in ranking:
        _before = float(initial_probabilities[0, _id])
        _after = float(trained_probabilities[0, _id])
        _bars.append(f'<div style="margin:12px 0"><strong style="font-family:monospace">{escape(repr(tokenizer.decode([int(_id)])))}</strong><div style="display:flex;align-items:center;gap:8px"><div style="flex:1;background:rgba(128,128,128,.12)"><div style="width:{100 * _before:.5f}%;height:7px;background:#94a3b8"></div><div style="width:{100 * _after:.5f}%;height:12px;background:#2563eb"></div></div><span style="min-width:140px;font-size:12px">{_before:.2%} → {_after:.2%}</span></div></div>')
    mo.vstack([
        mo.md(f"## 4. Turn the vector into a prediction\n\nA learned matrix and bias produce **{tokenizer.vocab_size} scores**. Softmax converts them into probabilities that sum to 100%. Here are the eight highest **after training**."),
        mo.Html('<div>' + ''.join(_bars) + '</div>'),
        mo.md("**Gray = before training · blue = after training.** Bar tracks represent 0–100%, not a rescaled top-eight total. Other vocabulary tokens still hold the remaining probability. A high probability is a model preference, not a guarantee."),
        mo.accordion({"See the score and probability calculation": mo.md("```python\nlogits = hidden[:, -1, :] @ output_weights + output_bias\nshifted = logits - logits.max()\nprobabilities = np.exp(shifted) / np.exp(shifted).sum()\n```")}),
    ])
    return


@app.cell(hide_code=True)
def _(escape, mo, story_sequences, training_stories):
    epochs = mo.ui.slider(0, 200, step=10, value=80, label="Passes through all three stories", show_value=True)
    learning_rate = mo.ui.slider(0.001, 0.01, step=0.001, value=0.003, label="Adam learning rate", show_value=True)
    mo.vstack([
        mo.md("## 5. Learn from complete TinyStories\n\nEvery pass visits **all next-token targets in all three stories**, including their endings. Training never joins unrelated story text. Changing these controls resets the seeded model and trains again; prompt and generation controls do not retrain."),
        mo.hstack([epochs, learning_rate]),
        mo.accordion({f"Story {i + 1} · {len(sequence) - 2} text tokens": mo.Html('<pre style="white-space:pre-wrap;max-height:360px;overflow:auto">' + escape(text) + '</pre>') for i, (text, sequence) in enumerate(zip(training_stories, story_sequences))}),
    ])
    return epochs, learning_rate


@app.cell(hide_code=True)
def _(context_size, example_count, mo, training_path, training_stories):
    mo.md(f"""
    ### Where do the answers come from?

    **{len(training_stories)} whole stories · {example_count:,} next-token examples per pass.**
    Source: `{training_path.name}`. Validation stories are not loaded.

    Each story is encoded as **boundary → story tokens → boundary**. The first
    boundary supplies context for the first token; the last is the learned stop
    signal. Each target sees up to {context_size} preceding tokens from that story,
    including shorter opening prefixes. No examples cross between stories.

    Mini-batches hold up to 16 examples of the same context length, so no padding
    or padding mask is needed. Examples and batch order are shuffled each pass.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### What changes during learning?

    Cross-entropy measures the negative log probability of the correct next token,
    averaged across examples. Explicit backpropagation computes gradients through
    attention, the feed-forward network, normalization, and both embedding tables.
    **Adam** uses running gradient moments to update every trainable parameter.
    Changing training settings starts from the same seeded weights. Editing only
    the prompt or generation length does not retrain. Each pass visits every target,
    not just a random excerpt.
    """)
    return


@app.cell(hide_code=True)
def _(epochs, example_count, losses, mo, training_updates):
    # Draw the loss directly from the values produced by the training loop.
    _width, _height = 600, 140
    _low, _high = min(losses), max(losses)
    _span = max(_high - _low, 1e-9)
    _points = " ".join(
        f"{10 + i / max(len(losses) - 1, 1) * 580:.1f},{10 + (_high - loss) / _span * 110:.1f}"
        for i, loss in enumerate(losses)
    )
    mo.vstack([
        mo.md(f"**Loss: {losses[0]:.3f} → {losses[-1]:.3f}** after {len(losses) - 1} complete passes ({training_updates:,} Adam updates; {example_count * epochs.value:,} next-token examples processed). Measured over every training target with fixed weights after each pass. Higher means worse; this is training loss, not validation loss."),
        mo.Html(f'<svg viewBox="0 0 {_width} {_height}" role="img" aria-label="Training loss"><polyline points="{_points}" fill="none" stroke="#2563eb" stroke-width="3"/></svg>'),
    ])
    return


@app.cell(hide_code=True)
def _(
    escape,
    mo,
    prompt,
    ranking,
    tokenizer,
    trained_probabilities,
    training_updates,
):
    _token_id = int(ranking[0])
    _token = tokenizer.decode([_token_id])
    _probability = float(trained_probabilities[0, _token_id])
    mo.vstack([
        mo.md("### Next-token prediction after training"),
        mo.Html('<p>For prompt <code style="white-space:pre-wrap">' + escape(prompt.value) + '</code></p>'),
        mo.Html('<div style="border-left:4px solid #2563eb;padding:16px"><strong style="font-size:24px;font-family:monospace;white-space:pre-wrap">' + escape(repr(_token)) + '</strong>' + f'<p>Probability: <strong>{_probability:.2%}</strong> · token ID {_token_id} · {training_updates} training updates</p></div>'),
        mo.md("This is the trained model’s highest-probability **next token** for the prediction prompt above. Quotes make spaces visible. Change the training controls to see this prediction update."),
    ])
    return


@app.cell
def _(np):
    def continue_story(model, tokenizer, prompt_text, token_limit):
        """Greedily predict tokens with a rolling context until EOD or the limit."""
        boundary = tokenizer.control_token_ids["<END_OF_DOCUMENT>"]
        history = [boundary] + tokenizer.encode(prompt_text)
        generated = []
        for _ in range(token_limit):
            inputs = np.array(history[-model.context_size:], dtype=np.int64)[None, :]
            probabilities = model.forward(inputs)["probabilities"][0]
            token_id = int(probabilities.argmax())
            if token_id == boundary:
                return generated, True
            generated.append(token_id)
            history.append(token_id)
        return generated, False


    return (continue_story,)


@app.cell(hide_code=True)
def _(mo):
    generation_limit = mo.ui.slider(20, 400, step=20, value=400, label="Maximum new tokens", show_value=True)
    mo.vstack([mo.md("## 6. Let the trained model continue the story"), generation_limit])
    return (generation_limit,)


@app.cell(hide_code=True)
def _(continue_story, escape, generation_limit, mo, model, prompt, tokenizer):
    generated_ids, reached_end = continue_story(model, tokenizer, prompt.value, generation_limit.value)
    continuation = tokenizer.decode(generated_ids, skip_control_tokens=True)
    mo.vstack([
        mo.Html('<div style="border-left:4px solid #2563eb;padding:16px;max-height:360px;overflow:auto;white-space:pre-wrap;font-size:18px">' + escape(prompt.value) + '<span style="background:rgba(37,99,235,.12)">' + escape(continuation) + '</span></div>'),
        mo.md(f"**{len(generated_ids)} new tokens** · " + ("stopped at **`<END_OF_DOCUMENT>`**." if reached_end else "stopped at the **token limit**, not a learned ending.")),
        mo.md("Highlighted text is generated, not copied from the dataset. At each step the model chooses its highest-probability token, appends it, and predicts again using the latest 32 tokens. The output is deterministic; no sampling or repetition fixes hide what the model learned."),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 7. Explore memorization versus generation

    1. Start from the supplied story prefix. Increase complete training passes and compare continuations.
    2. Copy a later passage from one training story into the prompt. Does it recover what followed?
    3. Try a new opening. Repetition and mixed-up characters expose the difference between fitting three stories and learning language.

    Training always supplies the real preceding tokens (**teacher forcing**).
    Generation supplies the model's own predictions, so one mistake can send it
    into unfamiliar contexts. The 32-token window also forgets earlier story details.
    All weights stay in this notebook session; this is not full-corpus training.
    """)
    return


if __name__ == "__main__":
    app.run()
