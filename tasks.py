from crewai import Task
from textwrap import dedent

class GameTasks:

    def track_game_state(self, agent, player_input, action_context, agent_action):
        return Task(
            description=dedent(f"""
                Based on current action context, player input and game master agent action infer accurate player metadata and board state.
                
                Player input: {player_input}
                Action context: {action_context}
                Game Master agent action: {agent_action}
            
                Return the updated summary of players and game state.
            """),
            agent=agent,
            expected_output="Updated player profile with assets, money, position, etc. "
                            "Explicitly state full name of current position of each of the players on the board."
        )

    def validate_action(self, agent, player_input, action_context, agent_action):
        return Task(
            description=dedent(f"""
                Validate the following game action taken by Agent leading the game of Monopoly taking into account
                player input, current state of the game and adherence to general rules of board game Monopoly.
                
                Player input: {player_input}
                Action context: {action_context}
                Agent action: {agent_action}

                Check for correctness and legality. If invalid, directly state 'invalid' or 'not allowed'. Never use those two phrases when input is valid. 
                In case of invalid input state why it is invalid in a way that would be helpful for an LLM agent to avoid making the same mistake again and 
                generate correct output.
            """),
            agent=agent,
            expected_output="Validation result and potential correction path if invalid."
        )

    def run_game(self, agent, player_names, player_piece):
        return Task(
            description=dedent(f"""
                Assume role of Game Master. Start the Monopoly game, set up the board,
                assign player positions, and explain the first steps needed to start a game.

                Prepare the game to begin.
                
                Players say that their names are: {player_names}
                Players say about pieces they picked out of Dog, House and Shoe: {player_piece}.
                
                Do not make any moves for the players.
            """),
            agent=agent,
            expected_output="Initial game state based on players input, setup details. Do not make any moves for the players."
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

def return_context_summarization_task(agent, conversation_text):
    return Task(
        description=f"Summarize the following Monopoly game conversation for game state tracking:\n\n{conversation_text}\n\nBe concise but retain all important facts and instructions.",
        agent=agent,
        expected_output="Summary of the important context so far. Explicitly state full name of current position of each of the players on the board."
    )
