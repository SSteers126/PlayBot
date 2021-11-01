import secrets
import copy
import store
from games.cards.decks import gen52Deck
from shuffle.secret import secretShuffle
from discord import Embed, Colour

def getCardValue(card):
    valueStr = card.split(" ")[0]
    # print(card.split(" "))
    # print(card)
    # print("ee")
    # print(valueStr)
    try:
        return int(valueStr)
    except:
        if valueStr == "Ace":
            # print("ace")
            return [1, 11]
        else:
            return 10

class BlackjackBoard:
    def __init__(self):
        self.inUse = True
        self.starting = True
        self.boardMessage = None
        self.boardMessage = None
        self.round = 0

        self.deck = None
        self.dealer = {"cards": [], "values": [0]}
        self.players = {}

    def report(self):
        reportDict = {}
        for playerid in self.players:
            reportDict[self.players[playerid]["name"]] = {"amount": len(self.players[playerid]["hand"]["cards"]),
                                                          "cards": self.players[playerid]["hand"]["cards"][1:]}
        dealerDict = {"amount": len(self.dealer["cards"]), "cards": self.dealer["cards"][1:]}

        return reportDict, dealerDict

    def addPlayer(self, playerid, tag, name, messageable):
        if playerid in self.players:
            return False

        else:
            self.players[playerid] = {"name": name, "tag": tag, "messageable": messageable, "DM": None,
                                "hand": {"cards": [], "values": [0]}, "inPlay": True, "folded": False, "bust": False,
                                "wins": 0, "losses": 0, "21s": 0}
            return True

    def reset(self):
        self.round += 1
        for playerid in self.players:
            self.players[playerid]["hand"] = {"cards": [], "values": [0]}
            self.players[playerid]["inPlay"] = True
            self.players[playerid]["folded"] = False
            self.players[playerid]["bust"] = False
        self.dealer = {"cards": [], "values": [0]}

        self.deck = secretShuffle(gen52Deck())

    def drawCards(self, amount, cards=[], values=[0]):
        """Draws 'amount' cards and then uses those to create possible values for that hand"""
        newCards = []
        newVals = [0]

        for i in range(amount):
            cards.append(self.deck.pop())

        for count, card in enumerate(cards):
            if card.split(" ")[0] == "Ace":
                # Allows for the second value of the ace to change, and dynamically use it to add all possible values
                newVals.append(newVals[-1]+((cardvals := getCardValue(card))[1]-1))
                for count, value in enumerate(newVals):
                    newVals[count] += cardvals[0]

            else:
                for count, value in enumerate(newVals):
                    newVals[count] += getCardValue(card)

        return [cards, newVals]

    def startRound(self):
        # self.deck = gen52Deck() # Use in combination with edited deck generation for deterministic gameplay
        # Code could be shorter by giving 2 cards at a time, but it would also change what is dealt.
        # self.deck = secretShuffle(gen52Deck())

        self.reset()
        # Reset function will run some unneeded code for the first round,
        # but guarantees all players are in a new state for subsequent rounds.

        for dealRound in range(2):
            # print(count)
            for playerid in self.players:
                draw = self.drawCards(1, self.players[playerid]["hand"]["cards"],
                                      self.players[playerid]["hand"]["values"])

                self.players[playerid]["hand"]["cards"] = draw[0]
                self.players[playerid]["hand"]["values"] = draw[1]

            dealerDraw = self.drawCards(1, self.dealer["cards"], self.dealer["values"])
            self.dealer["cards"] = dealerDraw[0]
            self.dealer["values"] = dealerDraw[1]

        return True

    def hit(self, playerid):
        draw = self.drawCards(1, self.players[playerid]["hand"]["cards"], self.players[playerid]["hand"]["values"])
        self.players[playerid]["hand"]["cards"] = draw[0]
        self.players[playerid]["hand"]["values"] = draw[1]

        return True

    def fold(self, playerid):
        self.players[playerid]["inPlay"] = False
        self.players[playerid]["folded"] = True
        return True

    def eval(self):
        topvalue = 0
        topPlayers = []
        cardlist = []
        for playerid in self.players:
            playertop = -1
            if not self.players[playerid]["bust"]:
                for value in self.players[playerid]["hand"]["values"]:
                    if 21 >= value > playertop:
                        playertop = value
            if playertop >= topvalue:
                if playertop > topvalue:
                    topPlayers = []
                    cardlist = []
                    topvalue = playertop
                topPlayers.append(self.players[playerid]["name"])
                cardlist.append(self.players[playerid]["hand"]["cards"])

        dealertop = -1
        for value in self.dealer["values"]:
            # print(value)
            if value <= 21:
                if value > dealertop:
                    # print(value)
                    dealertop = value
        # print(dealertop)

        draw = False
        if topvalue >= dealertop:  # Best hands are also shown on a draw
            winners = topPlayers
        elif topvalue == dealertop:
            draw = True
            cardlist.append(self.dealer["cards"])
        elif dealertop == -1:
            winners = None
        else:
            winners = ["Dealer"]

        for winner in winners:
            pass  # TODO: add user object so value can be added to dictionary
            for playerid in self.players:
                if self.players[playerid]["name"] == winner:
                    self.players[playerid]["wins"] += 1
                else:
                    self.players[playerid]["losses"] += 1

        return winners, draw, topvalue, topPlayers, dealertop, cardlist

    def getWinnerDict(self):
        winDict = {}
        for playerid in self.players:
            if (score := self.players[playerid]["wins"]) not in winDict:
                winDict[score] = [self.players[playerid]["name"]]
            else:
                winDict[score].append(self.players[playerid]["name"])

        # winDict[1] = "abc"

        return winDict

def genReportEmbed():
    gameReport, dealerReport = store.blackjackGame.report()
    reportStr = ""
    for name in gameReport:
        cardStr = ""
        for card in gameReport[name]["cards"]:
            cardStr += "{0}, ".format(card)
        cardStr = cardStr[:-2]

        reportStr += "{0}: {1} cards, {2} is visible\n".format(name, gameReport[name]["amount"], cardStr)

    cardStr = ""
    for card in dealerReport["cards"]:
        cardStr += "{0}, ".format(card)
    cardStr = cardStr[:-2]

    reportStr += "Dealer: {0} cards, {1} is visible\n".format(dealerReport["amount"], cardStr)

    jackEmbed = Embed(title="{0}'s Blackjack game - round {1}\n"
                                    "Player count: {2}".format(store.blackjackOwner,
                                                               store.blackjackGame.round,
                                                               len(store.blackjackGame.players)),
                              description="Table: {0}".format(reportStr),
                              colour=Colour(255).from_rgb(255, 0, 0))
    jackEmbed.set_thumbnail(
        url="https://www.dropbox.com/s/ghctzpqy93r2b3d/JackHeart-clean.png?dl=1")

    return jackEmbed