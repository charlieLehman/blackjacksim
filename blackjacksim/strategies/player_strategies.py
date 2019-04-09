import json
import pkg_resources
import random

basic_path = pkg_resources.resource_filename('blackjacksim.strategies','basic.json')
with open(basic_path, 'r') as strat:
    _basic = json.load(strat)

def basic(hand, dealer_up_card):
    try:
        n = None
        if hand.bust:
            return 'Bust'
        _type, _v = hand.strategy_value
        if dealer_up_card.name == 'A':
            n = '11'
        else:
            n = str(dealer_up_card.value)
        action = _basic[n][_type][_v]
        return action
    except Exception as e:
        print('Check your strategy JSON for the below condition')
        print(e)
        print(e, hand, n, _type, _v)
        raise

def random(hand, dealer_up_card):
    return random.choice(['Hit', 'Stand'])

