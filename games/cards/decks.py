def gen52Deck():
    houses = ["♤", "♦", "♧", "♥"] #♠♢♣♡
    values = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
    deck = []
    for house in houses:
        for value in values:
            deck.append("{0} of {1}".format(value, house))

    # With 1 player, guarantees player and dealer get blackjack
    # deck.append("Ace of x")
    # deck.append("Ace of x")
    # deck.append("10 of x")
    # deck.append("10 of x")
    return deck

# print(gen52Deck())
# print(len(gen52Deck()))
