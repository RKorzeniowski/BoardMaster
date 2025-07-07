from crewai import Crew
from tasks import return_context_summarization_task

SUMMARIZE_AFTER_N = 7

class ConversationContext:
    def __init__(self):
        self.history = []
        self.last_player = None
        self.last_agent = None
        self.pending_question = None
        self.turn_count = 0

    def add_turn(self, speaker, message):
        self.turn_count += 1
        self.history.append({"speaker": speaker, "message": message})
        if speaker == "player":
            self.last_player = message
        else:
            self.last_agent = message

    def add_validator_tip(self, tip):
        self.history.append({"speaker": "validator", "message": tip})

    def remove_last_agent_turn(self):
        self.history = [h for h in self.history if not (h['speaker'] == 'agent' and h['message'] == self.last_agent)]
        self.last_agent = None

    def summarize_context(self, summarizer_agent):
        if self.turn_count > SUMMARIZE_AFTER_N:
            # Construct a summarization request to the summarizer agent
            conversation_text = "\n".join(f"{entry['speaker']}: {entry['message']}" for entry in self.history)
            task = return_context_summarization_task(summarizer_agent, conversation_text)
            crew = Crew(agents=[summarizer_agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            self.history = [{"speaker": "summary", "message": result.raw}]
            self.turn_count = 1  # Reset count to allow more turns before next summarization

    def set_pending_question(self, question):
        self.pending_question = question

    def get_last_player_input(self):
        return self.last_player

    def get_last_agent_output(self):
        return self.last_agent

    def get_pending_question(self):
        return self.pending_question

    def clear_pending_question(self):
        self.pending_question = None

    def get_full_history(self):
        return self.history

    def summary(self):
        return "\n".join(f"{entry['speaker']}: {entry['message']}" for entry in self.history)
