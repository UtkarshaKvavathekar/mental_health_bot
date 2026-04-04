from typing import Dict
from emotion_classifier import EmotionClassifier

classifier=EmotionClassifier()

def emotion_node(state:Dict)->Dict:
    user_input=state["input"]

    result=classifier.predict(user_input)
    emotion=result["label"]

    state["emotion"]=emotion

    return state
if __name__ == "__main__":
    test_state = {"input": "I feel very sad today"}
    print(emotion_node(test_state))