import random
import numpy as np


AVG_SPEND = 0.25 
EPS = 0.05 
tau = 0

def get_name():
    return "throttling"

def update_pacing_factor(payment):
    global tau
    tau += EPS * (payment - AVG_SPEND)
    tau = max(0, tau)

def strategy(value, budget, remainingRound, myHistory):
    global tau
    if (len(myHistory) > 0):
        update_pacing_factor(myHistory[-1][3])
    else:
        tau = 0 # reset the pacing factor
    if (random.random() < 1.0/(tau + 1)):
        return min(value, budget)
    else:
        return 0
