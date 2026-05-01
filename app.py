import streamlit as st
import pdfplumber
import re
import io

st.set_page_config(page_title="療養計画書 自動生成アシスタント", page_icon="🏥", layout="wide")

st.title("🏥 療養計画書 自動生成アシスタント")
st.markdown("---")

# 目標値の定義
GOALS = {
    "HbA1c": {"max": 7.0, "unit": "%", "label": "HbA1c"},
    "LDL": {"max": 120, "unit": "mg/dL", "label": "LDL-C"},
    "HDL": {"min": 40, "unit": "mg/dL", "label": "HDL-C"},
    "TG": {"max": 150, "unit": "mg/dL", "label": "中性脂肪"},
}

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def parse_value(text, keywords):
    for keyword in keywords:
        pattern = rf"{keyword}[\s:：]*([0-9]+\.?[0-9]*)"
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
    return None

def judge(label, value, goal):
    if value is None:
        return None, "データなし"
    if "max" in goal:
        achieved = value <= goal["max"]
        target = f"{goal['max']}{goal['unit']}以下"
    else:
        achieved = value >= goal["min"]
        target = f"{goal['min']}{goal['unit']}以上"
    status = "✅ 達成" if achieved else "❌ 未達成"
    return achieved, f"{label}：{value}{goal['unit']}（目標{target}）→ {status}"

def judge_bp(systolic, diastolic):
    if systolic is None or diastolic is None:
        return None, "血圧：データなし"
    achieved = systolic < 130 and diastolic < 80
    status = "✅ 達成" if achieved else "❌ 未達成"
    return achieved, f"血圧：{systolic}/{diastolic}mmHg（目標130/80未満）→ {status}"

# レイアウト
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📄 検査結果PDFのアップロード")
    uploaded_file = st.file_uploader("PDFファイルを選択してください", type=["pdf"])

    st.subheader("🩺 血圧の入力")
    systolic = st.number_input("収縮期血圧（上）mmHg", min_value=0, max_value=300, value=0)
    diastolic = st.number_input("拡張期血圧（下）mmHg", min_value=0, max_value=200, value=0)

    analyze_btn = st.button("🔍 解析する", use_container_width=True)

with col2:
    st.subheader("📊 解析結果")

    if analyze_btn:
        results = []
      
