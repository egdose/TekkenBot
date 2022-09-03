"""
A bot that plays passively/defensively with pokes, waiting to punish and small counters

"""

import random
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

        # To count how many updates have passed since we last did a random action
        self.tick_till_next_rand = 0

        # Prevent doing nothing as a random action for too long
        self.last_rand_action_was_nth = False

        # True if we had to cover distance in order to get into poking range
        # for the pervious action
        self.last_asked_poke = False


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
                # Do nothing if bot is countering
                if not BotBehaviors.DefendAndCounter(gameState, self.botCommands, self.gameplan):
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
                            return
                
                # TODO: Make this better
                # Sometimes interferes collides with countering/blocking
                #self.TESTING_RandomAction(gameState)

    def TESTING_RandomAction(self, gameState: TekkenGameState):
        self.tick_till_next_rand += 1
        # Do a random action after set updates calls
        # NOTE: Not frames; Update calls
        if self.tick_till_next_rand >= 32:
            self.DoRandomAction(gameState)

    def DoRandomAction(self, gameState: TekkenGameState):
        """
        Do a random action.

        Possible actions are:
        - Poking (If within target distace)
        - Dashing (Towards a set distance)
        - Walking (Walking towards a set distance)
        - Ducking
        - Stepstep
        - Nothing
        """
        actionRNG = random.randint(1, 100)
        # Anything generated above this number, the bot chooses to poke
        POKE_CAP = 50
        DASH_CAP = 35
        DUCK_CAP = 20
        SIDESTEP_CAP = 10
        WALK_CAP = 5

        TARGET_DISTANCE = 2000.0 # 2.00

        # Ensure we dont do nothing for twice in a row
        if self.last_rand_action_was_nth:
            actionRNG += SIDESTEP_CAP
            self.last_rand_action_was_nth = False

        # Try to poke if the last action was spent getting
        # into range for pokes
        if self.last_asked_poke:
            actionRNG += POKE_CAP

        if actionRNG >= POKE_CAP:
            # Not in range, dash towards
            if TARGET_DISTANCE < gameState.GetDist():
                self.DashTowardsTargetDist(TARGET_DISTANCE, gameState)
                self.last_asked_poke = not self.last_asked_poke
            else:
                self.RandomPoke()
                self.last_asked_poke = False
        elif actionRNG >= DASH_CAP:
            self.DashTowardsTargetDist(TARGET_DISTANCE, gameState)
        elif actionRNG >= DUCK_CAP:
            # duck for a few frames
            self.botCommands.BlockLowFull(random.randint(8, 12))
        elif actionRNG >= SIDESTEP_CAP:
            # Pick between SS up or down
            if (random.randint(0, 1) == 0):
                self.botCommands.SidestepUp()
            else:
                self.botCommands.SidestepDown()
        elif actionRNG >= WALK_CAP:
            self.WalkTowardsTargetDist(TARGET_DISTANCE, gameState)
        else:
            self.last_rand_action_was_nth = True

        self.tick_till_next_rand = 0
    
    def WalkTowardsTargetDist(self, target_dist: float, gameState: TekkenGameState):
        """
        Walks a bit towards the target distance.
        """

        walkFrames = random.randint(8, 12)

        if target_dist > gameState.GetDist():
            self.botCommands.WalkBackwards(walkFrames)
        else:
            self.botCommands.WalkForward(walkFrames)

    def DashTowardsTargetDist(self, target_dist: float, gameState: TekkenGameState):
        """
        Dash once towards the target distance.
        """
        if target_dist > gameState.GetDist():
            self.botCommands.BackdashFull()
        else:
            self.botCommands.Fowarddash()
    
    def RandomPoke(self):
        poke = self.gameplan.GetRandomMove(ResponseTypes.pokes)
        if poke != None:
            self.botCommands.AddCommand(poke)



