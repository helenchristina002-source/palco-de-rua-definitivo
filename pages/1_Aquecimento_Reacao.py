import streamlit as st
import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime

st.set_page_config(page_title="Aquecimento – Reação do Espectador", page_icon="🔥")
st.title("🔥 Aquecimento – Reação do Espectador")

st.write(
    "Depois de assistir ao trecho de teatro de rua, descreva **em 3 palavras** sua sensação. "
    "Ex.: *surpreso*, *tenso*, *divertido*."
)

nome = st.text_input("Seu nome (ou apelido)")
col1, col2, col3 = st.columns(3)
with col1:
    p1 = st.text_input("Palavra 1").strip()
with col2:
    p2 = st.text_input("Palavra 2").strip()
with col3:
    p3 = st.text_input("Palavra 3").strip()

csv = Path("data/reacoes.csv")
csv.parent.mkdir(exist_ok=True)
if not csv.exists():
    pd.DataFrame(columns=["quando","nome","p1","p2","p3"]).to_csv(csv, index=False)

if st.button("Enviar minhas 3 palavras ✨") and nome and p1 and p2 and p3:
    df = pd.read_csv(csv)
    df.loc[len(df)] = [datetime.now().isoformat(), nome, p1.lower(), p2.lower(), p3.lower()]
    df.to_csv(csv, index=False)
    st.success("Obrigado! Suas palavras entraram no mural.")

st.subheader("🧩 Mural de sentimentos (frequências)")
df = pd.read_csv(csv) if csv.exists() else pd.DataFrame(columns=["quando","nome","p1","p2","p3"])
if not df.empty:
    todas = df["p1"].tolist() + df["p2"].tolist() + df["p3"].tolist()
    cont = Counter([w for w in todas if w])
    freq = pd.DataFrame(cont.most_common(), columns=["palavra","frequência"])
    st.dataframe(freq, use_container_width=True)
else:
    st.info("Ainda não há palavras enviadas.")

st.subheader("🕒 Envio mais recente")
if not df.empty:
    st.dataframe(df.sort_values("quando", ascending=False).head(10), use_container_width=True)
