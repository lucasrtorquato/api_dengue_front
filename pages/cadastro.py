import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# ==========================================
# CONFIGURAÇÕES
# ==========================================

API_URL = "https://api-dengue-z2ly.onrender.com"

st.set_page_config(
    page_title="Cadastro de Ocorrência",
    page_icon="🦟",
    layout="wide"
)

st.title("🦟 Cadastro de Foco de Dengue")

st.markdown("""
Cadastre uma ocorrência utilizando o CEP ou selecionando o local diretamente no mapa.
Ao clicar no mapa, um marcador será exibido automaticamente e o endereço será preenchido quando possível.
""")

# ==========================================
# FUNÇÕES
# ==========================================

def buscar_cep(cep):
    try:
        resposta = requests.get(
            f"https://viacep.com.br/ws/{cep}/json/",
            timeout=10
        )

        if resposta.status_code == 200:
            dados = resposta.json()

            if "erro" not in dados:
                return dados

    except Exception:
        pass

    return None


def buscar_coordenadas(endereco):
    try:

        resposta = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": endereco,
                "format": "json",
                "limit": 1
            },
            headers={
                "User-Agent": "ProjetoCombateDengue"
            },
            timeout=10
        )

        dados = resposta.json()

        if dados:

            return (
                float(dados[0]["lat"]),
                float(dados[0]["lon"])
            )

    except Exception:
        pass

    return None, None


def buscar_endereco_por_coordenada(lat, lon):

    try:

        resposta = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "json",
                "addressdetails": 1
            },
            headers={
                "User-Agent": "ProjetoCombateDengue"
            },
            timeout=10
        )

        if resposta.status_code == 200:

            dados = resposta.json()

            endereco = dados.get(
                "address",
                {}
            )

            return {
                "cep": endereco.get(
                    "postcode",
                    ""
                ),
                "rua": endereco.get(
                    "road",
                    ""
                ),
                "bairro": endereco.get(
                    "suburb",
                    endereco.get(
                        "neighbourhood",
                        ""
                    )
                ),
                "cidade": endereco.get(
                    "city",
                    endereco.get(
                        "town",
                        endereco.get(
                            "municipality",
                            ""
                        )
                    )
                ),
                "estado": endereco.get(
                    "state",
                    ""
                )
            }

    except Exception:
        pass

    return None


def cadastrar_ocorrencia(payload):

    try:

        resposta = requests.post(
            f"{API_URL}/focos",
            json=payload,
            timeout=15
        )

        

        st.write(f"teste {API_URL}/focos {payload}")
        

        return resposta

    except Exception as erro:

        st.error(str(erro))
        return None


# ==========================================
# SESSION STATE
# ==========================================

campos = [
    "cep",
    "rua",
    "bairro",
    "cidade",
    "estado",
    "latitude",
    "longitude"
]

for campo in campos:

    if campo not in st.session_state:
        st.session_state[campo] = ""

# ==========================================
# TIPO DA OCORRÊNCIA
# ==========================================

tipo = st.selectbox(
    "Tipo da Ocorrência",
    [
        "Água parada",
        "Terreno abandonado",
        "Lixo acumulado",
        "Piscina sem manutenção"
    ]
)

# ==========================================
# CEP
# ==========================================

st.divider()

st.subheader("📮 Buscar Endereço pelo CEP")

col1, col2 = st.columns([4, 1])

with col1:

    cep_digitado = st.text_input(
        "CEP",
        value=st.session_state["cep"],
        placeholder="19000-000"
    )

with col2:

    st.write("")
    st.write("")

    buscar = st.button(
        "Buscar",
        use_container_width=True
    )

if buscar:

    dados = buscar_cep(
        cep_digitado
    )

    if dados:

        st.session_state["cep"] = cep_digitado
        st.session_state["rua"] = dados.get(
            "logradouro",
            ""
        )

        st.session_state["bairro"] = dados.get(
            "bairro",
            ""
        )

        st.session_state["cidade"] = dados.get(
            "localidade",
            ""
        )

        st.session_state["estado"] = dados.get(
            "uf",
            ""
        )

        st.success(
            "CEP localizado com sucesso."
        )

    else:

        st.error(
            "CEP não encontrado."
        )

# ==========================================
# MAPA
# ==========================================

st.divider()

st.subheader("🗺️ Selecione o Local da Ocorrência")

latitude_atual = st.session_state.get(
    "latitude"
)

longitude_atual = st.session_state.get(
    "longitude"
)

if latitude_atual and longitude_atual:

    centro = [
        latitude_atual,
        longitude_atual
    ]

else:

    # Presidente Prudente
    centro = [
        -22.1200,
        -51.3900
    ]

mapa = folium.Map(
    location=centro,
    zoom_start=13
)

# Marcador do local selecionado

if latitude_atual and longitude_atual:

    folium.Marker(
        [
            latitude_atual,
            longitude_atual
        ],
        popup="📍 Local selecionado",
        tooltip="Ocorrência",
        icon=folium.Icon(
            icon="info-sign"
        )
    ).add_to(mapa)

resultado = st_folium(
    mapa,
    width=None,
    height=500,
    key="mapa_ocorrencia"
)

# Clique no mapa

if resultado and resultado.get(
    "last_clicked"
):

    lat = resultado["last_clicked"]["lat"]
    lon = resultado["last_clicked"]["lng"]

    mudou = (
        lat != st.session_state.get(
            "latitude"
        )
        or
        lon != st.session_state.get(
            "longitude"
        )
    )

    if mudou:

        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon

        endereco = buscar_endereco_por_coordenada(
            lat,
            lon
        )

        if endereco:

            st.session_state["cep"] = endereco["cep"]
            st.session_state["rua"] = endereco["rua"]
            st.session_state["bairro"] = endereco["bairro"]
            st.session_state["cidade"] = endereco["cidade"]
            st.session_state["estado"] = endereco["estado"]

        st.rerun()

# Exibe coordenadas selecionadas

if (
    st.session_state["latitude"]
    and
    st.session_state["longitude"]
):

    st.success(
        f"📍 Local selecionado: "
        f"{st.session_state['latitude']:.6f}, "
        f"{st.session_state['longitude']:.6f}"
    )

# ==========================================
# ENDEREÇO
# ==========================================

st.divider()

st.subheader("🏠 Endereço")

col1, col2 = st.columns(2)

with col1:

    rua = st.text_input(
        "Rua",
        value=st.session_state["rua"]
    )

with col2:

    numero = st.text_input(
        "Número"
    )

col1, col2 = st.columns(2)

with col1:

    bairro = st.text_input(
        "Bairro",
        value=st.session_state["bairro"]
    )

with col2:

    complemento = st.text_input(
        "Complemento"
    )

col1, col2, col3 = st.columns(3)

with col1:

    cidade = st.text_input(
        "Cidade",
        value=st.session_state["cidade"]
    )

with col2:

    estado = st.text_input(
        "Estado",
        value=st.session_state["estado"]
    )

with col3:

    cep = st.text_input(
        "CEP",
        value=st.session_state["cep"]
    )

# ==========================================
# CADASTRO
# ==========================================

st.divider()

if st.button(
    "🦟 Cadastrar Ocorrência",
    use_container_width=True
):

    latitude = st.session_state.get(
        "latitude"
    )

    longitude = st.session_state.get(
        "longitude"
    )

    # Caso usuário não tenha clicado no mapa

    if not latitude or not longitude:

        endereco_completo = (
            f"{rua}, {numero}, "
            f"{bairro}, {cidade}, "
            f"{estado}, {cep}"
        )

        latitude, longitude = buscar_coordenadas(
            endereco_completo
        )

    if not latitude or not longitude:

        st.error(
            "Não foi possível localizar o endereço."
        )

    else:

        payload = {
            "tipo": tipo,
            "rua": rua,
            "numero": numero,
            "bairro": bairro,
            "complemento": complemento,
            "cidade": cidade,
            "estado": estado,
            "cep": cep,
            "latitude": latitude,
            "longitude": longitude
        }

        resposta = cadastrar_ocorrencia(
            payload
        )

        if resposta and resposta.status_code in [200, 201]:

            st.success(
                "✅ Ocorrência cadastrada com sucesso!"
            )

            with st.expander(
                "Visualizar dados enviados"
            ):
                st.json(payload)

        else:

            st.error(
                "Erro ao cadastrar ocorrência."
            )
