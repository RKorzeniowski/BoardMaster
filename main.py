from board_game_helper.agents import GameAgents
from board_game_helper.conversation_tracker import ConversationContext

from crewai import Crew, Task
from textwrap import dedent
from dotenv import load_dotenv

load_dotenv()

class GameCrew:
    def __init__(self, mode='game'):
        self.mode = mode
        self.context = ConversationContext()
        self.agents = GameAgents()

        # Create core agents
        self.listener = self.agents.listener()
        self.rules_expert = self.agents.rules_expert()
        self.state_tracker = self.agents.game_state_manager()
        self.status_tracker = self.agents.player_status_tracker()
        self.validator = self.agents.validator()
        self.explainer = self.agents.explainer()
        self.game_master = self.agents.game_master()

        if mode == 'tutorial':
            self.mode_agent = self.agents.first_time_helper()
        else:
            self.mode_agent = self.game_master

    def run(self):
        print("\n🎲 Welcome to the Board Game Helper (Monopoly Edition)!")
        print("Type 'exit' to end the session.\n")

        while True:
            player_input = input("You: ")
            if player_input.lower() == 'exit':
                print("\n👋 Thanks for playing! See you next time.")
                break

            self.context.add_turn("player", player_input)

            parsed_action = self.listener.run(
                input=player_input
            )
            self.context.add_turn("listener", parsed_action)

            # Delegate to appropriate agent based on context
            if 'rule' in parsed_action.lower():
                rule_response = self.rules_expert.run(input=parsed_action)
                self.context.add_turn("rules_expert", rule_response)

                explanation = self.explainer.run(input=rule_response)
                self.context.add_turn("explainer", explanation)
                print(f"🧠 Explainer: {explanation}")
                continue

            if self.context.get_pending_question():
                answer = parsed_action
                self.context.add_turn("followup_response", answer)
                self.context.clear_pending_question()

            # Game master runs main logic
            gm_response = self.mode_agent.run(input=parsed_action)
            self.context.add_turn("game_master", gm_response)

            # Validate
            valid = self.validator.run(input=gm_response)
            self.context.add_turn("validator", valid)

            if "error" in valid.lower():
                print("🚫 Move invalid. Asking for clarification...")
                self.context.set_pending_question("Can you clarify or rephrase that?")
                print("🤖 Game Master: Can you clarify or rephrase that?")
            else:
                # Update game state and player status if needed
                self.state_tracker.run(input=gm_response)
                self.status_tracker.run(input=gm_response)
                print(f"🤖 Game Master: {gm_response}")

if __name__ == "__main__":
    mode = input("Choose mode (tutorial/game): ").strip().lower()
    if mode not in ['tutorial', 'game']:
        mode = 'game'
    game_crew = GameCrew(mode=mode)
    game_crew.run()
