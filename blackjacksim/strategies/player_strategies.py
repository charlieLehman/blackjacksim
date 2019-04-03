import json

# TODO make this depend on the json files present in the directory
with open('./basic.json', 'r') as strat:
    _basic = json.load(strat)

def basic(hand, dealer_up_card):
    _type, _v = hand.strategy_value
    return _basic[dealer_up_card][_type][_v]


