from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch


import os



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "models", "trained_distilbert")
# Load tokenizer
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)

# Load model
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)

# Put model in evaluation mode
model.eval()

def predict_emotion(text: str):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()
    predicted_label=model.config.id2label[predicted_class]

    return predicted_label, logits.tolist()


# Quick test
if __name__ == "__main__":
    text = "I feel very happy and joyful today"
    label, raw_logits = predict_emotion(text)

    print("Input:", text)
    print("Predicted emotion:", label)
    print("Logits:", raw_logits)

print("Model path:", MODEL_PATH)
print("Exists:", os.path.exists(MODEL_PATH))
