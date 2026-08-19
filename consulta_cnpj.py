import re
import io
import requests
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Consulta CNPJ", page_icon="🏢", layout="centered")
st.title(" Consulta de CNPJ")


def limpar_cnpj(cnpj):
    return re.sub(r"\D", "", cnpj)


def consultar_cnpj(cnpj):
    try:
        response = requests.get(f"https://www.receitaws.com.br/v1/cnpj/{cnpj}", timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        if data.get("status") == "ERROR":
            return None
        return data
    except Exception:
        return None


if "historico" not in st.session_state:
    st.session_state.historico = []

cnpj_input = st.text_input("Digite o CNPJ", placeholder="00.000.000/0000-00")

if st.button("Consultar", type="primary"):
    cnpj_limpo = limpar_cnpj(cnpj_input)

    if len(cnpj_limpo) != 14:
        st.error("CNPJ inválido. Informe 14 dígitos.")
    else:
        with st.spinner("Consultando..."):
            resultado = consultar_cnpj(cnpj_limpo)

        if not resultado:
            st.error("CNPJ não encontrado ou erro na consulta.")
        else:
            atividade = ""
            if resultado.get("atividade_principal"):
                atividade = resultado["atividade_principal"][0].get("text", "")

            dados = {
                "CNPJ": cnpj_limpo,
                "Razão Social": resultado.get("nome", ""),
                "Fantasia": resultado.get("fantasia", ""),
                "Situação": resultado.get("situacao", ""),
                "Logradouro": resultado.get("logradouro", ""),
                "Número": resultado.get("numero", ""),
                "Complemento": resultado.get("complemento", ""),
                "Bairro/Distrito": resultado.get("bairro", ""),
                "Cidade": resultado.get("municipio", ""),
                "UF": resultado.get("uf", ""),
                "Ente Federativo Responsável": resultado.get("efr", ""),
                "Atividade Principal": atividade,
            }

            st.session_state.historico.append(dados)
            st.session_state.ultimo = dados

if "ultimo" in st.session_state:
    st.subheader("Resultado")
    for campo, valor in st.session_state.ultimo.items():
        st.markdown(f"**{campo}:** {valor}")

if st.session_state.historico:
    st.divider()
    st.subheader(f"Histórico ({len(st.session_state.historico)} consultas)")
    df = pd.DataFrame(st.session_state.historico)
    st.dataframe(df, use_container_width=True)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    st.download_button(
        label="⬇️ Exportar Excel",
        data=buffer,
        file_name="consulta_cnpj.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )