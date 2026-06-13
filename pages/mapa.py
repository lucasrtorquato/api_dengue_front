import streamlit as st
import folium
from streamlit_folium import st_folium
from api import listar_focos

st.set_page_config(
    page_title="Mapa de Ocorrências",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Mapa de Ocorrências")

dados = listar_focos()

st.write(f"teste {dados}")

# Centro inicial (Presidente Prudente)
mapa = folium.Map(
    location=[-22.12, -51.39],
    zoom_start=12
)

for foco in dados:

    if not foco.get("latitude") or not foco.get("longitude"):
        continue

    cor = "red"

    if foco["status"] == "Resolvido":
        cor = "green"

    popup = f"""
    <b>Tipo:</b> {foco['tipo']}<br>
    <b>Status:</b> {foco['status']}<br>
    <b>Rua:</b> {foco['rua']}<br>
    <b>Número:</b> {foco['numero']}<br>
    <b>Bairro:</b> {foco['bairro']}<br>
    <b>Cidade:</b> {foco['cidade']}<br>
    <b>Estado:</b> {foco['estado']}<br>
    <b>CEP:</b> {foco['cep']}
    """

    folium.Marker(
        location=[
            float(foco["latitude"]),
            float(foco["longitude"])
        ],
        popup=folium.Popup(
            popup,
            max_width=350
        ),
        tooltip=foco["tipo"],
        icon=folium.Icon(
            color=cor,
            icon="info-sign"
        )
    ).add_to(mapa)

st_folium(
    mapa,
    width=None,
    height=700
)
