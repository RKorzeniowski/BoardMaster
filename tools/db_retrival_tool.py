import json
from crewai.tools import BaseTool

with open('tools/monopoly_data.json', 'r') as f:
    DATA = json.load(f)

class MonopolyKnowledgeTool(BaseTool):
    name: str = "Lookup Monopoly Info"
    description: str = "Search Monopoly board, chance/community cards, and basic rules. Input should be a string describing the topic."

    def _run(self, query: str) -> str:
        result = []
        query_lower = query.lower()

        for item in DATA.get("spaces", []):
            if query_lower in item["name"].lower():
                result.append(f"Board Space: {item['name']} - {item.get('type', 'unknown')}")

        for card in DATA.get("chance_cards", []) + DATA.get("community_chest_cards", []):
            if query_lower in card.lower():
                result.append(f"Card: {card}")

        for rule in DATA.get("rules", []):
            if query_lower in rule.lower():
                result.append(f"Rule: {rule}")

        return "\n".join(result) if result else "No Monopoly info found for query."
