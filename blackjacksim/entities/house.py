class PlayerWallet(object):
    def __init__(self, wager_unit, wager_pool):
        self.wager_unit = wager_unit
        self.wager_pool = wager_pool
        self.round_wagers = 0
        self.round_payouts = 0

    def make_wager(self, shoe):
        self.wager_pool -= self.wager_unit
        self.round_wagers += self.wager_unit
        return self.wager_unit

    def take_payout(self, payout):
        self.wager_pool += payout
        self.round_payouts += payout

    def finish_round(self):
        _rw = self.round_wagers
        _rp = self.round_payouts
        self.round_wagers = 0
        self.round_payouts = 0
        return _rw, _rp

    @property
    def is_broke(self):
        return self.wager_pool - self.wager_unit <= 0

class _HouseRules(object):
    def __init__(self, normal, blackjack, split_blackjack, split_limit):
        self.payout_on_normal = normal[0]/normal[1]
        self.payout_on_blackjack = blackjack[0]/blackjack[1]
        self.split_blackjack = split_blackjack
        self.hand_rules = {"split_limit":split_limit}
        self.wager_pool = {}

    def initial(self, hand, wager):
        self.wager_pool.update({hand.ID:wager})

    def split(self, hand, wager):
        initial_wager = self.wager_pool[hand.ID]
        if wager != initial_wager:
            raise Exception('Not proper split action: Initial bet {}, split bet {}'.format(initial_wager, wager))
        del self.wager_pool[hand.ID]
        return [lambda new_hand: self.initial(new_hand, initial_wager) for _ in range(2)]

    def double(self, hand, wager):
        if wager != self.wager_pool[hand.ID]:
            raise Exception('Not proper double down action: Initial bet {}, doubled bet {}'.format(self.wager_pool[hand.ID], wager))
        self.wager_pool[hand.ID] *= 2

    @property
    def settled(self):
        unsettled = 0
        for k, v in self.wager_pool.items():
            unsettled += v
        return unsettled == 0

    def _get_win_state(self, playerHand, dealerHand):

        # _maybe_blackjack = playerHand.value==21 and len(playerHand)==2
        # if playerHand.SplitCount > 0 and _maybe_blackjack and self.split_blackjack:
        #     _tempHand = playerHand.copy()
        #     _tempHand.SplitCount = 0
        #     return self._get_win_state(_tempHand, dealerHand)

        if playerHand.blackjack and dealerHand.blackjack:
            return 'Push'
        elif dealerHand.blackjack and not playerHand.blackjack:
            return 'Lose'
        elif not dealerHand.blackjack and playerHand.blackjack:
            return 'Blackjack'
        elif dealerHand.bust and not playerHand.bust:
            return 'Win'
        elif not dealerHand.bust and playerHand.bust:
            return 'Lose'
        elif dealerHand.value == playerHand.value:
            return 'Push'
        elif dealerHand.value > playerHand.value:
            return 'Lose'
        elif dealerHand.value < playerHand.value:
            return 'Win'

    def payout(self, playerHand, dealerHand):
        win_state = self._get_win_state(playerHand, dealerHand)
        wager = self.wager_pool[playerHand.ID]
        self.wager_pool[playerHand.ID] -= wager
        try:
            if win_state == 'Blackjack':
                pay = wager*(1+self.payout_on_blackjack)
            elif win_state == 'Lose':
                pay = 0
            elif win_state == 'Win':
                pay = wager*(1+self.payout_on_normal)
            elif win_state == 'Push':
                pay = wager
            if self.settled:
                self.wager_pool = {}
            return pay
        except KeyError as e:
            print(e, str(self.wager_pool))

    def finish_round(self):
        if not self.settled:
            raise Exception('Unsettled Wagers: {}'.format(self.wager_pool))

    def __repr__(self):
        return str(self.__class__.__name__)

class Blackjack32(_HouseRules):
    def __init__(self):
        super(Blackjack32, self).__init__(normal=(1,1), blackjack=(3,2), split_blackjack=True, split_limit=3)

class Blackjack65(_HouseRules):
    def __init__(self):
        super(Blackjack65, self).__init__(normal=(1,1), blackjack=(6,5), split_blackjack=True, split_limit=3)

class Blackjack32NoSplit(_HouseRules):
    def __init__(self):
        super(Blackjack32NoSplit, self).__init__(normal=(1,1), blackjack=(3,2), split_blackjack=False, split_limit=3)

class Blackjack65NoSplit(_HouseRules):
    def __init__(self):
        super(Blackjack65NoSplit, self).__init__(normal=(1,1), blackjack=(6,5), split_blackjack=False, split_limit=3)
