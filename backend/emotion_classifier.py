# from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
# import torch
# import os


# class EmotionClassifier:
#     def __init__(self):
#         BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#         MODEL_PATH = os.path.join(BASE_DIR, "models", "trained_distilbert")

#         self.tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
#         self.model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
#         self.model.eval()

#     def predict(self, text: str):
#         inputs = self.tokenizer(
#             text,
#             return_tensors="pt",
#             truncation=True,
#             padding=True,
#             max_length=128 
#         )

#         with torch.no_grad():
#             outputs = self.model(**inputs)

#         logits = outputs.logits
#         predicted_class_id = torch.argmax(logits, dim=1).item()
#         confidence = torch.softmax(logits, dim=1).max().item()
#         predicted_label=self.model.config.id2label[predicted_class_id]
#         return {
#             "label": predicted_label,
#             "confidence": confidence,
#             "logits": logits.tolist()
#         }




from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch


class EmotionClassifier:
    def __init__(self):
        MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

        self.tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)
        self.model = DistilBertForSequenceClassification.from_pretrained(MODEL_NAME)
        self.model.eval()

    def predict(self, text: str):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=1).item()
        confidence = torch.softmax(logits, dim=1).max().item()

        predicted_label = self.model.config.id2label[predicted_class_id]

        return {
            "label": predicted_label,
            "confidence": confidence,
            "logits": logits.tolist()
        }

