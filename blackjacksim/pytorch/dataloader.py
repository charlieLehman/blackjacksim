import torch
from torch.utils.data import Dataset
from blackjacksim.simulations import Game
import numpy as np


class BlackjackDataset(Dataset):
    def __init__(self, batch_size, config, max_len=5000):
        self.batch_size = batch_size
        self.config = config
        self.max_len = max_len
        self._dummy = [None]*max_len

    def __getitem__(self, index):
        self._dummy[index]
        g = Game(self.config)
        for _ in range(self.batch_size+1):
            g.round()
        S = np.stack(g.data.State)
        w = np.array(g.data.Advantage.apply(np.sign))
        w[w==0] = -1
        return torch.from_numpy(S[1:,:]), torch.from_numpy(w[1:])

    def __len__(self):
        return self.max_len


