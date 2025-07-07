from dotenv import load_dotenv
load_dotenv()

import speech_recognition as sr
import pyttsx3
from crewai import Crew
from agents import GameAgents
from tasks import GameTasks
from conversation_tracker import ConversationContext

TEXT_MODE = True
DUMMY_INPUTS = True
SOLO_MODE = True

class GameCrew:

    def __init__(self):
        self.context = ConversationContext()
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.game_started = False

    def speak(self, text):
        print("AI:", text)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
        try:
            input_text = self.recognizer.recognize_google(audio)
            print("You:", input_text)
            return input_text
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand that. Please try again.")
            return self.listen()
        except sr.RequestError as e:
            self.speak("ASR service error. Please check your internet connection.")
            raise e

    def run_solo(self):
        """
        run monopoly game with only game master agent
        """
        agents = GameAgents()
        tasks = GameTasks()

        master = agents.game_master()

        self._interactive_solo_game_session(master, tasks)

    def _interactive_solo_game_session(self, master, tasks):
        print("Starting game session. Type 'exit' to end.")

        if TEXT_MODE:
            if DUMMY_INPUTS:
                player_names = "Tom and Anna"
            else:
                player_names = input("What are your names players?:\n")
        else:
            self.speak("What are your names players?")
            player_names = self.listen()

        if TEXT_MODE:
            if DUMMY_INPUTS:
                player_piece = "Tom picked the Dog piece and Anna picked the Shoe piece"
            else:
                player_piece = input("What pieces do each of you pick out of Dog, House and Shoe?:\n")
        else:
            self.speak("What pieces do each of you pick out of Dog, House and Shoe?")
            player_piece = self.listen()
        self.context.add_turn("player", f"Players say that their names are {player_names} and that regarding pieces {player_piece}")

        while True:
            if not self.game_started:
                game_task = tasks.run_game(master, player_names, player_piece)
                crew = Crew(
                    agents=[master],
                    tasks=[game_task],
                    verbose=True
                )
                result = crew.kickoff()
                self.game_started = True

                if TEXT_MODE:
                    print("\nGame Master:", result)
                else:
                    self.speak(result.raw.replace("\n", " "))
            else:
                if TEXT_MODE:
                    player_input = input("Waiting for playing input:\n")
                else:
                    print("Waiting for playing input:")
                    player_input = self.listen()

                print(f"Player turn input {player_input}")
                if player_input.lower() == 'exit':
                    break

                self.context.add_turn("player", player_input)

                continue_task = tasks.continue_game(master, player_input, self.context.summary())

                crew = Crew(
                    agents=[master],
                    tasks=[continue_task],
                    verbose=True
                )
                result = crew.kickoff()

                agent_text_output = result.raw.replace("\n", " ")
                self.context.add_turn("game_master_agent", agent_text_output)
                if TEXT_MODE:
                    print(agent_text_output)
                else:
                    self.speak(agent_text_output)

    def run(self):
        agents = GameAgents()
        tasks = GameTasks()

        validator = agents.validator()
        master = agents.game_master()
        summarizer = agents.summarizer_agent()
        game_state_tracker = agents.game_state_manager()

        self._interactive_game_session(master, game_state_tracker, validator, summarizer, tasks)

    def _interactive_game_session(self, master, game_state_tracker, validator, summarizer, tasks):
        print("Starting game session. Type 'exit' to end.")

        if TEXT_MODE:
            if DUMMY_INPUTS:
                player_names = "Tom and Anna"
            else:
                player_names = input("What are your names players?:\n")
        else:
            self.speak("What are your names players?")
            player_names = self.listen()

        if TEXT_MODE:
            if DUMMY_INPUTS:
                player_piece = "Tom picked the Dog piece and Anna picked the Shoe piece"
            else:
                player_piece = input("What pieces do each of you pick out of Dog, House and Shoe?:\n")
        else:
            self.speak("What pieces do each of you pick out of Dog, House and Shoe?")
            player_piece = self.listen()
        self.context.add_turn("player", f"Players say that their names are {player_names} and that regarding pieces {player_piece}")

        while True:
            if not self.game_started:
                game_task = tasks.run_game(master, player_names, player_piece)
                crew = Crew(
                    agents=[master],
                    tasks=[game_task],
                    verbose=True
                )
                result = crew.kickoff()
                self.game_started = True

                if TEXT_MODE:
                    print("\nGame Master:", result)
                else:
                    self.speak(result.raw.replace("\n", " "))
            else:
                if TEXT_MODE:
                    player_input = input("Waiting for playing input:\n")
                else:
                    print("Waiting for playing input:")
                    player_input = self.listen()

                print(f"Player turn input {player_input}")
                if player_input.lower() == 'exit':
                    break

                self.context.add_turn("player", player_input)

                continue_task = tasks.continue_game(master, player_input, self.context.summary())

                crew = Crew(
                    agents=[master, game_state_tracker],
                    tasks=[continue_task],
                    verbose=True
                )
                result = crew.kickoff()

                validate_task = tasks.validate_action(validator, player_input=player_input, action_context=self.context.summary(), agent_action=result.raw)

                crew = Crew(
                    agents=[validator, game_state_tracker],
                    tasks=[validate_task],
                    verbose=True
                )

                val_track_result = crew.kickoff()
                validation_feedback = str(val_track_result.raw).lower()

                if "invalid " in validation_feedback or "invalid." in validation_feedback or "not allowed " in validation_feedback:
                    # Regenerate response using validator feedback as context
                    correction_context = f"The previous output was invalid: {validation_feedback}. Consider this when continuing."
                    self.context.add_turn("validator", f"Invalid output: {validation_feedback}")
                    retry_task = tasks.continue_game(master, player_input, self.context.summary() + "\n" + correction_context)

                    retry_crew = Crew(
                        agents=[master, game_state_tracker],
                        tasks=[retry_task],
                        verbose=True
                    )
                    result = retry_crew.kickoff()

                agent_text_output = result.raw.replace("\n", " ")
                self.context.add_turn("game_master_agent", agent_text_output)
                if TEXT_MODE:
                    print(agent_text_output)
                else:
                    self.speak(agent_text_output)

                self.context.summarize_context(summarizer)

if __name__ == "__main__":
    if TEXT_MODE:
        print("Welcome to the Board Master. Today we will play Monopoly")

    else:
        engine = pyttsx3.init()
        engine.say("Welcome to the Board Master. Today we will play Monopoly.")
        engine.runAndWait()

    helper = GameCrew()

    if SOLO_MODE:
        helper.run_solo()
    else:
        helper.run()
