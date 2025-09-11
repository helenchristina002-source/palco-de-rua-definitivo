import streamlit as st
import pandas as pd
import random
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Roleta de Cena + Aplausômetro", page_icon="🎲")
st.title("🎲 Roleta de Cena + 👏 Aplausômetro")

# Arquivos de dados
cenas_csv = Path("data/cenas.csv")
avaliacoes_csv = Path("data/avaliacoes.csv")
cenas_csv.parent.mkdir(exist_ok=True)
if not cenas_csv.exists():
    pd.DataFrame(columns=["quando","grupo","personagem","lugar","conflito","frase_final"]).to_csv(cenas_csv, index=False)
if not avaliacoes_csv.exists():
    pd.DataFrame(columns=["quando","grupo","avaliador","voz","clareza","impacto","coment"]).to_csv(avaliacoes_csv, index=False)

# 1) SORTEAR CENA
st.header("1) 🎲 Roleta de Cena (improviso)")
pers = ["artista mambembe","vendedor ambulante","turista","palhaço","músico de metrô","ativista","mágico de rua","contadora de histórias"]
lug  = ["praça","pátio da escola","feira","ponto de ônibus","escadaria","corredor","portão de entrada","quadra"]
conf = ["objeto perdido","mal-entendido","protesto","chuva repentina","plateia hostil","fiscal aparece","concorrência inesperada","música que para"]

if st.button("Sortear nova cena 🎯"):
    st.session_state.sorteio = (random.choice(pers), random.choice(lug), random.choice(conf))

p, l, c = st.session_state.get("sorteio", ("—","—","—"))
st.success(f"**Personagem:** {p} | **Lugar:** {l} | **Conflito:** {c}")
st.caption("Dica: 30s para planejar + 45–60s para improvisar. Fechem com uma frase marcante.")

# Cadastro do grupo
st.subheader("👥 Cadastre o grupo que vai apresentar agora")
grupo = st.text_input("Nome do grupo/cena (ex.: Grupo A, Trio 1)")
frase_final = st.text_input("Frase final (marcante), opcional")
if st.button("Salvar sorteio para este grupo 💾") and grupo and p != "—":
    dfc = pd.read_csv(cenas_csv)
    dfc.loc[len(dfc)] = [datetime.now().isoformat(), grupo, p, l, c, frase_final]
    dfc.to_csv(cenas_csv, index=False)
    st.success("Cena registrada para o grupo!")

st.divider()

# 2) APLAUSÔMETRO
st.header("2) 👏 Aplausômetro (avaliação do público)")
df_cenas = pd.read_csv(cenas_csv)
opcoes_grupo = sorted(df_cenas["grupo"].unique().tolist()) if not df_cenas.empty else []
grupo_chosen = st.selectbox("Escolha o grupo/cena para avaliar", opcoes_grupo)

avaliador = st.text_input("Seu nome (avaliador)")
col1, col2, col3 = st.columns(3)
with col1:
    voz = st.slider("Força da voz", 1, 5, 4)
with col2:
    clareza = st.slider("Clareza da mensagem", 1, 5, 4)
with col3:
    impacto = st.slider("Impacto emocional", 1, 5, 4)
coment = st.text_input("Comentário (1 frase)")

if st.button("Enviar avaliação ✅") and grupo_chosen and avaliador:
    dfa = pd.read_csv(avaliacoes_csv)
    dfa.loc[len(dfa)] = [datetime.now().isoformat(), grupo_chosen, avaliador, voz, clareza, impacto, coment]
    dfa.to_csv(avaliacoes_csv, index=False)
    st.success("Avaliação registrada! Obrigado.")

# Painel
st.subheader("📊 Painel – Médias por grupo")
dfa = pd.read_csv(avaliacoes_csv)
if not dfa.empty:
    painel = dfa.groupby("grupo")[["voz","clareza","impacto"]].mean().round(2).reset_index()
    painel["n_avaliacoes"] = dfa.groupby("grupo")["avaliador"].count().values
    st.dataframe(painel.sort_values(["voz","clareza","impacto"], ascending=False), use_container_width=True)
else:
    st.info("Sem avaliações ainda.")

st.subheader("💬 Comentários recentes")
if not dfa.empty:
    st.dataframe(dfa.sort_values("quando", ascending=False)[["grupo","avaliador","coment"]].head(15), use_container_width=True)
