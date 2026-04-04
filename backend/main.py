from emotion_classifier import EmotionClassifier
from rag import retrieve_context

text = "I dont know whts wrong with me"

classifier = EmotionClassifier()
emotion = classifier.predict(text)
context =retrieve_context(text)

print("Emotion:", emotion)
print("\n--- CONTEXT ---\n")
print(context)