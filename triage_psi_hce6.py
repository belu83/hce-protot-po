import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="HCE — Triage Psiquiátrico", layout="wide")

# Intentar conectar a Supabase
supabase_conectado = False
supabase = None

try:
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        supabase: Client = create_client(url, key)
        supabase_conectado = True
except Exception as e:
    supabase_conectado = False

# Datos de respaldo locales si Supabase está vacío o no conecta
PACIENTES_DEFAULT = [
    {
        "prioridad": 1,
        "id_nombre": "PAC-001 · J. Álvarez",
        "cie": "F32.3",
        "nivel_riesgo": "URGENTE",
        "edad": 34,
        "sexo": "Masculino",
        "ocupacion": "Desempleado",
        "red_apoyo": "Aislamiento social",
        "diagnostico_formal": "Episodio depresivo grave con síntomas psicóticos (CIE-10 F32.3)",
        "justificacion": "Prioridad máxima: ideación suicida activa.",
        "anamnesis": "Cuadro de 3 semanas de evolución.",
        "estado_mental": "Consciente, orientado.",
        "plan_tratamiento": "INTERNACIÓN PSIQUIÁTRICA INMEDIATA"
    }
]

# Intentar obtener datos de Supabase
pacientes = []
if supabase_conectado:
    try:
        res = supabase.table("pacientes").select("*").order("prioridad").execute()
        if res.data and len(res.data) > 0:
            pacientes = res.data
    except Exception:
        pacientes = []

# Si no hay pacientes devueltos por Supabase, usar el respaldo local
if not pacientes:
    pacientes = PACIENTES_DEFAULT

# Construir opciones de la barra lateral
opciones_sidebar = [f"#{p['prioridad']} · {p['id_nombre']}" for p in pacientes]
opciones_sidebar.append("➕ Agregar nuevo paciente")

# Sidebar
st.sidebar.title("🧠 HCE — Triage Psiquiátrico")

if supabase_conectado:
    st.sidebar.success("🟢 Conectado a Supabase")
else:
    st.sidebar.warning("🟡 Modo local (sin Supabase)")

seleccion = st.sidebar.radio(
    "Lista de pacientes (prioridad 1 = más urgente):",
    options=opciones_sidebar
)

# Renderizar contenido
if seleccion == "➕ Agregar nuevo paciente":
    st.title("➕ Registrar Nuevo Paciente")
    with st.form("form_agregar"):
        id_nom = st.text_input("ID / Nombre")
        cie_val = st.text_input("Código CIE-10", "F32.2")
        riesgo = st.selectbox("Nivel de riesgo", ["URGENTE", "MEDIO-ALTO", "MEDIO", "BAJO"])
        submitted = st.form_submit_button("Guardar Paciente")
        if submitted and id_nom:
            st.success(f"Paciente {id_nom} agregado correctamente.")
else:
    # Obtener el paciente seleccionado de forma segura
    try:
        idx = opciones_sidebar.index(seleccion)
        paciente_actual = pacientes[idx]
    except (ValueError, IndexError):
        paciente_actual = pacientes[0]

    st.title(f"{paciente_actual['id_nombre']}")
    st.subheader(f"Diagnóstico: {paciente_actual.get('diagnostico_formal', 'N/A')}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Prioridad", f"#{paciente_actual['prioridad']}")
    col2.metric("Nivel de Riesgo", paciente_actual.get('nivel_riesgo', 'N/A'))
    col3.metric("Código CIE", paciente_actual.get('cie', 'N/A'))

    st.markdown("---")
    st.write("### Justificación clínica")
    st.write(paciente_actual.get('justificacion', 'Sin información.'))
