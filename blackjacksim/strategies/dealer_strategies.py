def hit_on_soft_17(hand):
        if (hand.value < 17) | (hand.value == 17 and hand.soft):
            return 'Hit'
        elif (hand.value > 21):
                return 'Bust'
        else:
            return 'Stand'

def stand_on_soft_17(hand):
        if (hand.value < 17):
            return 'Hit'
        elif (hand.value > 21):
                return 'Bust'
        else:
            return 'Stand'
