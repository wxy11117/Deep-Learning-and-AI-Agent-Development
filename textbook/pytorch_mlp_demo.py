"""CPU-friendly teaching example. Requires PyTorch; no dataset download."""
from copy import deepcopy
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader


def main():
    torch.manual_seed(42)
    torch.set_num_threads(2)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    generator = torch.Generator().manual_seed(42)

    def make_data(n):
        x = torch.rand(n, 2, generator=generator) * 3 - 1.5
        y = (x.square().sum(dim=1) > 1).long()
        return x, y

    train_x, train_y = make_data(1000)
    valid_x, valid_y = make_data(400)
    test_x, test_y = make_data(800)
    mean = train_x.mean(dim=0)
    std = train_x.std(dim=0, unbiased=False).clamp_min(1e-8)
    train_x, valid_x, test_x = [
        (x - mean) / std for x in (train_x, valid_x, test_x)
    ]
    loader = DataLoader(TensorDataset(train_x, train_y), batch_size=64,
                        shuffle=True, generator=generator, num_workers=0)
    model = nn.Sequential(nn.Linear(2, 32), nn.Tanh(), nn.Linear(32, 2)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.01, weight_decay=1e-4)

    @torch.no_grad()
    def evaluate(x, y):
        model.eval()
        logits = model(x.to(device))
        target = y.to(device)
        return criterion(logits, target).item(), (
            logits.argmax(dim=1) == target
        ).float().mean().item()

    best_state, best_loss, best_epoch = None, float("inf"), 0
    for epoch in range(1, 101):
        model.train()
        loss_sum = 0.0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            loss_sum += loss.item() * y.numel()
        valid_loss, valid_acc = evaluate(valid_x, valid_y)
        if valid_loss < best_loss:
            best_loss, best_epoch = valid_loss, epoch
            best_state = deepcopy(model.state_dict())
        if epoch % 20 == 0:
            print(epoch, loss_sum / len(train_y), valid_loss, valid_acc)
    model.load_state_dict(best_state)
    test_loss, test_acc = evaluate(test_x, test_y)
    checkpoint = {
        "state_dict": {k: v.cpu() for k, v in model.state_dict().items()},
        "mean": mean, "std": std, "architecture": [2, 32, 2],
        "activation": "Tanh", "best_epoch": best_epoch,
    }
    torch.save(checkpoint, Path(__file__).with_name("pytorch_mlp.pt"))
    print({"best_epoch": best_epoch, "test_loss": test_loss, "test_accuracy": test_acc})


if __name__ == "__main__":
    main()
