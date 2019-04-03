def hit_on_soft_17(hand):
        if (hand.value < 17) | (hand.value == 17 and hand.soft):
            return 'Hit'
        else:
            return 'Stand'

def stand_on_soft_17(hand):
        if (hand.value < 17):
            return 'Hit'
        else:
            return 'Stand'
