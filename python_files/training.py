import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


# CONFIG


BATCH_SIZE = 128
EPOCHS = 20
LR = 1e-3

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", DEVICE)


# BINARY SIGN WITH STE


class BinarySign(torch.autograd.Function):

    @staticmethod
    def forward(ctx, x):
        return x.sign()

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output

binary_sign = BinarySign.apply

# BINARY LINEAR LAYER

class BinaryLinear(nn.Module):

    def __init__(self, in_features, out_features):
        super().__init__()

        self.weight = nn.Parameter(
            torch.randn(out_features, in_features) * 0.01
        )

    def forward(self, x):
        bw = binary_sign(self.weight)
        return x @ bw.t()

# NETWORK
#
#
#   testing input pixels {0,1}  →  remap to {-1,+1}
#   fc1 matmul with {-1,+1} weights  =  XNOR+popcount: 2*pcount-784
#   BN1  (running stats used for threshold folding in thresholds.py)
#   sign() activation → {-1,+1}      (testing: layer2 = "0"/"1")
#   fc2 matmul with {-1,+1} weights  =  XNOR+popcount: 2*pcount-256
#   BN2
#   sign() activation → {-1,+1}      (testing: layer3 = "0"/"1")
#   fc3 matmul with {-1,+1} weights  =  raw scores (testing: layer4)


class BNN(nn.Module):

    def __init__(self):
        super().__init__()

        self.fc1 = BinaryLinear(784, 256)
        self.bn1 = nn.BatchNorm1d(256)

        self.fc2 = BinaryLinear(256, 256)
        self.bn2 = nn.BatchNorm1d(256)

        self.fc3 = BinaryLinear(256, 10)

    def forward(self, x):
        x = x.view(-1, 784)


        x = 2.0 * x - 1.0

        x = self.fc1(x)
        x = self.bn1(x)
        x = binary_sign(x)

        x = self.fc2(x)
        x = self.bn2(x)
        x = binary_sign(x)

        x = self.fc3(x)

        return x

# DATA
# Pixels binarized at 0.5, matching testing.py exactly


transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Lambda(lambda x: (x >= 0.5).float())
])

train_dataset = datasets.MNIST(
    root="./data",
    train=True,
    download=True,
    transform=transform
)

test_dataset = datasets.MNIST(
    root="./data",
    train=False,
    download=True,
    transform=transform
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# MODEL


model = BNN().to(DEVICE)

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LR
)

# TRAINING

for epoch in range(EPOCHS):

    model.train()

    running_loss = 0.0

    for images, labels in train_loader:

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

    avg_loss = running_loss / len(train_loader)

    print(
        f"Epoch {epoch+1:02d}/{EPOCHS} "
        f"Loss = {avg_loss:.4f}"
    )

# EVALUATION

model.eval()

correct = 0
total = 0

with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        outputs = model(images)

        predictions = outputs.argmax(dim=1)

        correct += (predictions == labels).sum().item()

        total += labels.size(0)

accuracy = 100.0 * correct / total

print("\nTest Accuracy = %.2f%%" % accuracy)

# EXPORT BINARY WEIGHTS

w1 = model.fc1.weight.sign().detach().cpu()
w2 = model.fc2.weight.sign().detach().cpu()
w3 = model.fc3.weight.sign().detach().cpu()

torch.save(
    {
        "fc1": w1,
        "fc2": w2,
        "fc3": w3
    },
    "binary_weights.pt"
)

print("\nSaved binary_weights.pt")

# EXPORT BATCHNORM PARAMETERS

torch.save(
    {
        "bn1_gamma": model.bn1.weight.detach().cpu(),
        "bn1_beta": model.bn1.bias.detach().cpu(),
        "bn1_mean": model.bn1.running_mean.detach().cpu(),
        "bn1_var": model.bn1.running_var.detach().cpu(),

        "bn2_gamma": model.bn2.weight.detach().cpu(),
        "bn2_beta": model.bn2.bias.detach().cpu(),
        "bn2_mean": model.bn2.running_mean.detach().cpu(),
        "bn2_var": model.bn2.running_var.detach().cpu(),
    },
    "batchnorm_params.pt"
)

print("Saved batchnorm_params.pt")


# EXPORT HUMAN-READABLE WEIGHT TXT FILES


with open("fc1_weights.txt", "w") as f:
    for row in w1.numpy():
        f.write(" ".join(str(int(x)) for x in row) + "\n")

with open("fc2_weights.txt", "w") as f:
    for row in w2.numpy():
        f.write(" ".join(str(int(x)) for x in row) + "\n")

with open("fc3_weights.txt", "w") as f:
    for row in w3.numpy():
        f.write(" ".join(str(int(x)) for x in row) + "\n")

print("Saved fc1_weights.txt")
print("Saved fc2_weights.txt")
print("Saved fc3_weights.txt")

print("\nTraining complete.")