from blackjacksim.strategies import hit_on_soft_17, stand_on_soft_17

class Player(object):
    def __init__(self, action_strategy, wager_strategy, wager_unit, wager_pool):
        self.action_strategy = action_strategy
        self.wager_strategy = wager_strategy
        self.wager_unit = wager_unit
        self.wager_pool = wager_pool
        self.hands = []

    def deal(self, shoe):
        self.hands.append(shoe.draw(2))

    def make_wager(self):
        ## TODO Wager handler
        for hand in self.hands:
            wager = self.wager_strategy(hand, self.wager_unit)
            self.wager_pool -= wager

        return
    def play(self, shoe, dealer_up_card):
        # need to copy in case of split
        self.dealer_up_card = dealer_up_card
        _hands = self.hands.copy()
        for hand in _hands:
            action = self.action_strategy(hand, self.dealer_up_card)
            self.take_action(hand, shoe, action)

    def take_action(self, hand, shoe, action):
        while not (hand.stand or hand.bust):
            if action == 'Stand':
                hand.stand = True

            elif action == 'Hit':
                hand.extend(shoe.draw(1))

            elif action == 'Double':
                ## TODO Wager handler
                hand.extend(shoe.draw(1))
                hand.stand = True

            elif action == 'Split':
                for new_hand in hand.split():
                    ## TODO Wager handler
                    new_hand.extend(shoe.draw(1))
                    self.hands.append(new_hand)
                hand.stand = True
                self.hands.remove(hand)
                # recurse over modified hand
                self.play(shoe, self.dealer_up_card)
        return

    def __repr__(self):
        return str([(hand, hand.value) for hand in self.hands])

class Dealer(object):
    def __init__(self, strategy=hit_on_soft_17):
        self.strategy = strategy
        self.hand = None

    def deal(self, shoe):
        self.hand = shoe.draw(2)

    @property
    def up_card(self):
        return self.hand[0]

    def play(self, shoe):
        while not (self.hand.stand or self.hand.bust):
            action = self.strategy(self.hand)
            if action == 'Stand':
                self.hand.stand = True
            if action == 'Hit':
                self.hand.extend(shoe.draw(1))
        return

    def __repr__(self):
        return str([self.hand, self.hand.value])

