from dotenv import load_dotenv
load_dotenv()

import speech_recognition as sr
import pyttsx3
from crewai import Crew
from agents import GameAgents
from tasks import GameTasks
from conversation_tracker import ConversationContext

SKIP_INITIAL_RULES_SPEECH = False

class GameCrew:

    def __init__(self, game_mode='tutorial'):
        self.game_mode = game_mode
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

    def run(self):
        agents = GameAgents()
        tasks = GameTasks()

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
            result = crew.kickoff()
            self.speak(result)

        elif self.game_mode == 'rule_question':
            self.speak("What rule would you like help with?")
            user_query = self.listen()
            self.context.add_turn("player", user_query)

            parse_task = tasks.parse_player_input(listener, user_query)
            rule_task = tasks.check_rules(rules_agent, user_query)
            explain_task = tasks.explain_rules(explainer, f"<rule info from rule_task>")

            crew = Crew(
                agents=[listener, rules_agent, explainer],
                tasks=[parse_task, rule_task, explain_task],
                verbose=True
            )
            result = crew.kickoff()
            self.speak(result)

        elif self.game_mode == 'game':
            self._interactive_game_session(master, rules_agent, player_tracker, state_manager, explainer, validator, tasks)

    def _interactive_game_session(self, master, rules_agent, player_tracker, state_manager, explainer, validator, tasks):
        print("Starting game session. Type 'exit' to end.")
        self.speak("What are you names players?")
        player_names = self.listen()
        self.speak("What pieces do each of you pick out of Dog, House and Shoe?")
        player_piece = self.listen()
        self.context.add_turn("player", f"Players say that their names are {player_names} and that regarding pieces {player_piece}")
    
        while True:
            if not self.game_started:
                game_task = tasks.run_game(master, player_names, player_piece)
                crew = Crew(
                    agents=[master, rules_agent, player_tracker, state_manager, explainer],
                    tasks=[game_task],
                    verbose=True
                )
                result = crew.kickoff()
                self.game_started = True
    
                if SKIP_INITIAL_RULES_SPEECH:
                    print("\nGame Master:", result)
                else:
                    self.speak(result.raw.replace("\n", " "))
            else:
                print("Waiting for playing input")
                player_input = self.listen()
                print(f"Player turn input {player_input}")
                if player_input.lower() == 'exit':
                    break
    
                self.context.add_turn("player", player_input)
    
                continue_task = tasks.continue_game(master, player_input, self.context.summary())
                validate_task = tasks.validate_action(validator, f"{player_input}\n\nCurrent game context:\n{self.context.summary()}")
    
                crew = Crew(
                    agents=[master, rules_agent, player_tracker, state_manager, explainer, validator],
                    tasks=[continue_task, validate_task],
                    verbose=True
                )
                result = crew.kickoff()
    
                validation_feedback = str(result[1].raw).lower()
    
                if "invalid" in validation_feedback or "not allowed" in validation_feedback:
                    # Regenerate response using validator feedback as context
                    correction_context = f"The previous output was invalid: {validation_feedback}. Consider this when continuing."
                    self.context.add_turn("agent", f"Invalid output: {validation_feedback}")
                    retry_task = tasks.continue_game(master, player_input, self.context.summary() + "\n" + correction_context)
    
                    retry_crew = Crew(
                        agents=[master, rules_agent, player_tracker, state_manager, explainer],
                        tasks=[retry_task],
                        verbose=True
                    )
                    result = retry_crew.kickoff()
    
                self.context.add_turn("agent", result)
                print("starting to generate LLM speech")
                self.speak(result.raw.replace("\n", " "))
                print("done to generate LLM speech")


if __name__ == "__main__":
    engine = pyttsx3.init()
    engine.say("Welcome to the Board Master. Today we will play Monopoly. Please pick tutorial, game, or rule question mode.")
    engine.runAndWait()

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for mode selection...")
        audio = recognizer.listen(source)

    try:
        mode_input = recognizer.recognize_google(audio).lower()
        print(f"Heard mode_input: {mode_input} is invalid option. It has to be either tutorial, game, or rule question")
    except sr.UnknownValueError:
        mode_input = "game"
        engine.say("Sorry, I didn't catch that. Starting game mode.")
        engine.runAndWait()

    valid_mode = any([mode_input == mode for mode in ['tutorial', 'game', 'rule question']])

    if not valid_mode:
        mode_input = "game"
        engine.say(f"Sorry, you said {mode_input} but only options available are tutorial, game, or rule question. "
                   f"Falling back to the game mode.")
        engine.runAndWait()

    helper = GameCrew(game_mode=mode_input)
    helper.run()
