import os
import itertools
import importlib
import numpy as np
import random
import json

AUCTION_FOLDER = "auctionStrats"
STRATEGY_FOLDER = "exampleStrats"
CONTEXT_FILE = "context.json"


NUM_ROUNDS = 10000 # You can reduce the num round when you debug
TOTAL_BUDGET = 0.25 * NUM_ROUNDS

def gen_context():
    f = open(CONTEXT_FILE, 'w')
    jsonArr = []
    valueArr1 = []
    valueArr2 = []
    for i in range(NUM_ROUNDS):
        v1 = random.uniform(0,1)
        valueArr1.append(v1)
        v2 = random.uniform(0,1)
        valueArr2.append(v2)  

    for i in range(NUM_ROUNDS):
        jsonItem = {}
        jsonItem["v1"] = valueArr1[i]
        jsonItem["v2"] = valueArr2[i]
        jsonArr.append(jsonItem)
    
    json.dump(jsonArr, f, indent=4)


gen_context()       
# exit(0)




def calcScore(value, allocationResult):
    if allocationResult == 1:
        # winner, score is value
        return value
    else:
        # loser:  score 0
        return 0
    
def calcRevenue():
    pass

def runRound(pair, auction):
    # print("modulea:",STRATEGY_FOLDER+"."+pair[0])
    moduleA = importlib.import_module(STRATEGY_FOLDER+"."+pair[0])
    moduleB = importlib.import_module(STRATEGY_FOLDER+"."+pair[1])
    moduleAuction = importlib.import_module(AUCTION_FOLDER +"."+auction)
    contextJson = json.load(open(CONTEXT_FILE, 'r'))
    
    LENGTH_OF_GAME =len(contextJson)
    totalScore1, totalScore2 = 0, 0

    history1 = []
    history2 = []
    cnt1 = 0
    cnt2 = 0
    budget1 = TOTAL_BUDGET
    budget2 = TOTAL_BUDGET
    revenue = 0

    auctionHistory1 = []
    auctionHistory2 = []
    for turn in range(NUM_ROUNDS):
        contextItem = contextJson[turn]
        v1 = contextItem["v1"]
        v2 = contextItem["v2"]
        bid1 = moduleA.strategy(v1, budget1, LENGTH_OF_GAME - turn, history1)
        bid2 = moduleB.strategy(v2, budget2, LENGTH_OF_GAME - turn, history2)
        bid1 = min(bid1, budget1)
        bid2 = min(bid2, budget2)
        if(bid1 < 0):
            raise Exception("bid1 price is not valid (< 0) ", bid1)
        if(bid2 < 0):
            raise Exception("bid2 price is not valid (< 0)  ", bid2)


    
        # print("bid1=", bid1, " bid2=",bid2)
        # The auction strategy can also see the history of bids, payments, and allocations (but not values)
        auctionResult = moduleAuction.auctionStrategy(bid1, bid2, auctionHistory1, auctionHistory2)
        result1 = auctionResult[0][0]
        result2 = auctionResult[1][0]
        payment1 = auctionResult[0][1]
        payment2 = auctionResult[1][1]
        if payment1 >bid1 or payment2 >bid2:
            raise Exception("Bidder's payment cannot be larger than the bid price, please check your auction strategy")
        if not ((result1==1 and result2 ==0) or (result1 == 0 and result2 ==1) or (result1 == 0 and result2 ==0)):
            raise Exception("At most one bidder can win, and it is allowed that neither wins")
        # if auctionResult[0][0]==1:
        #     cnt1 +=1
        # if auctionResult[1][0]==1:
        #     cnt2 += 1
        # print(bid1," vs ", bid2, " win ", cnt1, " vs ", cnt2)

        score1 = calcScore(v1, result1)
        score2 = calcScore(v2, result2)
        budget1 -= payment1
        budget2 -= payment2
        revenue += payment1 + payment2
        totalScore1 += score1
        totalScore2 += score2
        history1.append([v1, bid1, result1, payment1])
        history2.append([v2, bid2, result2, payment2])
        
        auctionHistory1.append([bid1, result1, payment1])
        auctionHistory2.append([bid2, result2, payment2])

    return totalScore1 + totalScore2, revenue


def pad(stri, leng):
    result = stri
    for i in range(len(stri),leng):
        result = result+" "
    return result
    
def runFullPairingTournament(auctionFolder, stratsFolder):
    print("Starting tournament, reading files from "+stratsFolder)
    scoreKeeper = {}
    STRATEGY_LIST = []
    for file in os.listdir(stratsFolder):
        if file.endswith(".py"):
            STRATEGY_LIST.append(file[:-3])

    print("Reading Auction modes from "+auctionFolder)
    AUCTION_LIST = []
    for file in os.listdir(auctionFolder):
        if file.endswith(".py"):
            AUCTION_LIST.append(file[:-3])
            
    for strategy in STRATEGY_LIST:
        scoreKeeper[strategy] = 0


    for auction in AUCTION_LIST:
        totalWelfare = 0
        totalRevenue = 0
        pairNum = 0
        for pair in itertools.combinations(STRATEGY_LIST, r=2):
            welfare, revenue = runRound(pair, auction)
            totalWelfare += welfare
            totalRevenue += revenue
            pairNum +=1
        print("\t AvgScore ", round((totalRevenue + totalWelfare)/pairNum,2), "\t AvgWelfare ", round(totalWelfare/pairNum,2), "\t AvgRevenue ", round(totalRevenue/pairNum,2))
        
    
        
    # scoresNumpy = np.zeros(len(scoreKeeper))
    # for i in range(len(STRATEGY_LIST)):
    #     scoresNumpy[i] = scoreKeeper[STRATEGY_LIST[i]]
    # rankings = np.argsort(scoresNumpy)

    # print("\n\nTOTAL SCORES\n")
    # for rank in range(len(STRATEGY_LIST)):
    #     i = rankings[-1-rank]
    #     score = scoresNumpy[i]
    #     scorePer = score/(len(STRATEGY_LIST)-1)
    #     print("#"+str(rank+1)+": "+pad(STRATEGY_LIST[i]+":",16)+' %.3f'%score+'  (%.3f'%scorePer+" average)\n")
    # print("Done with everything!")
    
    
runFullPairingTournament(AUCTION_FOLDER, STRATEGY_FOLDER)
