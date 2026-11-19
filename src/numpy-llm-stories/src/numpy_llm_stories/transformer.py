"""A single decoder transformer block, including NumPy-only backpropagation."""

import numpy as np


class Transformer:
    """Learn next-token probabilities from equal-length, padding-free contexts.

    Each block uses pre-layer normalization, single-head causal attention, and a
    tanh feedforward network with four times the model width. The final position
    supplies the next-token prediction; there is no pooling over positions.
    """

    def __init__(self, vocab_size, context_size=8, width=16, seed=42):
        """Initialize learned parameters and empty Adam moments from a fixed seed."""
        if vocab_size < 1 or context_size < 1 or width < 1:
            raise ValueError("vocab_size, context_size, and width must be positive")
        self.vocab_size = vocab_size
        self.context_size = context_size
        self.width = width
        rng = np.random.default_rng(seed)

        def weights(fan_in, fan_out):
            """Initialize a projection with inverse-square-root input scaling."""
            return rng.normal(0.0, fan_in**-0.5, (fan_in, fan_out))

        self.parameters = {
            "token_embeddings": rng.normal(0.0, 0.1, (vocab_size, width)),
            "position_embeddings": rng.normal(0.0, 0.1, (context_size, width)),
            "attention_norm_scale": np.ones(width),
            "attention_norm_bias": np.zeros(width),
            "query_weights": weights(width, width),
            "query_bias": np.zeros(width),
            "key_weights": weights(width, width),
            "key_bias": np.zeros(width),
            "value_weights": weights(width, width),
            "value_bias": np.zeros(width),
            "attention_output_weights": weights(width, width),
            "attention_output_bias": np.zeros(width),
            "feedforward_norm_scale": np.ones(width),
            "feedforward_norm_bias": np.zeros(width),
            "feedforward_input_weights": weights(width, 4 * width),
            "feedforward_input_bias": np.zeros(4 * width),
            "feedforward_output_weights": weights(4 * width, width),
            "feedforward_output_bias": np.zeros(width),
            "final_norm_scale": np.ones(width),
            "final_norm_bias": np.zeros(width),
            "output_weights": weights(width, vocab_size),
            "output_bias": np.zeros(vocab_size),
        }
        self._causal_mask = np.triu(
            np.ones((context_size, context_size), dtype=bool), k=1
        )
        self._attention_scale = width**-0.5
        self._first_moments = {
            name: np.zeros_like(value) for name, value in self.parameters.items()
        }
        self._second_moments = {
            name: np.zeros_like(value) for name, value in self.parameters.items()
        }
        self._updates = 0

    @staticmethod
    def _layer_norm(values, scale, bias):
        """Normalize each token's coordinates and retain the backward intermediates."""
        centered = values - values.mean(axis=-1, keepdims=True)
        inverse_std = 1.0 / np.sqrt(
            np.mean(centered * centered, axis=-1, keepdims=True) + 1e-5
        )
        normalized = centered * inverse_std
        return normalized * scale + bias, (normalized, inverse_std)

    @staticmethod
    def _layer_norm_backward(gradient, scale, cache):
        """Differentiate layer normalization with respect to inputs, scale, and bias."""
        normalized, inverse_std = cache
        axes = tuple(range(gradient.ndim - 1))
        scale_gradient = np.sum(gradient * normalized, axis=axes)
        bias_gradient = gradient.sum(axis=axes)
        normalized_gradient = gradient * scale
        # The mean and variance both depend on every coordinate in this token.
        input_gradient = inverse_std * (
            normalized_gradient
            - normalized_gradient.mean(axis=-1, keepdims=True)
            - normalized
            * np.mean(normalized_gradient * normalized, axis=-1, keepdims=True)
        )
        return input_gradient, scale_gradient, bias_gradient

    @staticmethod
    def _linear_backward(gradient, inputs, weights):
        """Differentiate a shared affine projection across batch and token axes."""
        flat_gradient = gradient.reshape(-1, gradient.shape[-1])
        flat_inputs = inputs.reshape(-1, inputs.shape[-1])
        return (
            gradient @ weights.T,
            flat_inputs.T @ flat_gradient,
            flat_gradient.sum(axis=0),
        )

    def _forward(self, ids):
        """Compute decoder outputs and intermediates needed for explicit backpropagation."""
        ids = np.asarray(ids)
        if ids.ndim != 2 or ids.shape[0] == 0:
            raise ValueError("ids must have shape (batch, sequence) with a nonempty batch")
        length = ids.shape[1]
        if not 1 <= length <= self.context_size:
            raise ValueError("sequence length must be between 1 and context_size")
        if not np.issubdtype(ids.dtype, np.integer):
            raise TypeError("ids must contain integer token IDs")
        if np.any(ids < 0) or np.any(ids >= self.vocab_size):
            raise ValueError("token IDs must be within the vocabulary")

        p = self.parameters
        token_embeddings = p["token_embeddings"][ids]
        positioned = token_embeddings + p["position_embeddings"][:length]
        attention_input, attention_norm = self._layer_norm(
            positioned, p["attention_norm_scale"], p["attention_norm_bias"]
        )
        queries = attention_input @ p["query_weights"] + p["query_bias"]
        keys = attention_input @ p["key_weights"] + p["key_bias"]
        values = attention_input @ p["value_weights"] + p["value_bias"]
        scores = (queries @ keys.swapaxes(-1, -2)) * self._attention_scale
        scores[:, self._causal_mask[:length, :length]] = -np.inf
        scores -= scores.max(axis=-1, keepdims=True)
        attention = np.exp(scores)
        attention /= attention.sum(axis=-1, keepdims=True)
        attended = attention @ values
        after_attention = (
            positioned
            + attended @ p["attention_output_weights"]
            + p["attention_output_bias"]
        )
        feedforward_input, feedforward_norm = self._layer_norm(
            after_attention, p["feedforward_norm_scale"], p["feedforward_norm_bias"]
        )
        activation = np.tanh(
            feedforward_input @ p["feedforward_input_weights"]
            + p["feedforward_input_bias"]
        )
        after_feedforward = (
            after_attention
            + activation @ p["feedforward_output_weights"]
            + p["feedforward_output_bias"]
        )
        hidden, final_norm = self._layer_norm(
            after_feedforward, p["final_norm_scale"], p["final_norm_bias"]
        )
        logits = hidden[:, -1, :] @ p["output_weights"] + p["output_bias"]
        shifted_logits = logits - logits.max(axis=-1, keepdims=True)
        probabilities = np.exp(shifted_logits)
        probabilities /= probabilities.sum(axis=-1, keepdims=True)
        outputs = {
            "probabilities": probabilities,
            "attention": attention,
            "token_embeddings": token_embeddings,
            "positioned_embeddings": positioned,
            "hidden": hidden,
            "logits": logits,
        }
        cache = {
            "ids": ids,
            "attention_input": attention_input,
            "attention_norm": attention_norm,
            "queries": queries,
            "keys": keys,
            "values": values,
            "attended": attended,
            "feedforward_input": feedforward_input,
            "feedforward_norm": feedforward_norm,
            "activation": activation,
            "final_norm": final_norm,
            "shifted_logits": shifted_logits,
        }
        return outputs, cache

    def forward(self, ids):
        """Return inspection arrays for integer IDs of shape (B, T), 1 <= T <= C.

        Probabilities and logits have shape (B, V), attention (B, T, T), and
        token/positioned embeddings and final normalized hidden states (B, T, D).
        Future-position attention weights are exactly zero.
        """
        outputs, _ = self._forward(ids)
        return outputs

    def loss_and_gradients(self, ids, targets):
        """Return mean next-token cross entropy and every parameter's gradient.

        Targets have shape (B,). Differentiation is explicit, including embedding
        accumulation, attention softmax, both residual paths, and all layer norms.
        This method does not change parameters or Adam state.
        """
        outputs, cache = self._forward(ids)
        targets = np.asarray(targets)
        batch = outputs["logits"].shape[0]
        if targets.shape != (batch,):
            raise ValueError("targets must have shape (batch,)")
        if not np.issubdtype(targets.dtype, np.integer):
            raise TypeError("targets must contain integer token IDs")
        if np.any(targets < 0) or np.any(targets >= self.vocab_size):
            raise ValueError("target IDs must be within the vocabulary")
        rows = np.arange(batch)
        shifted_logits = cache["shifted_logits"]
        # Log-sum-exp avoids taking log of an underflowed target probability.
        loss = np.mean(
            np.log(np.exp(shifted_logits).sum(axis=-1))
            - shifted_logits[rows, targets]
        )
        p = self.parameters
        gradients = {}
        score_gradient = outputs["probabilities"].copy()
        score_gradient[rows, targets] -= 1.0
        score_gradient /= batch
        last_gradient, gradients["output_weights"], gradients["output_bias"] = (
            self._linear_backward(score_gradient, outputs["hidden"][:, -1, :], p["output_weights"])
        )
        hidden_gradient = np.zeros_like(outputs["hidden"])
        hidden_gradient[:, -1, :] = last_gradient
        residual_gradient, gradients["final_norm_scale"], gradients["final_norm_bias"] = (
            self._layer_norm_backward(hidden_gradient, p["final_norm_scale"], cache["final_norm"])
        )
        activation_gradient, gradients["feedforward_output_weights"], gradients["feedforward_output_bias"] = (
            self._linear_backward(
                residual_gradient, cache["activation"], p["feedforward_output_weights"]
            )
        )
        activation_gradient *= 1.0 - cache["activation"] ** 2
        feedforward_gradient, gradients["feedforward_input_weights"], gradients["feedforward_input_bias"] = (
            self._linear_backward(
                activation_gradient,
                cache["feedforward_input"],
                p["feedforward_input_weights"],
            )
        )
        norm_gradient, gradients["feedforward_norm_scale"], gradients["feedforward_norm_bias"] = (
            self._layer_norm_backward(
                feedforward_gradient, p["feedforward_norm_scale"], cache["feedforward_norm"]
            )
        )
        residual_gradient += norm_gradient
        attended_gradient, gradients["attention_output_weights"], gradients["attention_output_bias"] = (
            self._linear_backward(
                residual_gradient, cache["attended"], p["attention_output_weights"]
            )
        )
        attention = outputs["attention"]
        attention_gradient = attended_gradient @ cache["values"].swapaxes(-1, -2)
        value_gradient = attention.swapaxes(-1, -2) @ attended_gradient
        # Softmax Jacobian-vector product; masked entries remain exactly zero.
        attention_score_gradient = attention * (
            attention_gradient
            - np.sum(attention_gradient * attention, axis=-1, keepdims=True)
        )
        attention_score_gradient *= self._attention_scale
        query_gradient = attention_score_gradient @ cache["keys"]
        key_gradient = attention_score_gradient.swapaxes(-1, -2) @ cache["queries"]
        attention_input_gradient = np.zeros_like(cache["attention_input"])
        for name, gradient in (
            ("query", query_gradient),
            ("key", key_gradient),
            ("value", value_gradient),
        ):
            input_gradient, gradients[f"{name}_weights"], gradients[f"{name}_bias"] = (
                self._linear_backward(gradient, cache["attention_input"], p[f"{name}_weights"])
            )
            attention_input_gradient += input_gradient
        norm_gradient, gradients["attention_norm_scale"], gradients["attention_norm_bias"] = (
            self._layer_norm_backward(
                attention_input_gradient, p["attention_norm_scale"], cache["attention_norm"]
            )
        )
        residual_gradient += norm_gradient
        gradients["token_embeddings"] = np.zeros_like(p["token_embeddings"])
        # Repeated IDs must accumulate, rather than overwrite, their contributions.
        np.add.at(gradients["token_embeddings"], cache["ids"], residual_gradient)
        gradients["position_embeddings"] = np.zeros_like(p["position_embeddings"])
        gradients["position_embeddings"][: cache["ids"].shape[1]] = residual_gradient.sum(axis=0)
        return float(loss), gradients

    def step(self, gradients, learning_rate):
        """Apply one bias-corrected Adam update in place (betas 0.9 and 0.999)."""
        self._updates += 1
        first_correction = 1.0 - 0.9**self._updates
        second_correction = 1.0 - 0.999**self._updates
        for name, parameter in self.parameters.items():
            gradient = gradients[name]
            first = self._first_moments[name]
            second = self._second_moments[name]
            first *= 0.9
            first += 0.1 * gradient
            second *= 0.999
            second += 0.001 * gradient * gradient
            parameter -= learning_rate * (first / first_correction) / (
                np.sqrt(second / second_correction) + 1e-8
            )
