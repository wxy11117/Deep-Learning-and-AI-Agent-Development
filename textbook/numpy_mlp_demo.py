"""A small reproducible MLP, analytic gradients, and finite-difference check."""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parent


def dataset(rng, n):
    x = rng.uniform(-1.5, 1.5, (n, 2))
    y = (np.sum(x * x, axis=1) > 1.0).astype(np.int64)
    return x, y


def forward(x, p):
    h = np.tanh(x @ p["w1"] + p["b1"])
    logits = h @ p["w2"] + p["b2"]
    shifted = logits - logits.max(axis=1, keepdims=True)
    log_probs = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
    return h, log_probs


def loss_grads(x, y, p):
    h, logp = forward(x, p)
    loss = -logp[np.arange(len(y)), y].mean()
    dz = np.exp(logp)
    dz[np.arange(len(y)), y] -= 1
    dz /= len(y)
    dh = (dz @ p["w2"].T) * (1 - h * h)
    grads = {
        "w2": h.T @ dz, "b2": dz.sum(axis=0),
        "w1": x.T @ dh, "b1": dh.sum(axis=0),
    }
    return float(loss), grads


def evaluate(x, y, p):
    _, logp = forward(x, p)
    return float(-logp[np.arange(len(y)), y].mean()), float(
        (logp.argmax(axis=1) == y).mean()
    )


def main():
    rng = np.random.default_rng(42)
    xtr, ytr = dataset(rng, 1000)
    xva, yva = dataset(rng, 400)
    xte, yte = dataset(rng, 800)
    mean, std = xtr.mean(axis=0), xtr.std(axis=0)
    xtr, xva, xte = [(x - mean) / std for x in (xtr, xva, xte)]
    p = {
        "w1": rng.normal(0, np.sqrt(1 / 2), (2, 32)),
        "b1": np.zeros(32),
        "w2": rng.normal(0, np.sqrt(1 / 32), (32, 2)),
        "b2": np.zeros(2),
    }
    _, analytic = loss_grads(xtr[:7], ytr[:7], p)
    errors = []
    eps = 1e-5
    for key in p:
        for j in rng.choice(p[key].size, min(8, p[key].size), replace=False):
            original = p[key].flat[j]
            p[key].flat[j] = original + eps
            plus = loss_grads(xtr[:7], ytr[:7], p)[0]
            p[key].flat[j] = original - eps
            minus = loss_grads(xtr[:7], ytr[:7], p)[0]
            p[key].flat[j] = original
            errors.append(abs((plus - minus) / (2 * eps) - analytic[key].flat[j]))
    assert max(errors) < 1e-7, max(errors)
    history = []
    best_loss = float("inf")
    best, best_epoch = None, None
    for epoch in range(1, 301):
        order = rng.permutation(len(ytr))
        learning_rate = 0.08 * (0.3 + 0.7 * (1 + np.cos(np.pi * epoch / 300)) / 2)
        for start in range(0, len(order), 64):
            ids = order[start:start + 64]
            _, grads = loss_grads(xtr[ids], ytr[ids], p)
            for key in p:
                p[key] -= learning_rate * grads[key]
        train_loss, train_acc = evaluate(xtr, ytr, p)
        valid_loss, valid_acc = evaluate(xva, yva, p)
        history.append([epoch, train_loss, valid_loss, train_acc, valid_acc])
        if valid_loss < best_loss:
            best_loss, best_epoch = valid_loss, epoch
            best = {key: value.copy() for key, value in p.items()}
    test_loss, test_acc = evaluate(xte, yte, best)
    assert test_acc > 0.90, test_acc
    out = ROOT / "experiment"
    out.mkdir(exist_ok=True)
    np.savez(out / "numpy_mlp.npz", **best, mean=mean, std=std, x_test=xte, y_test=yte)
    np.savetxt(out / "history.csv", history, delimiter=",",
               header="epoch,train_loss,valid_loss,train_accuracy,valid_accuracy", comments="")
    result = {
        "seed": 42, "train_n": 1000, "valid_n": 400, "test_n": 800,
        "max_gradient_absolute_error": float(max(errors)),
        "best_epoch": best_epoch, "test_loss": test_loss, "test_accuracy": test_acc,
        "note": "Synthetic circles; model selection uses validation loss only."
    }
    (out / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
