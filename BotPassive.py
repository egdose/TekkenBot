"""
A bot that plays passively/defensively with pokes, waiting to punish and small counters

"""

from Bot import Bot
from TekkenGameState import TekkenGameState
from TekkenEncyclopedia import TekkenEncyclopedia
from BotData import BotBehaviors
from CharacterData import *


class BotPassive(Bot):

    def __init__(self, botCommands):
        super().__init__(botCommands)
        self.gameplan = None
        self.enemyCyclopedia = TekkenEncyclopedia(False)


    def Update(self, gameState: TekkenGameState):

        self.enemyCyclopedia.Update(gameState)

        if gameState.WasFightReset():
            self.botCommands.ClearCommands()
            self.gameplan = None

        if self.gameplan == None :
            char_id = gameState.GetBotCharId()
            if char_id != None:
                self.gameplan = GetGameplan(char_id)

        if self.gameplan != None:
            BotBehaviors.Basic(gameState, self.botCommands)
            if self.botCommands.IsAvailable():

                if BotBehaviors.TryBreakThrows(gameState, self.botCommands):
                    return

                # Do nothing if bot is countering
                if BotBehaviors.DefendAndCounter(gameState, self.botCommands, self.gameplan):
                    return

                frameAdvantage = None
                if gameState.IsBotBlocking():
                    frameAdvantage = self.enemyCyclopedia.GetFrameAdvantage(gameState.GetOppMoveId())
                elif gameState.IsBotGettingHit():
                    frameAdvantage = self.enemyCyclopedia.GetFrameAdvantage(gameState.GetOppMoveId(), isOnBlock=False)
                else:
                    BotBehaviors.TechThrows(gameState, self.botCommands)

                try:
                    frameAdvantage = int(frameAdvantage) * -1
                except:
                    frameAdvantage = None

                if frameAdvantage != None:
                    if frameAdvantage >= 10:
                        if gameState.IsBotWhileStanding():
                            punish = self.gameplan.GetMoveByFrame(ResponseTypes.ws_punishes, frameAdvantage)
                        else:
                            punish = self.gameplan.GetMoveByFrame(ResponseTypes.st_punishes, frameAdvantage)
                        if punish != None:
                            self.botCommands.AddCommand(punish)
            else:
                print("No Bot Cmd")




