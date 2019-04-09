import blackjacksim
import pandas as pd
from blackjacksim.entities import *
from blackjacksim.strategies import *

def _load(config, name):
    return getattr(blackjacksim.entities, config[name]['class'])(**config[name]['params'])

class Game(object):
    def __init__(self, config):
        self.wallet = _load(config,'wallet')
        self.house = _load(config,'house')
        self.dealer = _load(config,'dealer')
        config['player']['params'].update({'wallet':self.wallet, 'house':self.house})
        self.player = _load(config,'player')

        config['shoe']['params'].update({'house_rules':self.house})
        self.shoe = _load(config, 'shoe')
        self._data = []
        self._round_count = 0

    @property
    def _counter(self):
        self._round_count += 1
        return self._round_count

    @property
    def data(self):
        return pd.DataFrame(self._data)

    def round(self):
        s_pen = self.shoe.penetration
        s_state = self.shoe.state
        self.shoe = self.player.deal(self.shoe)
        self.shoe = self.dealer.deal(self.shoe)
        self.shoe = self.player.play(self.shoe, self.dealer.up_card)
        self.shoe = self.dealer.play(self.shoe, self.player.hands)
        for h in self.player.hands:
            self.wallet.take_payout(self.house.payout(h, self.dealer.hand))
        rw, rp = self.wallet.finish_round()
        self.house.finish_round()
        self._data.append({'Round':self._counter,
                    'Pool':self.wallet.wager_pool,
                    'Wager':rw,
                    'Payout':rp,
                    'Shoe Penetration':s_pen,
                    'State':s_state,
                    'Advantage':rp-rw,
                          'House':str(self.house)})
        self.shoe = self.dealer.inspect_shoe(self.shoe)
