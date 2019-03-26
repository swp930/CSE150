import pygame, sys, random, copy
from pygame.locals import *
from cards import *
import time
import numpy as np
import random

def genCard(cList, xList):
    #Generate and remove an card from cList and append it to xList.
    #Return the card, and whether the card is an Ace
    cA = 0
    card = random.choice(cList)
    cList.remove(card)
    xList.append(card)
    if card in cardA:
        cA = 1
    return card, cA

def initGame(cList, uList, dList):
    #Generates two cards for dealer and user, one at a time for each.
    #Returns if card is Ace and the total amount of the cards per person.
    userA = 0
    dealA = 0
    card1, cA = genCard(cList, uList)
    userA += cA
    card2, cA = genCard(cList, dList)
    dealA += cA
    dealAFirst = copy.deepcopy(dealA)
    card3, cA = genCard(cList, uList)
    userA += cA
    card4, cA = genCard(cList, dList)
    dealA += cA
    #The values are explained below when calling the function
    return getAmt(card1) + getAmt(card3), userA, getAmt(card2) + getAmt(card4), dealA, getAmt(card2), dealAFirst

def make_state(userSum, userA, dealFirst, dealAFirst):
    #Eliminate duplicated bust cases
    if userSum > 21: 
        userSum = 22
    #userSum: sum of user's cards
    #userA: number of user's Aces
    #dealFirst: value of dealer's first card
    #dealAFirst: whether dealer's first card is Ace   
    return (userSum, userA, dealFirst, dealAFirst)

def policy(userSum):
    if userSum < 17:
        return 0
    else:
        return 1

def simulation_sequence(policy, state, userCard, dealCard, ccards):
    episode = []
    userSum = state[0]
    userA = state[1]
    dealSum = state[2]
    dealA = state[3]
    dealFirst = state[2]
    dealAFirst = state[3]
    stand = False
    gameover = False
    # follow the game engine to do simulation
    while True:
        if (userSum >= 21 and userA == 0) or len(userCard) == 5:
            gameover = True
        else:
            gameover = False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        # calculate reward
        if not (gameover or stand):
            episode.append((state,0))
        else:
            if userSum == dealSum:
                reward = 0
            elif userSum <= 21 and len(userCard) == 5:
                reward = 1
            elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                reward = 1
            else:
                reward = -1
            episode.append((state,reward))
            return episode
        action = policy(userSum)
        if not (gameover or stand) and action == 0:
            #Give player a card
            card, cA = genCard(ccards, userCard)
            userA += cA
            userSum += getAmt(card)
            while userSum > 21 and userA > 0:
                userA -= 1
                userSum -= 10
        elif not gameover and action == 1:
            #Dealer plays, user stands
            stand = True
            if dealSum == 21:
                pass
            else:
                while dealSum <= userSum and dealSum < 17:
                    card, cA = genCard(ccards, dealCard)
                    dealA += cA
                    dealSum += getAmt(card)
                    while dealSum > 21 and dealA > 0:
                        dealA -= 1
                        dealSum -= 10
        state = make_state(userSum, userA, dealFirst, dealAFirst)

def simulate_one_step_tmp(state, action, userCard, dealCard, ccards, stand):
    # Initialize userSum, userA, dealSum, dealA, dealFirst, dealAFirst
    userSum = state[0]
    userA = state[1]
    dealSum = state[2]
    dealA = state[3]
    dealFirst = state[2]
    dealAFirst = state[3]
    gameover = False
    # If action given is to hit then add a card to userCard
    if action == 0:
        card, cA = genCard(ccards, userCard)
        userA += cA
        userSum += getAmt(card)
        while userSum > 21 and userA > 0:
            userA -= 1
            userSum -= 10
    elif action == 1: # If action given is to stand then add a card to dealer
        stand = True
        if dealSum == 21:
            pass
        else:
            while dealSum <= userSum and dealSum < 17:
                card, cA = genCard(ccards, dealCard)
                dealA += cA
                dealSum += getAmt(card)
                while dealSum > 21 and dealA > 0:
                    dealA -= 1
                    dealSum -= 10
    # Make a new state
    state = make_state(userSum, userA, dealFirst, dealAFirst) 
    # Check whether the game has terminated
    if(userSum >= 21 and userA == 0) or len(userCard) == 5:
        gameover = True
    else:
        gameover = False
    if len(userCard) == 2 and userSum == 21:
        gameover = True
    isTerminal = False
    reward = 0
    # Assign rewards based on the current state
    if gameover or stand:
        if userSum == dealSum:
            reward = 0
        elif userSum <= 21 and len(userCard) == 5:
            reward = 1
        elif userSum <= 21 and dealSum < userSum or dealSum > 21:
            reward = 1
        else:
            reward = -1
        isTerminal = True
    return state, reward, isTerminal

def reward_to_go(s, gamma, episode):
    # Calculate reward_to_go for a state within an episode
    i = 0
    for e in episode:
        if e == s:
           break
        i+=1
    tmp_episode = episode[i:]
    return pow(gamma,len(tmp_episode) - 1)*tmp_episode[len(tmp_episode) - 1][1]

def MC_Policy_Evaluation(policy, states, gamma, MCvalues, G):
    #Perform 50 simulations in each cycle in each game loop (so total number of simulations increases quickly)
    for simulation in range(50):
        # generate random game
        userCard = []
        dealCard = []
        ccards = copy.copy(cards)
        userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        # do simulation
        episode = simulation_sequence(policy, state, userCard, dealCard, ccards)
        print(episode)
        # update
        for e in episode:
            # Calculate reward_to_go and append to G value
            val = reward_to_go(e, gamma, episode)
            G[e[0]].append(val)

            # Calculate average of G values
            MCvalues[e[0]] = sum(G[e[0]])/len(G[e[0]])

def TD_Policy_Evaluation(policy, states, gamma, TDvalues, NTD):
    #Note to grader: Please give it 3 minutes to run, MC and TD values will converge after that time, thanks!
    #Perform 50 simulations in each cycle in each game loop (so total number of simulations increases quickly)
    for simulation in range(50):
        userCard = []
        dealCard = []
        rewardDict = {}
        ccards = copy.copy(cards)
        userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        # Keep track of rewards for each state
        rewardDict[state] = 0
        lastReward = 0
        lastTerminal = False
        while state is not None:
            # Calculate action based off a policy 
            action = policy(state[0])
            stand = False
            if(action == 1):
                stand = True
            # Increment the number of times visited for a state
            NTD[state] += 1
            # Calculate alpha based off the number of times the state was visited
            alpha = 10/(9 + NTD[state])
            # Simulate one step 
            next_s, reward, isTerminal = simulate_one_step_tmp(state, action, userCard, dealCard, ccards, stand)
            # Check to see if the next state is null
            if(lastTerminal):
                nextTD = 0
            else:
                nextTD = TDvalues[next_s]
            # Calculate TDvalues
            TDvalues[state] = TDvalues[state] + alpha*(rewardDict[state] + gamma*nextTD - TDvalues[state])
            # If the current state is terminal then break out
            if(lastTerminal):
                break
            rewardDict[next_s] = reward
            lastReward = reward
            lastTerminal = isTerminal
            state = next_s

def pick_action(s, eps, Q):
    if(random.uniform(0, 1) < eps):
        return random.choice([0,1])
    else:
        if(Q[s][0] > Q[s][1]):
            return 0
        else:
            return 1

def Q_Learning(states, gamma, Qvalues, NQ):
    # Perform 50 simulations in each cycle in each game loop (so total number of simulations increases quickly)
    for simulation in range(50):
        userCard = []
        dealCard = []
        rewardDict = {}
        ccards = copy.copy(cards)
        userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        # Keep track of rewards for each state
        rewardDict[state] = 0
        eps = 0.3
        lastReward = 0
        lastTerminal = False
        while state is not None:
            # Choose your action based on the pick_action function
            action = pick_action(state, eps, Qvalues)
            stand = False
            if(action == 1):
                stand = True
            # Increment the number of times visited for each state
            NQ[state] += 1
            # Calculate alpha based off the number of times visited for that state
            alpha = 10/(9 + NQ[state])
            # Simulate one step
            next_s, reward, isTerminal = simulate_one_step_tmp(state, action, userCard, dealCard, ccards, stand)
            if(lastTerminal):
                nextQ = 0
            else:
                nextQ = max(Qvalues[next_s][0], Qvalues[next_s][1])
            # Calculate the Q value
            Qvalues[state][action] = Qvalues[state][action] + alpha*(rewardDict[state] + gamma*nextQ - Qvalues[state][action])
            # If your current state is terminal then break out from the loop
            if(lastTerminal):
                break
            rewardDict[next_s] = reward
            lastReward = reward
            lastTerminal = isTerminal
            state = next_s
            
def main():
    ccards = copy.copy(cards)
    stand = False
    userCard = []
    dealCard = []
    winNum = 0
    loseNum = 0
    #Initialize Game
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Blackjack')
    font = pygame.font.SysFont("", 20)
    hitTxt = font.render('Hit', 1, black)
    standTxt = font.render('Stand', 1, black)
    restartTxt = font.render('Restart', 1, black)
    MCTxt = font.render('MC', 1, blue)
    TDTxt = font.render('TD', 1, blue)
    QLTxt = font.render('QL', 1, blue)
    playTxt = font.render('Play', 1, blue)
    gameoverTxt = font.render('End of Round', 1, white)
    #Prepare table of utilities
    G = {}
    MCvalues = {}
    R = {}
    TDvalues = {}
    NTD = {}
    Qvalues = {}
    NQ = {}
    #Initialization of the values
    #i iterates through the sum of user's cards. It is set to 22 if the user went bust. 
    #j iterates through the value of the dealer's first card. Ace is eleven. 
    #a1 is the number of Aces that the user has.
    #a2 denotes whether the dealer's first card is Ace. 
    states = []
    for i in range(2,23):
        for j in range(2,12):
            for a1 in range(0,5):
                for a2 in range(0,2):
                    s = (i,a1,j,a2)
                    states.append(s)
                    #utility computed by MC-learning
                    MCvalues[s] = 0
                    G[s] = []
                    #utility computed by TD-learning
                    TDvalues[s] = 0
                    NTD[s] = 0
                    #first element is Q value of "Hit", second element is Q value of "Stand"
                    Qvalues[s] = [0,0]
                    NQ[s] = 0
    #userSum: sum of user's cards
    #userA: number of user's Aces
    #dealSum: sum of dealer's cards (including hidden one)
    #dealA: number of all dealer's Aces, 
    #dealFirst: value of dealer's first card
    #dealAFirst: whether dealer's first card is Ace
    userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
    state = make_state(userSum, userA, dealFirst, dealAFirst)
    #Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((80, 150, 15))
    hitB = pygame.draw.rect(background, gray, (10, 445, 75, 25))
    standB = pygame.draw.rect(background, gray, (95, 445, 75, 25))
    MCB = pygame.draw.rect(background, white, (180, 445, 75, 25))
    TDB = pygame.draw.rect(background, white, (265, 445, 75, 25))
    QLB = pygame.draw.rect(background, white, (350, 445, 75, 25))
    playB = pygame.draw.rect(background, white, (435, 445, 75, 25))
    autoMC = False
    autoTD = False
    autoQL = False
    autoPlay = False
    #Event loop
    while True:
        #Our state information does not take into account of number of cards
        #So it's ok to ignore the rule of winning if getting 5 cards without going bust
        if (userSum >= 21 and userA == 0) or len(userCard) == 5:
            gameover = True
        else:
            gameover = False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        if autoMC:
            #MC Learning
            #Compute the utilities of all states under the policy "Always hit if below 17"
            MC_Policy_Evaluation(policy, states, 0.9, MCvalues, G)
        if autoTD:
            #TD Learning
            #Compute the utilities of all states under the policy "Always hit if below 17"
            TD_Policy_Evaluation(policy, states, 0.9, TDvalues, NTD)
        if autoQL:
            #Q-Learning
            #For each state, compute the Q value of the action "Hit" and "Stand"
            Q_Learning(states, 0.9, Qvalues, NQ)
        if autoPlay:
            state = make_state(userSum, userA, dealFirst, dealAFirst)
            hitQ, standQ = Qvalues[state][0], Qvalues[state][1]
            decision = None
            if hitQ > standQ:
                decision = "hit"
            elif standQ > hitQ:
                decision = "stand"
            else:
                if userSum < 17:
                    decision = "hit"
                else:
                    decision = "stand"
            if (gameover or stand):
                #restart the game, updating scores
                if userSum == dealSum:
                    pass
                elif userSum <= 21 and len(userCard) == 5:
                    winNum += 1
                elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
            elif not (gameover or stand) and decision == "hit":
                #Give player a card
                card, cA = genCard(ccards, userCard)
                userA += cA
                userSum += getAmt(card)
                while userSum > 21 and userA > 0:
                    userA -= 1
                    userSum -= 10
            elif not gameover and decision == "stand":
                #Dealer plays, user stands
                stand = True
                if dealSum == 21:
                    pass
                else:
                    while dealSum <= userSum and dealSum < 17:
                        card, cA = genCard(ccards, dealCard)
                        dealA += cA
                        dealSum += getAmt(card)
                        while dealSum > 21 and dealA > 0:
                            dealA -= 1
                            dealSum -= 10
            
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #Clicking the white buttons can start or pause the learning processes
            elif event.type == pygame.MOUSEBUTTONDOWN and MCB.collidepoint(pygame.mouse.get_pos()):
                autoMC = not autoMC
            elif event.type == pygame.MOUSEBUTTONDOWN and TDB.collidepoint(pygame.mouse.get_pos()):
                autoTD = not autoTD
            elif event.type == pygame.MOUSEBUTTONDOWN and QLB.collidepoint(pygame.mouse.get_pos()):
                autoQL = not autoQL
            elif event.type == pygame.MOUSEBUTTONDOWN and playB.collidepoint(pygame.mouse.get_pos()):
                autoPlay = not autoPlay
            elif event.type == pygame.MOUSEBUTTONDOWN and (gameover or stand) and not autoPlay:
                #restarts the game, updating scores
                if userSum == dealSum:
                    pass
                elif userSum <= 21 and len(userCard) == 5:
                    winNum += 1
                elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
            elif event.type == pygame.MOUSEBUTTONDOWN and not (gameover or stand) and hitB.collidepoint(pygame.mouse.get_pos()) and not autoPlay:
                #Give player a card
                card, cA = genCard(ccards, userCard)
                userA += cA
                userSum += getAmt(card)
                while userSum > 21 and userA > 0:
                    userA -= 1
                    userSum -= 10
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameover and standB.collidepoint(pygame.mouse.get_pos()) and not autoPlay:
                #Dealer plays, user stands
                stand = True
                if dealSum == 21:
                    pass
                else:
                    while dealSum <= userSum and dealSum < 17:
                        card, cA = genCard(ccards, dealCard)
                        dealA += cA
                        dealSum += getAmt(card)
                        while dealSum > 21 and dealA > 0:
                            dealA -= 1
                            dealSum -= 10
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        MCU = font.render('MC-Utility of Current State: %f' % MCvalues[state], 1, black)
        TDU = font.render('TD-Utility of Current State: %f' % TDvalues[state], 1, black)
        QV = font.render('Q values: (Hit) %f (Stand) %f' % (Qvalues[state][0], Qvalues[state][1]) , 1, black)
        winTxt = font.render('Wins: %i' % winNum, 1, white)
        loseTxt = font.render('Losses: %i' % loseNum, 1, white)
        screen.blit(background, (0, 0))
        screen.blit(hitTxt, (39, 448))
        screen.blit(standTxt, (116, 448))
        screen.blit(MCTxt, (193, 448))
        screen.blit(TDTxt, (280, 448))
        screen.blit(QLTxt, (357, 448))
        screen.blit(playTxt, (444, 448))
        screen.blit(winTxt, (550, 423))
        screen.blit(loseTxt, (550, 448))
        screen.blit(MCU, (20, 200))
        screen.blit(TDU, (20, 220))
        screen.blit(QV, (20, 240))
        for card in dealCard:
            x = 10 + dealCard.index(card) * 110
            screen.blit(card, (x, 10))
        screen.blit(cBack, (120, 10))
        for card in userCard:
            x = 10 + userCard.index(card) * 110
            screen.blit(card, (x, 295))
        if gameover or stand:
            screen.blit(gameoverTxt, (270, 200))
            screen.blit(dealCard[1], (120, 10))
        pygame.display.update()

if __name__ == '__main__':
    main()

