import json
import pkg_resources

default_config_path = pkg_resources.resource_filename('blackjacksim.data','default_config.json')
with open(default_config_path, 'r') as conf:
    default_config = json.load(conf)

basic_path = pkg_resources.resource_filename('blackjacksim.data','basic.json')
with open(basic_path, 'r') as strat:
    _basic = json.load(strat)

def DefaultGameConfig():
    return default_config

def BasicStrategy():
    return _basic
