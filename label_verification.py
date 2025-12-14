import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
from tqdm import tqdm

model_name = "monologg/koelectra-base-v3-discriminator"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained("trained_model")

df = pd.read_csv("zero_shot_labeled.csv")

def predict(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    conf, label_id = torch.max(probs, dim=1)
    return int(label_id), float(conf)


suspects = []

for i, row in tqdm(df.iterrows(), total=len(df), desc="Label verifying"):
    pred_label, pred_conf = predict(row["sentence"])

    # 의심 기준
    cond1 = (row["label_id"] != pred_label)
    cond2 = (pred_conf < 0.45)
    cond3 = (len(row["sentence"]) <= 6)

    if cond1 or cond2 or cond3:
        suspects.append(i)

df["is_suspect"] = False
df.loc[suspects, "is_suspect"] = True

df.to_csv("verified_labels.csv", index=False, encoding="utf-8-sig")
print(f"✔ 검증 완료 → suspected {len(suspects)}개")
