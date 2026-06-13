import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURAÇÕES
# ==========================================

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Dashboard - Combate à Dengue",
    page_icon="🦟",
    layout="wide"
)

# ==========================================
# FUNÇÕES
# ==========================================

def obter_dashboard():
    try:
        response = requests.get(
            f"{API_URL}/dashboard",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

    except Exception as erro:
        st.error(f"Erro ao carregar dashboard: {erro}")

    return None


def listar_focos():
    try:
        response = requests.get(
            f"{API_URL}/focos",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

    except Exception as erro:
        st.error(f"Erro ao carregar ocorrências: {erro}")

    return []


def resolver_foco(id_foco):
    try:
        response = requests.put(
            f"{API_URL}/focos/{id_foco}/resolver",
            timeout=10
        )

        return response.status_code == 200

    except:
        return False


def excluir_foco(id_foco):
    try:
        response = requests.delete(
            f"{API_URL}/focos/{id_foco}",
            timeout=10
        )

        return response.status_code == 200

    except:
        return False

def marcar_pendente(id_foco):
    try:
        response = requests.put(
            f"{API_URL}/focos/{id_foco}/pendente",
            timeout=10
        )

        return response.status_code == 200

    except:
        return False

# ==========================================
# CABEÇALHO
# ==========================================

st.title("🦟 Dashboard - Combate à Dengue")

st.caption(
    "Monitoramento, indicadores e administração das ocorrências registradas."
)

# ==========================================
# CARREGA DADOS
# ==========================================

dashboard = obter_dashboard()
focos = listar_focos()

# ==========================================
# KPIs
# ==========================================

if dashboard:

    st.subheader("📈 Indicadores")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total de Ocorrências",
            dashboard["total_focos"]
        )

    with col2:
        st.metric(
            "Resolvidos",
            dashboard["resolvidos"]
        )

    with col3:
        st.metric(
            "Pendentes",
            dashboard["pendentes"]
        )

# ==========================================
# GRÁFICOS
# ==========================================

if dashboard and dashboard["por_tipo"]:

    st.divider()

    st.subheader("📊 Análises")

    df_tipos = pd.DataFrame(
        list(dashboard["por_tipo"].items()),
        columns=[
            "Tipo",
            "Quantidade"
        ]
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_bar = px.bar(
            df_tipos,
            x="Tipo",
            y="Quantidade",
            text_auto=True,
            title="Ocorrências por Tipo"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    with col2:

        fig_pie = px.pie(
            df_tipos,
            names="Tipo",
            values="Quantidade",
            title="Distribuição por Tipo"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

# ==========================================
# FILTROS
# ==========================================

st.divider()

st.subheader("🔍 Filtros")

col1, col2 = st.columns(2)

with col1:

    filtro_status = st.selectbox(
        "Status",
        [
            "Todos",
            "Pendente",
            "Resolvido"
        ]
    )

with col2:

    filtro_tipo = st.selectbox(
        "Tipo",
        [
            "Todos"
        ] + sorted(
            list(
                set(
                    [
                        foco["tipo"]
                        for foco in focos
                    ]
                )
            )
        )
    )

# ==========================================
# APLICA FILTROS
# ==========================================

focos_filtrados = focos.copy()

if filtro_status != "Todos":

    focos_filtrados = [
        foco
        for foco in focos_filtrados
        if foco["status"] == filtro_status
    ]

if filtro_tipo != "Todos":

    focos_filtrados = [
        foco
        for foco in focos_filtrados
        if foco["tipo"] == filtro_tipo
    ]

# ==========================================
# TABELA
# ==========================================

st.divider()

st.subheader(
    f"📋 Ocorrências ({len(focos_filtrados)})"
)

if focos_filtrados:

    tabela = pd.DataFrame(
        focos_filtrados
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "Nenhuma ocorrência encontrada para os filtros selecionados."
    )

# ==========================================
# ADMINISTRAÇÃO
# ==========================================

st.divider()

st.subheader("⚙️ Administração")

if not focos_filtrados:

    st.info(
        "Nenhuma ocorrência para exibir."
    )

for foco in focos_filtrados:

    status = foco["status"]

    if status == "Resolvido":

        emoji = "🟢"

    else:

        emoji = "🔴"

    titulo = (
        f"{emoji} "
        f"#{foco['id']} - "
        f"{foco['tipo']} "
        f"({status})"
    )

    with st.expander(titulo):

        col1, col2 = st.columns(2)

        # ==========================
        # DADOS
        # ==========================

        with col1:

            st.markdown("### 📍 Endereço")

            st.write(
                f"**Rua:** {foco['rua']}"
            )

            st.write(
                f"**Número:** {foco['numero']}"
            )

            st.write(
                f"**Bairro:** {foco['bairro']}"
            )

            st.write(
                f"**Complemento:** "
                f"{foco.get('complemento','')}"
            )

            st.write(
                f"**Cidade:** {foco['cidade']}"
            )

            st.write(
                f"**Estado:** {foco['estado']}"
            )

            st.write(
                f"**CEP:** {foco['cep']}"
            )

        # ==========================
        # INFORMAÇÕES
        # ==========================

        with col2:

            st.markdown("### ℹ️ Informações")

            st.write(
                f"**Tipo:** {foco['tipo']}"
            )

            st.write(
                f"**Status:** {status}"
            )

            st.write(
                f"**Latitude:** "
                f"{foco.get('latitude','-')}"
            )

            st.write(
                f"**Longitude:** "
                f"{foco.get('longitude','-')}"
            )

            if foco.get("data_criacao"):

                st.write(
                    f"**Data:** "
                    f"{foco['data_criacao']}"
                )

        st.divider()

        # ==========================
        # AÇÕES
        # ==========================

        col_resolver, col_excluir = st.columns(2)

        with col_resolver:

            if status == "Pendente":

                if st.button(
                    "✅ Marcar como Resolvido",
                    key=f"resolver_{foco['id']}",
                    use_container_width=True
                ):

                    if resolver_foco(foco["id"]):

                        st.success(
                            "Ocorrência marcada como resolvida."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Erro ao atualizar ocorrência."
                        )

            else:

                if st.button(
                    "↩️ Voltar para Pendente",
                    key=f"pendente_{foco['id']}",
                    use_container_width=True
                ):

                    if marcar_pendente(
                        foco["id"]
                    ):

                        st.success(
                            "Ocorrência marcada como pendente."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Erro ao atualizar ocorrência."
                        )

        with col_excluir:

            if st.button(
                "🗑️ Excluir Ocorrência",
                key=f"excluir_{foco['id']}",
                use_container_width=True
            ):

                if excluir_foco(
                    foco["id"]
                ):

                    st.success(
                        "Ocorrência removida com sucesso."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Erro ao excluir ocorrência."
                    )

# ==========================================
# RODAPÉ
# ==========================================

st.divider()

st.caption(
    f"Total exibido: {len(focos_filtrados)} ocorrência(s)"
)