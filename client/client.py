import time

import discord

import CONSTANTS
import store
import games

from asyncio import TimeoutError as asyncTimeout

def messageStartsWith(matching, message):
    return message.content.split(" ")[0].lower() == ("{0}{1}".format(CONSTANTS.PREFIX, matching))

class PlayBot(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        currentChannel = message.channel

        if messageStartsWith("cleanup", message):
            mgs = []
            numdel = int(message.content.split(" ")[1])
            delay = 10

            cd_message = await message.channel.send("Commencing cleanup of {0} messages in {1} seconds...".format(numdel, delay))
            for count, winner in enumerate(range(delay)):
                time.sleep(1)
                if count == delay-1:
                    await cd_message.delete()
                else:
                    await cd_message.edit(content="Commencing cleanup of {0} messages in {1} seconds...".format(numdel, delay-(count+1)))

            for winner in range(numdel):
                try:
                    mgs.append(x := await currentChannel.history().get(author__name='ASHE-Bot'))
                    print("got message {}".format(str(x)))
                    await currentChannel.delete_messages(mgs)
                    mgs = []
                except Exception as e:
                    if x is None:
                        await currentChannel.send("No messages are left to clean up.", delete_after=5.0)
                        break
                    else:
                        print(e)

        if messageStartsWith("cleancommands", message):
            numdel = int((arguments := message.content.split(" ")[1:])[0])
            try:
                limit = arguments[1]
            except:
                limit = numdel * 5

            async for histMessage in currentChannel.history(limit=limit):
                print(histMessage.content)
                print(preftext := str(histMessage.content)[:len(CONSTANTS.PREFIX)])
                if preftext == CONSTANTS.PREFIX:
                    await histMessage.delete()

        if messageStartsWith("purge", message):
            numdel = int(message.content.split(" ")[1])
            await currentChannel.purge(limit=numdel)
            await currentChannel.send("Purged {} messages!".format(numdel), delete_after=5.0)

        if messageStartsWith("test", message):
            # await currentChannel.send("Hello, {0} [name {1}]!".format(message.author.mention, message.author.name))
            if store.blackjackGame.addPlayer(0, message.author.mention, "testPlayer"):
                names = ""
                players = len(store.blackjackGame.players)
                for count, id in enumerate(store.blackjackGame.players):
                    names += "{}, ".format(store.blackjackGame.players[id]["name"])
                    if count + 1 == players:
                        names = names[:-2]
                jackEmbed = discord.Embed(title="{0} is starting a blackjack game!\n"
                                                "Player count: {1}".format(message.author.name,
                                                                           len(store.blackjackGame.players)),
                                          description="Player(s): {0}".format(names),
                                          colour=discord.Colour(255).from_rgb(255, 0, 0), )
                jackEmbed.set_thumbnail(url="https://www.dropbox.com/s/ghctzpqy93r2b3d/JackHeart-clean.png?dl=1")

                await store.blackjackGame.boardMessage.edit(embed=jackEmbed)

        if messageStartsWith("startjack", message):
            # await currentChannel.send("Sorry, this is not implemented yet!")
            if store.blackjackGame is None or not store.blackjackGame.inUse:

                store.blackjackGame = games.BlackjackBoard()
                store.blackjackGame.addPlayer(message.author.id, message.author.mention, message.author.name, message.author)
                # await store.blackjackGame.players[message.author.id]["messageable"].send("hello again!")
                # jackimg = discord.File("JackHeart-clean.png", filename="JackHeart-clean.png")
                jackEmbed = discord.Embed(title="{0} is starting a Blackjack game!\n"
                                                "Player count: {1}".format(message.author.name, len(store.blackjackGame.players)),
                                          description="Player(s): {0}".format(message.author.name),
                                          colour=discord.Colour(255).from_rgb(255, 0, 0),)
                jackEmbed.set_thumbnail(url="https://www.dropbox.com/s/ghctzpqy93r2b3d/JackHeart-clean.png?dl=1")
                # store.blackjackGame.statusMessage = \
                #     await currentChannel.send("{0} is starting a blackjack game!\n"
                #                               "Player count: {1}"
                #                               .format(message.author.mention, len(store.blackjackGame.players)))
                store.blackjackGame.boardMessage = await currentChannel.send(embed=jackEmbed)
                await message.delete()
                store.blackjackOwner = message.author.name


        if messageStartsWith("joinjack", message):
            if store.blackjackGame is not None and store.blackjackGame.starting:
                if store.blackjackGame.addPlayer(message.author.id, message.author.mention, message.author.name, message.author):
                    names = ""
                    players = len(store.blackjackGame.players)
                    for count, id in enumerate(store.blackjackGame.players):
                        names += "{}, ".format(store.blackjackGame.players[id]["name"])
                        if count+1 == players:
                            names = names[:-2]
                    jackEmbed = discord.Embed(title="{0} is starting a Blackjack game!\n"
                                                    "Player count: {1}".format(store.blackjackOwner,
                                                                               len(store.blackjackGame.players)),
                                              description="Player(s): {0}".format(names),
                                              colour=discord.Colour(255).from_rgb(255, 0, 0), )
                    jackEmbed.set_thumbnail(url="https://www.dropbox.com/s/ghctzpqy93r2b3d/JackHeart-clean.png?dl=1")

                    await store.blackjackGame.boardMessage.edit(embed=jackEmbed)
                    await message.delete()

        if messageStartsWith("playjack", message):
            joined = False
            for playerid in store.blackjackGame.players:
                if playerid == message.author.id:
                    joined = True
            if not joined:
                await message.channel.send("{0}, you need to be in the game to start it!".format(message.author.mention), delete_after=5.0)
            else:
                if store.blackjackGame is not None and store.blackjackGame.starting:
                    store.blackjackGame.starting = False

                    if store.blackjackGame.startRound():
                        playAgain = True
                        while playAgain:
                            jackEmbed = games.genReportEmbed()
                            store.blackjackGame.boardMessage = await currentChannel.send(embed=jackEmbed)
                            await message.delete()

                            # used to tell if people have a possible play left,
                            # or will be notified of a fold/bust before showing results
                            playersLeft = True
                            # lastRun = False

                            while playersLeft:
                                playersLeft = False
                                playingBeforeMove = False
                                if store.blackjackGame.players[playerid]["inPlay"]:
                                    playingBeforeMove = True  # Faster than deepcopy
                                    # print("playingbeforemove")
                                for playerid in store.blackjackGame.players:
                                    boardEmbed = games.genReportEmbed()
                                    await store.blackjackGame.boardMessage.edit(embed=boardEmbed)
                                    if store.blackjackGame.players[playerid]["inPlay"] and not store.blackjackGame.players[playerid]["folded"]:

                                        valueStr = ""
                                        for value in store.blackjackGame.players[playerid]["hand"]["values"]:
                                            valueStr += "{0} or ".format(value)
                                            # Used if blackjack is drawn in the first two card
                                            if value == 21:
                                                store.blackjackGame.players[playerid]["inPlay"] = False

                                        valueStr = valueStr[:-4]


                                        playStr = "Do you want to hit {0}, or fold {1}?".format(CONSTANTS.HIT, CONSTANTS.FOLD)
                                        playable = True


                                    if (not store.blackjackGame.players[playerid]["inPlay"] and not store.blackjackGame.players[playerid]["folded"] and not store.blackjackGame.players[playerid]["bust"]):  # This is only reached when the hand has a value of 21
                                        valueStr = "Blackjack!"
                                        playStr = "No need to play on Blackjack!"
                                        playable = False
                                        store.blackjackGame.players[playerid]["inPlay"] = False

                                    if store.blackjackGame.players[playerid]["folded"]:
                                        playStr = "You folded. You cannot make any moves."
                                        playable = False
                                        store.blackjackGame.players[playerid]["inPlay"] = False

                                    if store.blackjackGame.players[playerid]["bust"]:
                                        playStr = "You went bust. You cannot make any moves."
                                        playable = False
                                        store.blackjackGame.players[playerid]["inPlay"] = False

                                    handStr = ""
                                    for card in store.blackjackGame.players[playerid]["hand"]["cards"]:
                                        handStr += "{0}, ".format(card)
                                    handStr = handStr[:-2]

                                    dmEmbed = discord.Embed(title="{0}'s Blackjack game - round {1}".format
                                        (store.blackjackOwner, store.blackjackGame.round),
                                                            description="Your hand: {0}\n"
                                                                        "Value(s) of hand: {1}\n"
                                                                        "{2}".format
                                                            (handStr, valueStr, playStr),
                                                            colour=discord.Colour(255))
                                    dmEmbed.set_thumbnail(
                                        url="https://www.dropbox.com/s/ghctzpqy93r2b3d/JackHeart-clean.png?dl=1")
                                    store.blackjackGame.players[playerid]["DM"] = \
                                        await store.blackjackGame.players[playerid]["messageable"].send(embed=dmEmbed)


                                    if playable:
                                        reacts = [CONSTANTS.HIT, CONSTANTS.FOLD]
                                        for reaction in reacts:
                                            await store.blackjackGame.players[playerid]["DM"].add_reaction(reaction)

                                        # Since this is in DMs, we already know the user. we only need the reaction
                                        # reaction, _ = await store.blackjackGame.players[playerid]["DM"].wait_for("reaction_add", check=)
                                        try:
                                            reaction, _ = await client.wait_for('reaction_add',
                                                                                   check=lambda
                                                                                       r, u: u.id ==
                                                                                       store.blackjackGame.players
                                                                                       [playerid]["messageable"].id,
                                                                                   timeout=30)
                                            stri = "a"
                                            stri.encode("utf-8")
                                            if (reactutf := str(reaction).encode("utf-8")) == CONSTANTS.HIT.encode("utf-8"):
                                                store.blackjackGame.hit(playerid)
                                            elif reactutf == CONSTANTS.FOLD.encode("utf-8"):
                                                store.blackjackGame.fold(playerid)
                                            else:
                                                print("found non matching reaction")
                                                print(reaction)
                                                print(reactutf)
                                                print(reacts)

                                        except asyncTimeout:
                                            store.blackjackGame.fold(playerid)
                                            await store.blackjackGame.players[playerid]["messageable"].send("Due to inactivity, "
                                                                                                    "you have been forced to fold.")

                                    # store.blackjackGame.players[playerid]["inPlay"] = False
                                    store.blackjackGame.players[playerid]["bust"] = False
                                    altVal = False  # Used when aces have hand values above and below 21
                                    for value in store.blackjackGame.players[playerid]["hand"]["values"]:
                                        # if value < 21:
                                        #     store.blackjackGame.players[playerid]["inPlay"] = True

                                        if value > 21 and not altVal:
                                            store.blackjackGame.players[playerid]["bust"] = True
                                            break
                                        else:
                                            altVal = True

                                    # print(playingBeforeMove)
                                    if store.blackjackGame.players[playerid]["inPlay"] or playingBeforeMove:
                                        playersLeft = True




                            # TODO: Evaluate scores and show winner

                            winners, draw, topvalue, topPlayers, dealertop, cardlist = store.blackjackGame.eval()

                            if winners is None:
                                desc = "Everyone went bust. No one wins."
                            elif winners == ["Dealer"]:
                                desc = "The dealer won with a score of {0}!".format(dealertop)
                                cardlist = []
                                cardlist.append(store.blackjackGame.dealer["cards"])
                            elif draw:
                                winnerStr = ""
                                for winner in winners:
                                    winnerStr += "{0} and".format(winner)
                                winnerStr = winnerStr[:-4]
                                desc = "{0} drew with the dealer with a score of {1}!".format(winnerStr, topvalue)
                            else:
                                winnerStr = ""
                                for winner in winners:
                                    winnerStr += "{0} and".format(winner)
                                winnerStr = winnerStr[:-4]
                                if len(winners) > 1:
                                    winnerStr += "all"
                                desc = "{0} won with a score of {1}!".format(winnerStr, topvalue)

                            winHands = ""
                            for hand in cardlist:
                                for card in hand:
                                    winHands += "{0}, ".format(card)
                                winHands = winHands[:-2]
                                winHands += " | "
                            winHands = winHands[:-3]

                            firstWinPic = None
                            # Get the first winner's profile picture, if there is only dealer
                            # then default to normal picture
                            for playerid in store.blackjackGame.players:
                                isWinner = False
                                for winner in winners:
                                    if winner == store.blackjackGame.players[playerid]["name"]:
                                        isWinner = True
                                        firstWinPic = store.blackjackGame.players[playerid]["messageable"].avatar_url
                                        break
                                if isWinner:
                                    break

                            evalEmbed = discord.Embed(title="{0}'s Blackjack game - round {1} results".format
                                        (store.blackjackOwner, store.blackjackGame.round),
                                                            description="{0}\n"
                                                                        "Winning cards: {1}".format
                                                            (desc, winHands),
                                                            colour=discord.Colour(255).from_rgb(255, 0, 0))
                            evalEmbed.set_thumbnail(url="https://www.dropbox.com/s/ghctzpqy93r2b3d/JackHeart-clean.png?dl=1")
                            await message.channel.send(embed=evalEmbed)
                            # TODO: work on evaluation embed to include winners etc, and then use reactions
                            #  to work with multiple rounds.
                            replayEmbed = discord.Embed(title="EvalTest")
                            if firstWinPic is not None:
                                replayEmbed.set_thumbnail(url=firstWinPic)
                            else:
                                replayEmbed.set_thumbnail(url="https://www.dropbox.com/s/ghctzpqy93r2b3d/JackHeart-clean.png?dl=1")

                            await message.channel.send(embed=replayEmbed)

                            break



                            # TODO: clean up winner string generator for drawing, and then add the ability to play more rounds,
                            #  and to message bust/folded players without giving choices
                            #  (may the case that it only occurs when multiple people are playing, test this)