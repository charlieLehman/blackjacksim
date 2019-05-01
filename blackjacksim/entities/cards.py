import itertools
import numpy as np
import collections
import random

#Standard deck of cards
CARDS = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10,'A':11}
SUITS = ['S','H','D','C']
STANDARD_DECK = list(itertools.product(CARDS.items(), SUITS))

class Card(object):
    def __init__(self, name, value, suit):
        self.name = name
        self.value = value
        self.suit = suit

    def __repr__(self):
        return ('{} {}'.format(self.name, self.suit))

class Hand(collections.MutableSequence):
    def __init__(self, cards, split_limit=2, blackjack_on_split=True):
        self.cards = cards
        self._action_hist = []
        self.stand = False
        self.ID = None
        self.SplitCount = 0
        self.split_limit = split_limit
        self.blackjack_on_split = blackjack_on_split
        self.player_has_blackjack = False

    def __len__(self):
        return len(self.cards)

    def __delitem__(self, index):
        self.cards.__delitem__(index)

    def insert(self, index, value):
        self.cards.insert(index, value)

    def __setitem__(self, index, value):
        self.cards.__setitem__(index, value)

    def __getitem__(self, index):
        return self.cards.__getitem__(index)

    def __repr__(self):
        return "{}: {}".format(self.ID, str(self.cards))

    def log(self, action):
        self._action_hist.append(action)

    def copy(self):
        _h = Hand(self, self.split_limit, self.blackjack_on_split)
        _h._action_hist = self._action_hist.copy()
        _h.stand = self.stand
        _h.SplitCount = self.SplitCount
        _h.ID = self.ID
        return _h

    @property
    def blackjack(self):
        _split_rule = self.SplitCount == 0 or self.blackjack_on_split
        return self.value==21 and len(self)==2 and _split_rule

    @property
    def splittable(self):
        return len(self.cards) == 2 and self.cards[0].name == self.cards[1].name and self.SplitCount <= self.split_limit

    @property
    def _a_idx(self):
        return [c.value==11 for c in self.cards]

    @property
    def soft(self):
        return any(self._a_idx)

    def split(self):
        for card in self.cards:
            if card.name == 'A':
                card.value = 11
        h1, h2 = Hand([self.cards[0]], self.split_limit, self.blackjack_on_split), Hand([self.cards[1]], self.split_limit, self.blackjack_on_split)
        h1.ID = '{}_Split_{}'.format(self.ID, 0)
        h1.SplitCount = self.SplitCount + 1
        h2.ID = '{}_Split_{}'.format(self.ID, 1)
        h2.SplitCount = self.SplitCount + 1
        return h1, h2

    @property
    def value(self):
        _value = 0
        for card in self.cards:
            _value += card.value
        if _value > 21:
            for card in list(itertools.compress(self.cards,self._a_idx)):
                card.value = 1
                _value -= 10
                if _value < 21:
                    return _value
        return _value

    @property
    def strategy_value(self):
        if self.splittable:
            return "Splittable", "AA" if all(self._a_idx) else str(self.value)
        elif self.soft:
            return "Soft", str(self.value)
        # elif not self.soft:
        else:
            return "Hard", str(self.value)
        # else:
        #     raise Exception ("There is no strategy value for {}".format(self))

    @property
    def bust(self):
        return self.value > 21

class Deck(object):
    def __init__(self):
        self._deck = []
        for ((name,value),suit) in STANDARD_DECK:
            self._deck.append(Card(name, value, suit))

    def __getitem__(self, index):
        return self._deck[index]

    def __setitem__(self, index, card):
        self._deck[index] = card

    def __len__(self):
        return len(self._deck)

class Shoe(object):
    def __init__(self, size, cut_card_position, house_rules):
        self._shoe = []
        self._dealt = []
        # assuming STANDARD deck is used
        _s = 4*size
        self._initial = {'2':_s,
                         '3':_s,
                         '4':_s,
                         '5':_s,
                         '6':_s,
                         '7':_s,
                         '8':_s,
                         '9':_s,
                         '10':4*_s,
                         '11':_s}
        self.size = size
        self.cut_card_position = cut_card_position
        for _ in range(size):
            self._shoe.extend(Deck())
        self.orig_len = len(self._shoe)
        random.shuffle(self)
        self.house_rules = house_rules

    def __getitem__(self, index):
        return self._shoe[index]

    def __setitem__(self, index, card):
        self._shoe[index] = card

    def __len__(self):
        return len(self._shoe)

    @property
    def state(self):
        _d = dict(self._initial)
        for c in self._dealt:
            _val = c.value if c.value!=1 else 11
            _d[str(_val)] -= 1
        return np.array([v for v in _d.values()])

    @property
    def penetration(self):
        return 1-float(self.__len__())/float(self.orig_len)

    def __call__(self, can_shuffle=False):
        if self.penetration > self.cut_card_position and can_shuffle:
            return Shoe(self.size, self.cut_card_position, self.house_rules)
        else:
            return self

    def __repr__(self):
        return "{} Deck Shoe with {} cards left or {:.2f} % Penetration".format(self.size, self.__len__(), self._penetration_state*100)

    def draw(self, number=1, **kwargs):
        if len(self) < number:
            self = self(True)
        _d = self._shoe[:number].copy()
        self._dealt.extend(_d)
        del self._shoe[:number]
        return Hand(_d, **self.house_rules.hand_rules)

class CustomShoe(Shoe):
    def __init__(self, decks, size, cut_card_position, house_rules):
        super(CustomShoe, self).__init__(size, cut_card_position, house_rules)
        for deck in decks:
            self._shoe.extend(deck)
