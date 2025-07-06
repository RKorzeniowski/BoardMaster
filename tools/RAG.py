import json
from langchain.tools import tool

class MonopolyKnowledgeTool:

    def __init__(self):
        with open('tools/monopoly_data.json', 'r') as f:
            self.data = json.load(f)

    @tool("Lookup Monopoly Info")
    def lookup(query):
        """
        Search Monopoly board, chance/community cards, and basic rules.
        Input should be a string describing the topic.
        """
        result = []
        query_lower = query.lower()

        for item in MonopolyKnowledgeTool().data.get("spaces", []):
            if query_lower in item["name"].lower():
                result.append(f"Board Space: {item['name']} - {item.get('type', 'unknown')}")

        for card in MonopolyKnowledgeTool().data.get("chance_cards", []) + MonopolyKnowledgeTool().data.get("community_chest_cards", []):
            if query_lower in card.lower():
                result.append(f"Card: {card}")

        for rule in MonopolyKnowledgeTool().data.get("rules", []):
            if query_lower in rule.lower():
                result.append(f"Rule: {rule}")

        return result if result else "No Monopoly info found for query."
