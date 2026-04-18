from typing import Dict
from emotion_classifier import EmotionClassifier

classifier=EmotionClassifier()

def emotion_node(state):
    text = state["messages"][-1].content   # ✅ FIX

    result = classifier.predict(text)

    return {
        "emotion": result["label"]
    }