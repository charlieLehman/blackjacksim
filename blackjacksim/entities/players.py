from blackjacksim.strategies import hit_on_soft_17, stand_on_soft_17

class Player(object):
    def __init__(self, action_strategy, wallet, payout_rules):
        self.action_strategy = action_strategy
        self.wallet = wallet
        self.payout_rules = payout_rules

    def deal(self, shoe):
        self.hands = []
        self._hand_id_count = 0
        shoe = shoe()
        h = shoe.draw(2)
        h.ID = self._hand_id()
        wager = self.wallet.make_wager(shoe)
        self.payout_rules.initial(h, wager)
        self.hands.append(h)
        return shoe

    def _hand_id(self):
        self._hand_id_count += 1
        return '{:04d}'.format(self._hand_id_count)

    def play(self, shoe, dealer_up_card):
        shoe = shoe()
        self.dealer_up_card = dealer_up_card
        # need to copy in case of split
        _hands = self.hands.copy()
        for hand in _hands:
            action = self.action_strategy(hand, self.dealer_up_card)
            self.take_action(hand, shoe, action)
        return shoe

    def take_action(self, hand, shoe, action):

        if self.wallet.is_broke:
            return

        hand.log(action)

        if action == 'Stand':
            return

        elif action == 'Hit':
            hand.extend(shoe.draw(1))
            new_action = self.action_strategy(hand, self.dealer_up_card)
            self.take_action(hand, shoe, new_action)

        elif action == 'Double':
            ## TODO Wager handler
            wager = self.wallet.make_wager(shoe)
            self.payout_rules.double(hand, wager)
            hand.extend(shoe.draw(1))
            return

        elif action == 'Split':
            # this may be dangerous because it just removes the first one it encounters
            if hand in self.hands: self.hands.remove(hand)
            wager = self.wallet.make_wager(shoe)
            for new_hand, new_wager in zip(hand.split(), self.payout_rules.split(hand,wager)):
                new_wager(new_hand)
                new_hand.extend(shoe.draw(1))
                self.hands.append(new_hand)
                new_action = self.action_strategy(new_hand, self.dealer_up_card)
                self.take_action(new_hand, shoe, new_action)

        elif action == 'Bust':
            return

    @property
    def blackjack(self):
        return [hand.blackjack for hand in self.hands]

    def __repr__(self):
        return str([(hand, hand.value) for hand in self.hands])

class Dealer(object):
    def __init__(self, strategy=hit_on_soft_17):
        self.strategy = strategy

    def deal(self, shoe):
        self.hands = None
        shoe = shoe()
        self.hand = shoe.draw(2)
        return shoe

    @property
    def blackjack(self):
        return self.hand.blackjack

    @property
    def up_card(self):
        return self.hand[0]

    def play(self, shoe, players_hands):
        shoe = shoe()
        if all([h.bust for h in players_hands]):
            return shoe
        while not (self.hand.stand or self.hand.bust):
            action = self.strategy(self.hand)
            if action == 'Stand':
                self.hand.stand = True
            if action == 'Hit':
                self.hand.extend(shoe.draw(1))
        return shoe

    def __repr__(self):
        return str([self.hand, self.hand.value])

