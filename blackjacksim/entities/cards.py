import itertools
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
    def __init__(self, cards):
        self.cards = cards
        self.stand = False

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
        return str(self.cards)

    @property
    def blackjack(self):
        return self.value==21 and self.__len__()==2

    @property
    def splittable(self):
        return len(self.cards) == 2 and self.cards[0].name == self.cards[1].name

    @property
    def _a_idx(self):
        return [c.value==11 for c in self.cards]

    @property
    def soft(self):
        return any(self._a_idx)

    def split(self):
        if not self.splittable:
            raise Exception("Bad Move: Can't split this hand {}".format(self))
        for card in self.cards:
            if card.name == 'A':
                card.value = 11
        return Hand([self.cards[0]]), Hand([self.cards[1]])

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
            return "Splittable", "AA" if any(self._a_idx) and len(self.cards) == 2 else str(self.value)
        elif self.soft:
            return "Soft", str(self.value)
        elif not self.soft:
            return "Hard", str(self.value)
        else:
            raise Exception ("There is no strategy value for {}".format(self))

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
    def __init__(self, size, penetration):
        self._shoe = []
        self.size = size
        self.penetration = penetration
        for _ in range(size):
            self._shoe.extend(Deck())
        self.orig_len = len(self._shoe)
        random.shuffle(self._shoe)

    def __getitem__(self, index):
        return self._shoe[index]

    def __setitem__(self, index, card):
        self._shoe[index] = card

    def __len__(self):
        return len(self._shoe)

    @property
    def _penetration_state(self):
        return float(self.__len__())/float(self.orig_len)

    def __call__(self):
        if self._penetration_state < self.penetration:
            return Shoe(self.size, self.penetration)
        else:
            return self

    def __repr__(self):
        return "{} Deck Shoe with {} cards left or {:.2f} % Penetration".format(self.size, self.__len__(), self._penetration_state*100)

    def draw(self, number=1):
        _d = self._shoe[:number].copy()
        del self._shoe[:number]
        return Hand(_d)
