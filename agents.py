from crewai import Agent
from langchain.llms import OpenAI

class GameAgents:

    def rules_expert(self):
        return Agent(
            role="Rules Expert",
            goal="Answer game rule queries and provide game setup information",
            backstory="Knows the rulebook of Monopoly by heart. Provides game setup instructions and rule clarifications.",
            verbose=True,
        )

    def player_status_tracker(self):
        return Agent(
            role="Player Status Tracker",
            goal="Track and recall player data, including positions, money, and assets",
            backstory="Maintains accurate player metadata and updates after each turn.",
            verbose=True,
        )

    def game_state_manager(self):
        return Agent(
            role="Game State Manager",
            goal="Track the overall state of the Monopoly game, including turn order and board state",
            backstory="Keeps track of where pieces are on the board and manages phase transitions.",
            verbose=True,
        )

    def validator(self):
        return Agent(
            role="Game Move Validator",
            goal="Ensure actions and responses align with game rules and state",
            backstory="Verifies consistency between inputs, game state, and rules. Handles error recovery.",
            verbose=True,
        )

    def listener(self):
        return Agent(
            role="Listener and Parser",
            goal="Convert player speech into structured game actions or questions",
            backstory="Listens to players' speech and translates it into actionable input for agents.",
            verbose=True,
        )

    def explainer(self):
        return Agent(
            role="Game Explainer",
            goal="Translate game rule answers into digestible, easy instructions",
            backstory="Explains game concepts to players clearly, with educational intent but minimal overload.",
            verbose=True,
        )

    def first_time_helper(self):
        return Agent(
            role="First-Time Player Helper",
            goal="Guide players through a dummy game of Monopoly to teach game flow and rules",
            backstory="Acts like a practice round coach for new players learning Monopoly.",
            verbose=True,
        )

    def game_master(self):
        return Agent(
            role="Game Master",
            goal="Conduct the Monopoly game, prompting players and resolving actions",
            backstory="Coordinates the game, keeping play flowing and delegating clarifications to other agents.",
            verbose=True,
        )
