class PlayerWallet(object):
    def __init__(self, wager_unit, wager_pool):
        self.wager_unit = wager_unit
        self.wager_pool = wager_pool
        self.wins = 0
        self.attempts = 0

    def make_wager(self, shoe):
        self.wager_pool -= self.wager_unit
        return self.wager_unit

    def take_payout(self, payout):
        self.attempts += 0 if payout == self.wager_unit else 1
        self.wins += 1 if payout > 0 else 0
        self.wager_pool += payout

    @property
    def is_broke(self):
        return self.wager_pool - self.wager_unit <= 0

class _HouseRules(object):
    def __init__(self, normal, blackjack, split_blackjack):
        self.payout_on_normal = normal[0]/normal[1]
        self.payout_on_blackjack = blackjack[0]/blackjack[1]
        self.split_blackjack = split_blackjack
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

        if playerHand.isSplit and playerHand.blackjack:
            _tempHand = playerHand.copy()
            _tempHand.isSplit = False
            _tempHand.split_blackjack = self.split_blackjack
            return self._get_win_state(_tempHand, dealerHand)

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

class Blackjack32(_HouseRules):
    def __init__(self):
        super(Blackjack32, self).__init__(normal=(1,1), blackjack=(3,2), split_blackjack=True)

class Blackjack65(_HouseRules):
    def __init__(self):
        super(Blackjack65, self).__init__(normal=(1,1), blackjack=(6,5), split_blackjack=True)

class Blackjack32NoSplit(_HouseRules):
    def __init__(self):
        super(Blackjack32NoSplit, self).__init__(normal=(1,1), blackjack=(3,2), split_blackjack=False)

class Blackjack65NoSplit(_HouseRules):
    def __init__(self):
        super(Blackjack65NoSplit, self).__init__(normal=(1,1), blackjack=(6,5), split_blackjack=False)
