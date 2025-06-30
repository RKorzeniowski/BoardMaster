class ConversationContext:
    def __init__(self):
        self.history = []
        self.last_player = None
        self.last_agent = None
        self.pending_question = None

    def add_turn(self, speaker, message):
        self.history.append({"speaker": speaker, "message": message})
        if speaker == "player":
            self.last_player = message
        else:
            self.last_agent = message

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
