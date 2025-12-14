from transformers import pipeline
import pandas as pd
from tqdm import tqdm

classifier = pipeline(
    "zero-shot-classification",
    model="joeddav/xlm-roberta-large-xnli"
)

labels = [
    "직원 태도 및 친절도",
    "진료 및 설명",
    "대기 시간",
    "시설 및 환경",
    "가격 및 비용",
    "효과 및 결과",
    "기타 긍정",
    "기타 부정"
]

df = pd.read_csv("clean_data.csv")
results = []

for sent in tqdm(df["sentence"], desc="Zero-shot labeling"):
    result = classifier(sent, labels)
    pred_label = result["labels"][0]
    score = float(result["scores"][0])

    results.append([sent, pred_label, score])

df["zero_shot_label"] = [r[1] for r in results]
df["zero_shot_confidence"] = [r[2] for r in results]

df.to_csv("zero_shot_labeled.csv", index=False, encoding="utf-8-sig")

print("✔ Zero-shot 라벨링 완료 → zero_shot_labeled.csv")
