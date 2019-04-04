import json
import pkg_resources

# TODO make this depend on the json files present in the directory

basic_path = pkg_resources.resource_filename('blackjacksim.strategies','basic.json')
with open(basic_path, 'r') as strat:
    _basic = json.load(strat)

def basic(hand, dealer_up_card):
    _type, _v = hand.strategy_value
    if dealer_up_card.name == 'A':
        n = '11'
    else:
        n = str(dealer_up_card.value)
    return _basic[n][_type][_v]


