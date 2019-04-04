from blackjacksim.strategies import hit_on_soft_17, stand_on_soft_17

class Player(object):
    def __init__(self, action_strategy, wager_strategy, wager_unit, wager_pool):
        self.action_strategy = action_strategy
        self.wager_strategy = wager_strategy
        self.wager_unit = wager_unit
        self.wager_pool = wager_pool

    def deal(self, shoe):
        self.hands = []
        shoe = shoe()
        self.hands.append(shoe.draw(2))
        return shoe

    def make_wager(self):
        ## TODO Wager handler
        for hand in self.hands:
            wager = self.wager_strategy(hand, self.wager_unit)
            self.wager_pool -= wager
        return

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

        if action == 'Stand':
            return

        elif action == 'Hit':
            hand.extend(shoe.draw(1))
            new_action = self.action_strategy(hand, self.dealer_up_card)
            self.take_action(hand, shoe, new_action)

        elif action == 'Double':
            ## TODO Wager handler
            hand.extend(shoe.draw(1))
            new_action = self.action_strategy(hand, self.dealer_up_card)
            self.take_action(hand, shoe, new_action)

        elif action == 'Split':
            if hand in self.hands: self.hands.remove(hand)
            for new_hand in hand.split():
                ## TODO Wager handler
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

