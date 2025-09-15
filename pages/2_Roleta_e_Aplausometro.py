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
import itertools

st.header("1) 🎲 Roleta de Cena (improviso)")

# Listas ampliadas
pers = [
    "artista mambembe","vendedor ambulante","turista","palhaço","músico de metrô","ativista",
    "mágico de rua","contadora de histórias","grafiteira","malabarista","fotógrafa urbana",
    "vigilante da praça","instrutor de capoeira","pichadora arrependida","poeta de slam",
    "pregador excêntrico","estudante atrasada","influencer ao vivo","mascote da escola",
    "atriz invisível","repórter improvisado","veterano da feira"
]
lug  = [
    "praça","pátio da escola","feira","ponto de ônibus","escadaria","corredor",
    "portão de entrada","quadra","biblioteca aberta","refeitório","estacionamento",
    "marquise","arquibancada","canchita","jardim","hall do auditório"
]
conf = [
    "objeto perdido","mal-entendido","protesto","chuva repentina","plateia hostil","fiscal aparece",
    "concorrência inesperada","música que para","celular toca no clímax","microfone falha",
    "criança interrompe","aplauso fora de hora","troca de figurino errada","luz apaga de repente",
    "barulho de sirene","mensagem urgente chega","câmera gravando sem avisar","barbeiro ambulante entra",
    "disputa por espaço","mensagem secreta no bilhete"
]

# Caminho do POOL (todas as combinações possíveis)
pool_csv = Path("data/roleta_pool.csv")
pool_csv.parent.mkdir(exist_ok=True)

def gerar_pool():
    combos = list(itertools.product(pers, lug, conf))
    df_pool = pd.DataFrame(combos, columns=["personagem","lugar","conflito"])
    # embaralha a ordem para variar
    df_pool = df_pool.sample(frac=1, random_state=None).reset_index(drop=True)
    df_pool.to_csv(pool_csv, index=False)
    return df_pool

# Carrega ou cria o pool
if pool_csv.exists():
    df_pool = pd.read_csv(pool_csv)
else:
    df_pool = gerar_pool()

# UI: info e botões de controle do pool
colA, colB, colC = st.columns([1,1,2])
with colA:
    st.metric("Combinações restantes", len(df_pool))
with colB:
    if st.button("🔄 Repor pool (recomeçar)", help="Recria todas as combinações e limpa a lista de usados."):
        df_pool = gerar_pool()
        st.success("Pool recriado!")
with colC:
    skip_remove = st.checkbox("Não remover ao sortear (modo teste)", value=False,
                              help="Marque apenas se quiser experimentar sem consumir o pool.")

# Sorteio
if st.button("Sortear próxima cena 🎯"):
    if df_pool.empty:
        st.warning("O pool acabou! Clique em 'Repor pool' para recomeçar.")
    else:
        # pega a primeira linha do pool (já embaralhado)
        row = df_pool.iloc[0]
        st.session_state.sorteio = (row["personagem"], row["lugar"], row["conflito"])
        st.success(f"**Personagem:** {row['personagem']} | **Lugar:** {row['lugar']} | **Conflito:** {row['conflito']}")
        st.caption("Dica: 30s para planejar + 45–60s para improvisar. Fechem com uma frase marcante.")

        # consome a combinação sorteada (remove do pool) — a menos que esteja em modo teste
        if not skip_remove:
            df_pool = df_pool.iloc[1:].reset_index(drop=True)
            df_pool.to_csv(pool_csv, index=False)

# Exibe o último sorteio guardado (caso não tenha clicado agora)
p, l, c = st.session_state.get("sorteio", ("—","—","—"))
if p != "—":
    st.info(f"Último sorteio ativo → **{p}** em **{l}** com **{c}**")

# Cadastro rápido do grupo que vai se apresentar
st.subheader("👥 Cadastre o grupo que vai apresentar agora")
grupo = st.text_input("Nome do grupo/cena (ex.: Grupo A, Trio 1)")
frase_final = st.text_input("Frase final (marcante), opcional")
if st.button("Salvar sorteio para este grupo 💾") and grupo and p != "—":
    dfc = pd.read_csv(cenas_csv)
    dfc.loc[len(dfc)] = [datetime.now().isoformat(), grupo, p, l, c, frase_final]
    dfc.to_csv(cenas_csv, index=False)
    st.success("Cena registrada para o grupo!")

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
