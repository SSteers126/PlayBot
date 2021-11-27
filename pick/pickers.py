from secrets import randbelow
from shuffle.secret import secretShuffle
from games.cards.decks import gen52Deck

def coinFlip():
    choice = randbelow(2)
    print(choice)
    if choice == 1:
        return "Tails"
    else:
        return "Heads"

def pickCard(decktype="52"):
    if decktype == "52":
        deck = secretShuffle(gen52Deck())

    return deck[0]