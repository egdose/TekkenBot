from dis import dis
from xml.dom.minidom import CharacterData
from TekkenGameState import TekkenGameState
from BasicCommands import BotCommands
from CharacterData import *

import random

class BotBehaviors:

    # NOTE: Bot have trouble defending against attacks like Akuma's "hyaki zangeki".
    # Likely due to the fact that the initial jump is counted as a mid/high attack.
    # Causing the bot to continue defending mid/high when a low is executed after.

    def Basic(gameState, botCommands):
        if BotBehaviors.TryBreakThrows(gameState, botCommands):
            return
        BotBehaviors.StopPressingButtonsAfterGettingHit(gameState, botCommands)
        BotBehaviors.GetUp(gameState, botCommands)
        BotBehaviors.TechCombos(gameState, botCommands)

    def StopPressingButtonsAfterGettingHit(gameState, botCommands):
        if gameState.IsBotStartedGettingHit():
            botCommands.ClearCommands()
        if gameState.IsBotStartedBeingThrown():
            botCommands.ClearCommands()

    def TechThrows(gameState, botCommands):
        if gameState.IsBotBeingThrown():
            botCommands.MashTech()

    def GetUp(gameState, botCommands):
        if gameState.IsBotOnGround():
            botCommands.GetUp()

    def TechCombos(gameState, botCommands):
        if gameState.IsBotBeingJuggled():
            botCommands.MashTech()

    def DefendAllAttacks(gameState: TekkenGameState, botCommands:BotCommands):
        if gameState.IsOppAttacking():
            frames = gameState.GetOppTimeUntilImpact()
            if gameState.IsOppAttackLow():
                botCommands.BlockLowFull(max(0, frames))
            else:
                botCommands.BlockMidFull(max(0, frames))

    def TryBreakThrows(gameState: TekkenGameState, botCommands:BotCommands) -> bool:
        """
        Spam break throws when opponent is attempting to throw.

        Output
        -----------------
        True if the bot is attempting break throws
        """
        if BotBehaviors.OppIsThrowing(gameState):
            print("Breaking Throws")
            botCommands.MashTech()
            return True
        return False

    def OppIsThrowing(gameState: TekkenGameState):
        if gameState.IsOppAttackThrow():
            return True
        elif gameState.IsBotStartedBeingThrown():
            return True
        elif gameState.IsBotBeingThrown():
            return True
        return False


    def DefendAndCounter(gameState: TekkenGameState, botCommands:BotCommands, gameplan: Gameplan) -> bool:
        """
        Counter (with another attack) whenever possible, blocks otherwise.

        Output
        -----------------
        If True, the bot is doing blocks/Dodges/nothing.
        If False, the bot is countering.
        """

        if gameState.IsBotAttackStarting():
            return False

        if gameState.IsOppAttacking():
            # TODO: Poke on whiff
            oppAirborne = gameState.IsOppAirborne()
            frames = gameState.GetOppTimeUntilImpact()
            dist = gameState.GetDist()

            # Higher the number, the higher the chance AI chooses
            # trying to counter
            COUNTER_CHANCE = 90

            # Dont counter if distance is too big (2.0)
            if dist < 2000.0 and COUNTER_CHANCE >= random.randint(0, 100):
                counter = BotBehaviors.CanCounter(frames - 2, gameState, oppAirborne)
            else:
                counter = False

            oppLowAtk = gameState.IsOppAttackLow()
            oppMidAtk = gameState.IsOppAttackMid()
            oppHighAtk = not oppLowAtk and not oppMidAtk

            if counter:
                counterCommand = None
                if oppAirborne:
                    counterCommand = gameplan.GetMoveByFrame(ResponseTypes.air_counters, frames - 1)
                    print("Get Counter for air :: " + str(counterCommand))
                elif oppLowAtk:
                    counterCommand = gameplan.GetMoveByFrame(ResponseTypes.low_counters, frames - 1)
                    print("Get Counter for low :: " + str(counterCommand))
                elif oppMidAtk:
                    counterCommand = gameplan.GetMoveByFrame(ResponseTypes.mid_counters, frames - 1)
                    print("Get Counter for Mid :: " + str(counterCommand))
                else:
                    counterCommand = gameplan.GetMoveByFrame(ResponseTypes.high_counters, frames - 1)
                    print("Get Counter for High :: " + str(counterCommand))

                if not counterCommand == None:
                    botCommands.AddCommand(counterCommand)
                    return False

            # Out of 100, higher the number, higher the chance AI chooses to dodge
            DODGE_CHANCE = 40
            dodgeChance = random.randint(1, 100)

            if DODGE_CHANCE > dodgeChance and oppHighAtk:
                print("Dodging High")
                botCommands.BlockLowFull(max(0, frames))
                return True
            elif oppLowAtk:
                print("Blocking Low")
                botCommands.BlockLowFull(max(0, frames))
                return True
            else:
                print("Blocking HighMid")
                botCommands.BlockMidFull(max(0, frames))
                return True
        return True

    def UnblockIncomingAttacks(self, gameState: TekkenGameState):
        if gameState.IsOppAttacking():
            self.botCommands.WalkForward(max(0, gameState.GetOppTimeUntilImpact()))

    def CanCounter(frames: int, gameState: TekkenGameState, airborneOpp: bool):
        # Dont counter crushes
        if gameState.IsOppPowerCrush():
            return False
        # Dont counter if we are currently blocking
        elif gameState.IsBotBlocking():
            return False
            
        # Counter if the attack is more than 10 frames
        elif frames > 10:
            return True
        # Counter if the opponent is airborn, and the attack is more than 5 frames.
        elif airborneOpp and frames > 5:
            return True
        else:
            return False