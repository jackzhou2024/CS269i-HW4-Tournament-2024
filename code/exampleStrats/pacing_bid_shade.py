import numpy as np

AVG_SPEND = 0.25
EPS = 0.05 
mu = 0 

def get_name():
    return "bid_shading"

def update_pacing_factor(payment):
    global mu
    mu += EPS * (payment - AVG_SPEND)
    mu = max(0, mu)

def strategy(value, budget, remainingRound, myHistory):
    global mu
    if (len(myHistory) > 0):
        update_pacing_factor(myHistory[-1][3])
    else:
        mu = 0
    return min(value / (mu + 1), budget)
