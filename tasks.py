from crewai import Task
from textwrap import dedent

class GameTasks:

    def parse_player_input(self, agent, player_message, context=""):
        return Task(
            description=dedent(f"""
                Interpret the following user message in the context of an ongoing Monopoly game.
                Consider the previous conversation:
                {context}

                Extract the player's intent (e.g., move, ask rule, buy property).

                Message: "{player_message}"
            """),
            agent=agent,
            expected_output="Structured game-related command or question from user input."
        )

    def check_rules(self, agent, query):
        return Task(
            description=dedent(f"""
                Provide a clear and complete answer to the following rule question,
                referencing the Monopoly rulebook.

                Question: "{query}"
            """),
            agent=agent,
            expected_output="Authoritative answer based on official Monopoly rules."
        )

    def track_player_state(self, agent, player_name, updates):
        return Task(
            description=dedent(f"""
                Update player "{player_name}"'s status with the following updates:
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

                Rule response: "{rule_response}"
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

                Check for correctness and legality. If invalid, directly state 'invalid' or 'not allowed'. Never use those two phrases when input is valid. 
                In case of invalid input state why it is invalid in a way that would be helpful for an LLM agent to avoid making the same mistake again and 
                generate correct output.
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

    def run_game(self, agent, player_names, player_piece):
        return Task(
            description=dedent(f"""
                Assume role of Game Master. Start the Monopoly game, set up the board,
                assign player positions, and explain the first steps.

                Prepare the game to begin.
                
                Players say that their names are: {player_names}
                Players say about pieces they picked out of Dog, House and Shoe: {player_piece}.
            """),
            agent=agent,
            expected_output="Initial game state based on players input, setup details" # , and player's first turn.
        )

    def continue_game(self, agent, player_message, context):
        return Task(
            description=dedent(f"""
                Continue the Monopoly game. Consider this new player input:
                "{player_message}"

                And the current context:
                {context}

                Respond as the Game Master, advancing the game state, validating moves,
                and addressing rule questions if necessary.
            """),
            agent=agent,
            expected_output="Updated game progress, next steps, and player guidance."
        )
