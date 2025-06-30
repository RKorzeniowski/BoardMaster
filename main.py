from crewai import Crew
from board_game_helper.agents import GameAgents
from board_game_helper.tasks import GameTasks

from dotenv import load_dotenv
load_dotenv()

class GameCrew:

    def __init__(self, game_mode='tutorial', player_input=None):
        self.game_mode = game_mode
        self.player_input = player_input or ""

    def run(self):
        agents = GameAgents()
        tasks = GameTasks()

        # Instantiate agents
        rules_agent = agents.rules_expert()
        player_tracker = agents.player_status_tracker()
        state_manager = agents.game_state_manager()
        validator = agents.validator()
        listener = agents.listener()
        explainer = agents.explainer()
        tutorial_guide = agents.first_time_helper()
        master = agents.game_master()

        if self.game_mode == 'tutorial':
            task = tasks.run_tutorial(tutorial_guide)
            crew = Crew(
                agents=[tutorial_guide, rules_agent, explainer],
                tasks=[task],
                verbose=True
            )

        elif self.game_mode == 'game':
            task = tasks.run_game(master)
            crew = Crew(
                agents=[master, rules_agent, player_tracker, state_manager, explainer],
                tasks=[task],
                verbose=True
            )

        elif self.game_mode == 'rule_question':
            parse_task = tasks.parse_player_input(listener, self.player_input)
            rule_task = tasks.check_rules(rules_agent, self.player_input)
            explain_task = tasks.explain_rules(explainer, "<placeholder for rule_task result>")

            crew = Crew(
                agents=[listener, rules_agent, explainer],
                tasks=[parse_task, rule_task, explain_task],
                verbose=True
            )

        else:
            raise ValueError("Unknown game mode. Choose 'tutorial', 'game', or 'rule_question'.")

        result = crew.kickoff()
        return result


if __name__ == "__main__":
    print("## Welcome to Board Game Helper for MONOPOLY")
    print("-------------------------------------------")
    mode = input("Choose mode ('tutorial', 'game', 'rule_question'): ").strip()

    if mode == 'rule_question':
        user_query = input("What rule would you like help with? ")
        crew = GameCrew(game_mode=mode, player_input=user_query)
    else:
        crew = GameCrew(game_mode=mode)

    result = crew.run()

    print("\n\n########################")
    print("## Session Result")
    print("########################\n")
    print(result)
