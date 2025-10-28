import streamlit as st
import polars as pl
import gspread

# --- Configuración de la Página ---
# Usamos el layout ancho para que la tabla ocupe más espacio
st.set_page_config(layout="wide")

st.title("Reporte - Parte Diario (Método 1)")

# --- Configuración de Google Sheets ---
SERVICE_ACCOUNT_FILE = "dotacion-key.json"
GOOGLE_SHEET_IDENTIFIER = "DOTACION_GENERAL"
HOJA_CON_LA_TABLA = "Tabla dinámica 1" # Nombre de la hoja donde están las tablas

# --- CONEXIÓN GLOBAL A GOOGLE SHEETS ---
try:
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open(GOOGLE_SHEET_IDENTIFIER)
except Exception as e:
    st.error(f"Error fatal al conectar con Google Sheets: {e}")
    # Detiene la app si no se puede conectar al inicio
    st.stop() 

# --- Función de Carga (sin cambios) ---
@st.cache_data(ttl=600) # Cachear por 10 minutos
def load_pivot_range(worksheet_name, range_name):
    """
    Se conecta a Google Sheets y lee solo el rango específico.
    """
    try:
        worksheet = sh.worksheet(worksheet_name)
        data = worksheet.get_values(range_name)
        
        if not data:
            st.error(f"No se encontraron datos en el rango {range_name} de la hoja {worksheet_name}")
            return None
        
        df = pl.DataFrame(data[1:], schema=data[0], orient="row")
        return df

    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Error: No se encontró la hoja llamada '{worksheet_name}'. Revisa el nombre.")
        return None
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al cargar '{worksheet_name}': {e}")
        return None

# --- Botón de Recarga ---
if st.button("Recargar Datos"):
    load_pivot_range.clear()
    st.toast("Datos actualizados desde Google Sheets.", icon="🔄")

st.markdown("---")

# --- App ---
df_pivot = None
with st.spinner("Cargando datos desde Google Sheets..."):
    # --- SECCIÓN 1: RESUMEN DE ESCALAFONES ---
    RANGO_RESUMEN = "A2:D5" # Rango para la primera tabla
    
    df_resumen = load_pivot_range(HOJA_CON_LA_TABLA, RANGO_RESUMEN) 

if df_resumen is not None:
    st.header("Resumen de Escalafones")
    st.dataframe(df_resumen, hide_index=True, width='stretch')

# -----------------------------------------------
# --- SECCIÓN 2: OFICIALES ---
st.markdown("---")

# 1. Define la hoja y el rango para OFICIALES
RANGO_OFICIALES = "A8:D17" # Asegúrate que este sea el rango correcto

# 2. Llama a la función de carga
try:
    df_oficiales = load_pivot_range(HOJA_CON_LA_TABLA, RANGO_OFICIALES)
    
    if df_oficiales is not None:
        # 3. Muéstrala
        st.header("OFICIALES")
        st.dataframe(df_oficiales, hide_index=True, width='stretch')

except Exception as e:
    st.warning(f"No se pudo cargar la tabla OFICIALES ({HOJA_CON_LA_TABLA}): {e}")
# -----------------------------------------------

# -----------------------------------------------
# --- SECCIÓN 3: SUBOFICIALES ---
st.markdown("---")

# 1. Define la hoja y el rango para SUBOFICIALES
# ¡OJO! Este rango es un EJEMPLO, debes cambiarlo por el correcto
RANGO_SUBOFICIALES = "A18:D25" 

# 2. Llama a la función de carga
try:
    df_suboficiales = load_pivot_range(HOJA_CON_LA_TABLA, RANGO_SUBOFICIALES)
    
    if df_suboficiales is not None:
        # 3. Muéstrala
        st.header("SUBOFICIALES")
        st.dataframe(df_suboficiales, hide_index=True, width='stretch')

except Exception as e:
    st.warning(f"No se pudo cargar la tabla SUBOFICIALES ({HOJA_CON_LA_TABLA}): {e}")
# -----------------------------------------------

# --- PARA AGREGAR OTRA TABLA, COPIA Y PEGA EL BLOQUE ANTERIOR ---

