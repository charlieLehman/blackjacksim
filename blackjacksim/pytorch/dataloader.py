import torch
from torch.utils.data import Dataset
from blackjacksim.simulations import Game
from blackjacksim.data import DefaultGameConfig
import numpy as np

_default = DefaultGameConfig()
class BlackjackDataset(Dataset):
    def __init__(self, batch_size, config=_default, max_len=5000):
        self.batch_size = batch_size
        self.config = config
        self.max_len = (max_len//batch_size)
        self._dummy = [None]*self.max_len

    def __getitem__(self, index):
        self._dummy[index]
        g = Game(self.config)
        shoesize = self.config['shoe']['params']['size']
        for _ in range(np.random.randint(1,shoesize*(50))):
            g.round()
        for _ in range(2*self.batch_size):
            g.round()
        S = np.stack(g.data.State)
        w = np.array(g.data.Advantage.apply(np.sign))
        # w[w==0] = -1
        w = w[S.sum(1)!=shoesize*52]
        S = S[S.sum(1)!=shoesize*52]
        idx = np.random.permutation(range(len(w)))
        S = S[idx][:self.batch_size,:]
        w = w[idx][:self.batch_size]
        return torch.from_numpy(S).float(), torch.from_numpy(w).float()

    def __len__(self):
        return self.max_len


