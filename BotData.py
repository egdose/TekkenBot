from xml.dom.minidom import CharacterData
from TekkenGameState import TekkenGameState
from BasicCommands import BotCommands
from CharacterData import *

class BotBehaviors:

    def Basic(gameState, botCommands):
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

        if gameState.IsOppAttacking():
            oppAirborne = gameState.IsOppAirborne()
            frames = gameState.GetOppTimeUntilImpact() + 1
            counter = BotBehaviors.CanCounter(frames, gameState, oppAirborne)

            if counter:
                counterCommand = None
                if oppAirborne:
                    counterCommand = gameplan.GetMoveByFrame(ResponseTypes.low_counters, frames)
                elif gameState.IsOppAttackMid:
                    counterCommand = gameplan.GetMoveByFrame(ResponseTypes.mid_counters, frames)
                else:
                    counterCommand = gameplan.GetMoveByFrame(ResponseTypes.high_counters, frames)

                if not counterCommand == None:
                    print("Countering")
                    botCommands.AddCommand(counterCommand)
                    return False

            if gameState.IsOppAttackLow():
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
        # or already attacking
        elif gameState.IsBotAttackStarting():
            return False
            
        # Counter if the attack is more than 10 frames
        elif frames > 10:
            return True
        # Counter if the opponent is airborn, and the attack is more than 5 frames.
        elif airborneOpp and frames > 5:
            return True
        else:
            return False