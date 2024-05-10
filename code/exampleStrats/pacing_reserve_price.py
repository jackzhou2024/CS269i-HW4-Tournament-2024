import random
import numpy as np

AVG_SPEND = 0.25 
EPS = 0.05
r = 0

def get_name():
    return "reserve_price"

def update_pacing_factor(payment):
    global r
    r += EPS * (payment - AVG_SPEND)
    r = max(0, r)
    r = min(1, r)

def strategy(value, budget, remainingRound, myHistory):
    global r
    if (len(myHistory) > 0):
        update_pacing_factor(myHistory[-1][3])
    else:
        r = 0
    if (value > r):
        return min(value, budget)
    else:
        return 0
