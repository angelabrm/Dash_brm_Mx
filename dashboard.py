import streamlit as st
import pandas as pd
import os

# --- Conexión segura a PostgreSQL ---
conn = st.connection("postgresql", type="sql")

def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        if 'Documento' in df.columns:
            df['Documento'] = df['Documento'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

def show_home(excel_path, image_path):
    st.title("Welcome")
    rfc_input = st.text_input("RFC", placeholder="Ingrese su RFC aquí")

    if st.button("Ingresar"):
        if rfc_input:
            if os.path.exists(excel_path):
                df = load_data(excel_path)
                if df is not None:
                    clean_rfc = rfc_input.strip()
                    if 'Documento' in df.columns and 'Nombre' in df.columns and 'Compass' in df.columns:
                        result = df[df['Documento'] == clean_rfc]
                        if not result.empty:
                            nombre = result.iloc[0]['Nombre']
                            vista_dash = result.iloc[0]['Vista Dash'] if 'Vista Dash' in df.columns else "N/A"
                            compass_value = result.iloc[0]['Compass']

                            # --- Consulta a la base de datos ---
                            query = f"""
                                SELECT COUNT(*) AS casos
                                FROM mexico_open_cases
                                WHERE nombre_del_agente = '{compass_value}'
                            """
                            db_result = conn.query(query)
                            casos_count = db_result.iloc[0]['casos']

                            # Guardar en session_state
                            st.session_state.page = 'result'
                            st.session_state.result_name = nombre
                            st.session_state.result_vista = vista_dash
                            st.session_state.result_casos = casos_count
                            st.rerun()
                        else:
                            st.error("RFC no encontrado.")
                    else:
                        st.error("Columnas 'Documento', 'Nombre' o 'Compass' faltantes.")
            else:
                st.error(f"No se encontró {excel_path}")
        else:
            st.warning("Ingrese un RFC.")

def show_result():
    st.title("Resultado")
    st.markdown(f"## Nombre: {st.session_state.result_name}")
    st.markdown(f"### Vista Dash: {st.session_state.result_vista}")
    st.markdown(f"### Casos abiertos: {st.session_state.result_casos}")

    if st.button("Volver"):
        st.session_state.page = 'home'
        st.rerun()

def main():
    st.set_page_config(page_title="Dashboard RFC", layout="centered")
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    excel_path = "ROSTER2.xlsx"
    image_path = "stellantis.jpeg"

    if st.session_state.page == 'home':
        show_home(excel_path, image_path)
    elif st.session_state.page == 'result':
        show_result()

if __name__ == "__main__":
    main()

