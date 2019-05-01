import torch.nn as nn


class DisOneLinear(nn.Module):
    def __init__(self, dim):
        super(DisOneLinear, self).__init__()
        self.classifier = nn.Sequential(
            nn.Linear(dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        y = self.classifier(x)
        return y


class DisTwoLinear(nn.Module):
    def __init__(self, dim):
        super(DisTwoLinear, self).__init__()
        self.classifier = nn.Sequential(
            nn.Linear(dim, 20),
            nn.Sigmoid(),
            nn.Linear(20, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        y = self.classifier(x)
        return y


class DisThreeLinear(nn.Module):
    def __init__(self, dim):
        super(DisThreeLinear, self).__init__()
        self.classifier = nn.Sequential(
            nn.Linear(dim, 40),
            nn.Sigmoid(),
            nn.Linear(40, 20),
            nn.Sigmoid(),
            nn.Linear(20, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        y = self.classifier(x)
        return y


class DisFiveLinearReLu(nn.Module):
    def __init__(self, dim):
        super(DisFiveLinearReLu, self).__init__()
        self.classifier = nn.Sequential(
            nn.Linear(dim, 10),
            nn.ReLU(),
            nn.Linear(10, 10),
            nn.ReLU(),
            nn.Linear(10, 10),
            nn.ReLU(),
            nn.Linear(10, 10),
            nn.ReLU(),
            nn.Linear(10, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        y = self.classifier(x)
        return y


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        m.weight.data.normal_(0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        m.weight.data.normal_(1.0, 0.02)
        m.bias.data.fill_(0)
