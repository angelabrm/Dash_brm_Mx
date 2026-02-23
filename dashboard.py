import streamlit as st
import base64
import os
import pandas as pd

# --- Utils ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/jpeg;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)

def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        if 'Documento' in df.columns:
            df['Documento'] = df['Documento'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

# --- Pages ---

def show_home(excel_path, image_path):
    # Set background only on Home page
    if os.path.exists(image_path):
        set_png_as_page_bg(image_path)
    else:
        st.warning(f"Image not found at {image_path}")

    st.title("Welcome")
    
    rfc_input = st.text_input("RFC", placeholder="Ingrese su RFC aquí")
    
    if st.button("Ingresar"):
        if rfc_input:
            if os.path.exists(excel_path):
                df = load_data(excel_path)
                if df is not None:
                    clean_rfc = rfc_input.strip()
                    # Check for required columns
                    if 'Documento' in df.columns and 'Nombre' in df.columns:
                        result = df[df['Documento'] == clean_rfc]
                        if not result.empty:
                            nombre = result.iloc[0]['Nombre']
                            
                            # Get Vista Dash if it exists, otherwise default to "N/A"
                            vista_dash = "N/A"
                            if 'Vista Dash' in df.columns:
                                vista_dash = result.iloc[0]['Vista Dash']
                            
                            # Set session state to switch "page"
                            st.session_state.page = 'result'
                            st.session_state.result_name = nombre
                            st.session_state.result_vista = vista_dash
                            st.rerun()
                        else:
                            st.error("RFC no encontrado.")
                    else:
                        st.error("Columnas 'Documento' o 'Nombre' faltantes.")
            else:
                st.error(f"No se encontró {excel_path}")
        else:
            st.warning("Ingrese un RFC.")

def show_result():
    st.title("Resultado")
    
    # Display Name
    st.markdown(f"## Nombre: {st.session_state.result_name}")
    
    # Display Vista Dash
    # You can format this however you like, e.g. another header or just text
    if 'result_vista' in st.session_state:
        st.markdown(f"### Vista Dash: {st.session_state.result_vista}")
    
    if st.button("Volver"):
        st.session_state.page = 'home'
        # Clear specific session data if desired, or just overwrite next time
        st.rerun()

# --- Main ---

def main():
    st.set_page_config(page_title="Dashboard RFC", layout="centered")
    
    # Initialize Session State
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
