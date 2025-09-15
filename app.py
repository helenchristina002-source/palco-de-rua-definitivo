import streamlit as st

st.set_page_config(page_title="Palco de Rua", page_icon="🎭")

st.title("🎭 Palco de Rua – Menu")
st.write("Escolha um módulo da oficina:")

st.page_link("pages/1_Aquecimento_Reacao.py",
             label="Reação do Espectador", icon="🔥")
st.page_link("pages/2_Roleta_e_Aplausometro.py",
             label="🎲 Roleta de Cena + 👏 Aplausômetro", icon="🎲")
