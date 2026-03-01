# semantic/semantic_extractor.py

import re

IMPORTANT_KEYWORDS = {
    "locations": ["chennai", "bangalore", "bengaluru", "delhi", "mumbai"],
    "actions": ["living", "studied", "working", "travelling"],
}

def extract_semantics(text: str):
    text = text.lower()

    entities = {
        "names": [],
        "locations": [],
        "numbers": [],
        "actions": []
    }

    # Names (simple heuristic: first word if alphabetic)
    words = re.findall(r"[a-z]+", text)
    if words:
        entities["names"].append(words[0])

    # Locations
    for loc in IMPORTANT_KEYWORDS["locations"]:
        if loc in text:
            entities["locations"].append(loc)

    # Actions
    for act in IMPORTANT_KEYWORDS["actions"]:
        if act in text:
            entities["actions"].append(act)

    # Numbers
    entities["numbers"] = re.findall(r"\d+", text)

    return entities


def semantic_summary(entities: dict):
    lines = ["⚠️ High Noise Detected – Semantic Summary"]

    if entities["names"]:
        lines.append(f"• Person: {', '.join(set(entities['names']))}")

    if entities["locations"]:
        lines.append(f"• Locations: {', '.join(set(entities['locations']))}")

    if entities["actions"]:
        lines.append(f"• Actions: {', '.join(set(entities['actions']))}")

    if entities["numbers"]:
        lines.append(f"• Numbers: {', '.join(set(entities['numbers']))}")

    if len(lines) == 1:
        lines.append("• No reliable semantic information detected")

    return "\n".join(lines)