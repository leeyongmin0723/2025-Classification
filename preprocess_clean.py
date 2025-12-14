import re
import pandas as pd

def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = re.sub(r"<.*?>", "", text)        # HTML 태그 제거
    text = re.sub(r"[^\w\s가-힣.,!?]", "", text)  # 이모지/특수문자 제거
    text = re.sub(r"http\S+", "", text)      # URL 제거
    text = re.sub(r"\s+", " ", text).strip() # 다중 공백 제거
    return text


def split_sentences(text):
    """간단한 문장 분리."""
    sentences = re.split(r"[.!?]", text)
    return [s.strip() for s in sentences if len(s.strip()) > 0]


df = pd.read_json("reviews_combined.json")   # 여러 병원의 리뷰 합친 파일

clean_rows = []

for _, row in df.iterrows():
    cleaned = clean_text(row["content"])
    sents = split_sentences(cleaned)

    for idx, s in enumerate(sents):
        if len(s) >= 3:   # 짧은 문장 제거 규칙
            clean_rows.append({
                "place_id": row["place_id"],
                "review_id": row["review_id"],
                "sentence_index": idx,
                "sentence": s
            })

clean_df = pd.DataFrame(clean_rows)
clean_df.to_csv("clean_data.csv", index=False, encoding="utf-8-sig")

print(f"✔ 정제 완료 → clean_data.csv (총 {len(clean_df)} 문장)")
