import json
import random

def getInt(i):
    try:
        return int(i)
    except ValueError:
        return False

def getLimitedInt(i, lo, hi):
    i = getInt(i)
    return i if lo <= i < hi else False

def betterInput(prompt, validate, *opts):
    i = False
    while i == False: 
        i = validate(input(prompt), *opts)
    return i

def main():
    # Load Cards
    gameset = readFromFile("cludo.json")
    
    # Get number of humans and computers
    humans = betterInput("Enter number of humans (up to 6)? ", getLimitedInt, 1, 6)
    computers = betterInput("Enter number of computers (up to "+str(6-humans)+")? ", getLimitedInt, 0, 6-humans))
    
    # Count cards and deal making sure all players N or N+1 cards
    cardCount = countCards(gameset) - len(gameset.keys())
    cardPerPlayer = cardCount // (humans + computers)
    extraCard = cardCount % (humans + computers)
    cardsPP = [cardPerPlayer + 1 if i < extraCard else cardPerPlayer for i in range(humans + computers)]
    assert(sum(cardsPP) == cardCount)
    
    # Prompt user to deal human cards
    for i in range(0,humans):
        print("Deal", cardsPP[i], "cards to player", i + 1)    
    print("Place remaining cards in pile")
    input()
    
    # World represents the cards that have not been delt yet
    world = {}
    for k,v in gameset.items():
        world[k] = list(range(len(v)))

    # PlayerCards is a list that stores a map of categories, the key is
    # a list one 3 items. The first list is the numerical representation of the card
    # the second is the string name of that card, the thrid is a boolean representing
    # whether or not that card has been shown to anyone already.
    playersCards = []

    # Get player cards
    for i in range(humans):
        print("Enter cards for player", i + 1)
        cards,change = getHumanCards(gameset, cardsPP[i])
        print("You've entered this:")
        printPlayerDeck(cards)
        while betterInput("Is this correct [y/n]? ", oneOf, ["y","n"]):
            cards, change = getHumanCards(gameset, world, cardsPP[i])
            print("You've entered this:")
            printPlayerDeck(cards)
        playersCards += [cards]
        # Delete changed cards from the world 
        [world[v[0]].remove(v[1]) for v in change ]
        # Clear Screen
        print(chr(27) + "[2J")

    # If the world doesn't have one card in a given category the player has to redeal
    for v in world.values():
        if len(v) == 0:
            print("Sadly you need to redeal the cards")
            return
    
    # Select 1 card from each category
    answer = [[],[]]
    for k in list(world.keys()):
        card = drawFromCategory(world, k)
        answer[0] += [card]
        answer[1] += [gameset[card[0]][card[1]]]
    assert(len(answer[0]) == 3)
    
    # Assign the computer cards
    for i in range(computers):
        cards = {}
        for k in gameset:
            cards[k] = [[],[],[]]
        for j in range(cardsPP[humans+i]):
            card = drawFromWorld(world) 
            cards[card[0]][0] += [card[1]]
            cards[card[0]][1] += [gameset[card[0]][card[1]]]
            cards[card[0]][2] += [False]
        playersCards += [cards]

    # Allow user to query state
    while True:
        i = betterInput("Enter 'q' to ask a question or 'g' to guess the answer: ", oneOf, ["q","answer","a"])
        if i == 'q':
            i = betterInput("Who would you like to ask? ", getLimitedInt, 1, humans + computers) - 1
            if 0 <= i < computers + humans:
                card = playersCards[i]
                inp = getInput(gameset)
                pOptions = []
                for x in inp:
                    options = [ x for x in inp if x[1] in card[x[0]][0] ]
                    try:
                        index_of_item = card[x[0]][0].index(x[1])
                        if card[x[0]][2][index_of_item]:
                            pOptions.append(x)
                    except ValueError:
                        pass
                if len(pOptions) > 0:
                    options = pOptions 
                if len(options) == 0:
                    print("Player", i+1,"has none of those")
                else:
                    chosen = random.choice(options)
                    c = card[chosen[0]]
                    index = c[0].index(chosen[1])
                    c[2][index] = True
                    print("Player", i+1,"has", c[1][index])
                input()
                print(chr(27) + "[2J")
        elif i == 'a':
            inp = getInput(gameset)
            if inp == answer[0]:
                print("You win, the answer was", answer[1])
                return
            else:
                print("That's not the right answer")
        elif i == 'answer':
            print(answer)
                
def getInput(deck):
    results = []
    for k in deck:
        for i in range(len(deck[k])):
            print(i,":", deck[k][i])
        i = int(input("Pick a "+k+": "))
        if 0 <= i < len(deck[k]):
            results += [(k,i)]
    return results

def drawFromWorld(world):
    cat = random.choice(list(world))
    return drawFromCategory(world, cat)

def drawFromCategory(world, category):
    n = random.choice(world[category])
    world[category].remove(n)
    if len(world[category]) == 0:
        del world[category]
    return (category,n)

def printPlayerDeck(cards):
    for k,v in cards.items():
        print(k + ":")
        print(v[1])

def getHumanCards(deck, amount):
    change = []
    cards = {}
    cardsEntered = 1
    for k in deck:
        cards[k] = [[],[],[]]
        for i in range(len(deck[k])):
            print(i,":", deck[k][i])
        print("-- Type [done] to go to next category--")
        cardIn = input("Enter card ["+str(cardsEntered)+"/"+str(amount)+"]: ")
        while cardIn.lower() != "done":
            cardIn = int(cardIn)
            if cardIn not in cards[k] and 0 <= cardIn < len(deck[k]):
                cards[k][0] += [cardIn]
                cards[k][1] += [deck[k][cardIn]]
                cards[k][2] += [False]
                change += [(k,cardIn)]
                cardsEntered +=1
            cardIn = input("Enter card ["+str(cardsEntered)+"/"+str(amount)+"]: ")
    return cards, change

def readFromFile(filename):
    with open(filename) as json_file:  
        return json.load(json_file)

def countCards(gameset):
    return sum([ len(v) for v in gameset.values()])
    
#if __name__ == "__main__":
    #main()
