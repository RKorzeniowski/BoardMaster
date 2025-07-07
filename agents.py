import os

from crewai import Agent
from langchain.chat_models import ChatOpenAI
from tools.wiki_search import WikiSearchTool


api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model='gpt-4.1-nano', openai_api_key=api_key)

class GameAgents:

    def summarizer_agent(self):
        return Agent(
            role="Conversation Summarizer",
            goal="Condense the last few turns of the Monopoly game into a short, fact-rich summary that maintains all key game state details.",
            backstory=(
                "This agent specializes in memory compression. It observes the last turns of player and system interaction "
                "and rewrites them into a minimal summary. Its output helps keep context concise without losing any information "
                "critical to game logic, rule enforcement, player status, or board position tracking."
            ),
            verbose=True,
            llm=llm,
            allow_delegation=False
        )

    def game_state_manager(self):
        return Agent(
            role="Game State Manager",
            goal="Track the overall state of the Monopoly game, all the player data, including positions, money assets as well as turn order, and board state",
            backstory="Maintains accurate player metadata and updates after each turn. "
                      "Keeps track of where pieces are on the board and manages phase transitions."
                      "If asked provides current status of the game. Explicitly states full name of current position of each of the players on the board and all the other "
                      "relevant medata about the players.",
            verbose=True,
            allow_delegation=False,
            llm=llm,
        )

    def validator(self):
        return Agent(
            role="Game Move Validator",
            goal="Ensure actions and responses align with game rules and state",
            backstory="Verifies consistency between inputs, game state, and rules. Handles error recovery.",
            verbose=True,
            tools=[WikiSearchTool()],
            allow_delegation=False,
            llm=llm,
        )

    def game_master(self):
        return Agent(
            role="Game Master",
            goal="Conduct the Monopoly game, prompting players and resolving actions",
            backstory="Coordinates the game, keeping play flowing and delegating clarifications to other agents. "
                      "If unsure about the game state or player metadata asks game_state_manager agent to provide current status. ",
            verbose=True,
            allow_delegation=True,
            llm=llm,
        )
