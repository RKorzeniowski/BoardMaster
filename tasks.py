from crewai import Task
from textwrap import dedent

class GameTasks:

    def parse_player_input(self, agent, player_message):
        return Task(
            description=dedent(f"""
                Interpret this user message and extract the intent, including whether
                it's a question, game action, or confusion.

                Output should be structured, e.g.:
                {{
                    "intent": "move", 
                    "details": {{
                        "action": "roll", 
                        "current_position": 5
                    }}
                }}

                Message: \"{player_message}\"
            """),
            agent=agent,
            expected_output="Structured game-related command or question from user input."
        )

    def check_rules(self, agent, query):
        return Task(
            description=dedent(f"""
                Provide a clear and complete answer to the following rule question,
                referencing the Monopoly rulebook.

                Question: \"{query}\"
            """),
            agent=agent,
            expected_output="Authoritative answer based on official Monopoly rules."
        )

    def track_player_state(self, agent, player_name, updates):
        return Task(
            description=dedent(f"""
                Update player \"{player_name}\"'s status with the following updates:
                {updates}

                Return the updated summary of this player's state.
            """),
            agent=agent,
            expected_output="Updated player profile with assets, money, position, etc."
        )

    def explain_rules(self, agent, rule_response):
        return Task(
            description=dedent(f"""
                Convert this rule response into an easy-to-understand explanation.
                Be helpful but concise.

                Rule response: \"{rule_response}\"
            """),
            agent=agent,
            expected_output="User-friendly, digestible explanation for players."
        )

    def validate_action(self, agent, action_context):
        return Task(
            description=dedent(f"""
                Validate the following game action or message in the context of
                current game state and rules.

                Action context: {action_context}

                Check for correctness and legality. If invalid, say why.
            """),
            agent=agent,
            expected_output="Validation result and potential correction path if invalid."
        )

    def run_tutorial(self, agent):
        return Task(
            description=dedent("""
                Start a guided dummy game session of Monopoly, focusing on helping
                first-time players understand the basics: setup, turn structure,
                movement, and property buying.

                Explain each concept clearly and simulate turns interactively.
            """),
            agent=agent,
            expected_output="Guided interactive dummy game walkthrough."
        )

    def run_game(self, agent):
        return Task(
            description=dedent("""
                Assume role of Game Master. Start the game, guide players through each
                step, manage turns, trigger rule clarifications and player updates
                via relevant agents.

                Keep flow simple, support users when confused.
            """),
            agent=agent,
            expected_output="Live guided Monopoly game session"
        )
