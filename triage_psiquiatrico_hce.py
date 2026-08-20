"""
====================================================================
 HCE SIMULADA - TRIAGE PSIQUIÁTRICO (DEPRESIÓN) - 20 PACIENTES + ALTA
====================================================================
Prototipo educativo/demostrativo de una Historia Clínica Electrónica
para priorización clínica de pacientes con trastornos depresivos.
Incluye panel para agregar nuevos pacientes a la lista de triage
(se guardan en st.session_state mientras dure la sesión del navegador).

IMPORTANTE:
- Todos los datos de pacientes son FICTICIOS / SIMULADOS, generados
  únicamente con fines educativos y de demostración de software.
- Esta herramienta NO debe usarse para tomar decisiones clínicas
  reales. No sustituye el juicio de un profesional de salud mental.

CÓMO EJECUTAR:
1. Instala las dependencias:
       pip install streamlit pandas
2. Guarda este archivo como: triage_psiquiatrico_hce.py
3. Ejecuta desde la terminal:
       streamlit run triage_psiquiatrico_hce.py
4. Se abrirá automáticamente en tu navegador (http://localhost:8501)
====================================================================
"""

import streamlit as st
import pandas as pd
import copy
import os

# --------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# --------------------------------------------------------------
st.set_page_config(
    page_title="HCE - Triage Psiquiátrico",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------
# ESTÉTICA "WINDOWS VISTA / FRUTIGER AERO" — CSS INYECTADO
# --------------------------------------------------------------
# Cristal translúcido (Aero Glass), degradados glossy, bordes
# brillantes y fondo azul marino / teal / gris metálico.
AERO_CSS = """
<style>

/* ---------- Tipografía general ---------- */
html, body, [class*="css"] {
    font-family: "Segoe UI", "Trebuchet MS", Tahoma, sans-serif;
}

/* ---------- Fondo general: degradado marino / teal / metálico ---------- */
.stApp {
    background: radial-gradient(circle at 15% 0%, #dfeffa 0%, transparent 45%),
                radial-gradient(circle at 85% 10%, #c9f4ea 0%, transparent 40%),
                linear-gradient(160deg, #0a2a43 0%, #124f6b 22%, #1c7a8c 45%,
                                 #3f9fa8 62%, #7fb8bd 78%, #b9c9cf 100%);
    background-attachment: fixed;
}

/* Burbujas/reflejos decorativos flotando en el fondo (look Aero clásico) */
.stApp::before {
    content: "";
    position: fixed;
    top: -120px; left: -100px;
    width: 480px; height: 480px;
    background: radial-gradient(circle at 35% 30%,
                rgba(255,255,255,0.55) 0%,
                rgba(255,255,255,0.12) 35%,
                rgba(255,255,255,0) 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}
.stApp::after {
    content: "";
    position: fixed;
    bottom: -160px; right: -120px;
    width: 560px; height: 560px;
    background: radial-gradient(circle at 60% 60%,
                rgba(180,255,240,0.35) 0%,
                rgba(180,255,240,0.08) 40%,
                rgba(180,255,240,0) 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}

/* ---------- Bloque principal: contenedor de cristal ---------- */
[data-testid="stAppViewContainer"] > .main .block-container {
    background: rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(18px) saturate(160%);
    -webkit-backdrop-filter: blur(18px) saturate(160%);
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-radius: 18px;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.8),
        inset 0 -1px 12px rgba(255,255,255,0.15),
        0 8px 32px rgba(6, 30, 45, 0.35);
    padding: 2rem 2.4rem 2.4rem 2.4rem;
    margin-top: 1rem;
}

/* ---------- Sidebar: panel de cristal con brillo superior ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
                rgba(230, 248, 255, 0.55) 0%,
                rgba(150, 200, 215, 0.35) 40%,
                rgba(40, 90, 110, 0.45) 100%);
    backdrop-filter: blur(16px) saturate(160%);
    -webkit-backdrop-filter: blur(16px) saturate(160%);
    border-right: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: inset -1px 0 0 rgba(255,255,255,0.25);
}
[data-testid="stSidebar"] * {
    color: #0b2e3d;
}
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {
    color: #14495a !important;
}

/* ---------- Títulos con relieve tipo Vista (glow + sombra suave) ---------- */
h1, h2, h3 {
    color: #0c2e42;
    text-shadow: 0 1px 0 rgba(255,255,255,0.65), 0 2px 6px rgba(255,255,255,0.35);
    font-weight: 700;
}
h1 { letter-spacing: 0.3px; }

/* ---------- Botones: efecto "glossy" clásico Aero ---------- */
.stButton > button, .stFormSubmitButton > button {
    position: relative;
    background: linear-gradient(180deg, #eaf9ff 0%, #bfe8f5 45%, #7fc4de 46%, #4fa8c9 100%);
    border: 1px solid #3f8aad;
    border-radius: 10px;
    color: #0b2e3d;
    font-weight: 600;
    padding: 0.5rem 1.1rem;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.9),
        0 2px 6px rgba(10, 40, 60, 0.35);
    transition: all 0.15s ease-in-out;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: linear-gradient(180deg, #f5fdff 0%, #d3f1fb 45%, #98d5ea 46%, #5fb6d6 100%);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.95),
        0 4px 10px rgba(10, 40, 60, 0.45);
    transform: translateY(-1px);
}
.stButton > button:active, .stFormSubmitButton > button:active {
    transform: translateY(1px);
    box-shadow: inset 0 2px 4px rgba(10,40,60,0.35);
}

/* ---------- Radios (lista de pacientes) con look de "burbuja" cristal ---------- */
[data-testid="stSidebar"] [role="radiogroup"] label {
    background: rgba(255, 255, 255, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-radius: 10px;
    padding: 6px 10px;
    margin-bottom: 4px;
    backdrop-filter: blur(6px);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.8), 0 1px 3px rgba(10,40,60,0.15);
    transition: background 0.15s ease-in-out;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.7);
}

/* ---------- Tabs con estilo "pill" glossy ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(255,255,255,0.25);
    backdrop-filter: blur(10px);
    border-radius: 14px;
    padding: 6px;
    border: 1px solid rgba(255,255,255,0.5);
}
.stTabs [data-baseweb="tab"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.75), rgba(200,230,240,0.55));
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.6);
    color: #0b2e3d;
    font-weight: 600;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.8);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, #bfe8f5, #4fa8c9) !important;
    color: #06202e !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.9), 0 2px 8px rgba(6,30,45,0.35);
}

/* ---------- Métricas (st.metric) como "gemas" de cristal ---------- */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.35);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.65);
    border-radius: 14px;
    padding: 12px 14px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.85), 0 3px 10px rgba(10,40,60,0.2);
}

/* ---------- Cajas informativas (st.info / st.success) tipo cristal ---------- */
[data-testid="stAlert"] {
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.6);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.7), 0 2px 8px rgba(10,40,60,0.15);
}

/* ---------- Expanders (paneles colapsables) con borde brillante ---------- */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.25);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-radius: 12px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
}

/* ---------- Inputs de texto / número / textarea con look "vidrio hundido" ---------- */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox > div {
    background: rgba(255, 255, 255, 0.55) !important;
    border: 1px solid rgba(255,255,255,0.7) !important;
    border-radius: 8px !important;
    box-shadow: inset 0 1px 4px rgba(10,40,60,0.25) !important;
}

/* ---------- Dataframe / tabla ---------- */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.6);
    box-shadow: 0 2px 10px rgba(10,40,60,0.2);
}

/* ---------- Divisores más sutiles y brillantes ---------- */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.9), transparent);
}

</style>
"""
st.markdown(AERO_CSS, unsafe_allow_html=True)

# --------------------------------------------------------------
# CANDADO DE ACCESO: PIN DE 4 DÍGITOS
# --------------------------------------------------------------
# El PIN se busca en este orden:
#   1) st.secrets["APP_PIN"]   -> recomendado para Streamlit Community Cloud
#      (se configura en el dashboard: Settings -> Secrets, formato:
#       APP_PIN = "7391")
#   2) variable de entorno APP_PIN -> recomendado para correrlo en local
#      Linux/Mac:   export APP_PIN="7391"
#      Windows CMD: set APP_PIN=7391
#      PowerShell:  $env:APP_PIN="7391"
#   3) "1234" por defecto si no se configuró nada (CÁMBIALO antes de
#      compartir la URL).
#
# ADVERTENCIA DE SEGURIDAD: un PIN de 4 dígitos numéricos solo tiene
# 10.000 combinaciones posibles y no ofrece protección real contra
# un atacante que lo intente repetidamente (no hay límite de intentos
# aquí). Es una barrera básica para compartir un prototipo con datos
# ficticios entre pocas personas de confianza — NO es apto para
# proteger datos clínicos reales expuestos en internet.
def _obtener_pin():
    try:
        if "APP_PIN" in st.secrets:
            return str(st.secrets["APP_PIN"])
    except Exception:
        pass  # No hay archivo de secrets configurado (ej. ejecución local sin secrets.toml)
    return os.environ.get("APP_PIN", "1234")


PIN_CORRECTO = _obtener_pin()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col_izq, col_centro, col_der = st.columns([1, 1.1, 1])
    with col_centro:
        st.markdown(
            """
            <div style="text-align:center; margin-top: 3rem;">
                <h1 style="margin-bottom:0;">🔒 Acceso restringido</h1>
                <p style="color:#0b2e3d;">HCE — Triage Psiquiátrico (prototipo)</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("form_pin", clear_on_submit=False):
            pin_ingresado = st.text_input(
                "Ingresa el PIN de 4 dígitos",
                type="password",
                max_chars=4,
                placeholder="••••",
            )
            entrar = st.form_submit_button("Entrar", width='stretch')

        if entrar:
            if pin_ingresado == PIN_CORRECTO:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("PIN incorrecto. Intenta nuevamente.")
    st.stop()  # Detiene la ejecución: nada del resto de la app se renderiza


# --------------------------------------------------------------
# MAPA DE COLORES / ETIQUETAS DE RIESGO
# --------------------------------------------------------------
RISK_STYLE = {
    "Urgente": {"color": "#D32F2F", "emoji": "🔴", "label": "URGENTE"},
    "Medio-Alto": {"color": "#F57C00", "emoji": "🟠", "label": "MEDIO-ALTO"},
    "Medio": {"color": "#FBC02D", "emoji": "🟡", "label": "MEDIO"},
    "Bajo": {"color": "#388E3C", "emoji": "🟢", "label": "BAJO"},
}

# --------------------------------------------------------------
# CATÁLOGO CIE-10: DEPRESIÓN, ANSIEDAD, ESTRÉS Y SOMATIZACIÓN
# --------------------------------------------------------------
# Catálogo de referencia usado en los menús desplegables de "Agregar
# paciente" y "Editar paciente". Organizado por categoría diagnóstica;
# cada entrada es (código, descripción).
CIE10_CATALOGO = {
    "Depresión y trastornos del humor (F30-F39, F06, F53)": [
        ("F32.0", "Episodio depresivo leve (sin síntomas somáticos)"),
        ("F32.01", "Episodio depresivo leve con síntomas somáticos"),
        ("F32.1", "Episodio depresivo moderado (sin síntomas somáticos)"),
        ("F32.11", "Episodio depresivo moderado con síntomas somáticos"),
        ("F32.2", "Episodio depresivo grave sin síntomas psicóticos"),
        ("F32.3", "Episodio depresivo grave con síntomas psicóticos"),
        ("F32.8", "Otros episodios depresivos (Depresión atípica / enmascarada)"),
        ("F32.9", "Episodio depresivo no especificado"),
        ("F33.0", "Trastorno depresivo recurrente, episodio actual leve"),
        ("F33.1", "Trastorno depresivo recurrente, episodio actual moderado"),
        ("F33.2", "Trastorno depresivo recurrente, episodio actual grave sin síntomas psicóticos"),
        ("F33.3", "Trastorno depresivo recurrente, episodio actual grave con síntomas psicóticos"),
        ("F33.4", "Trastorno depresivo recurrente actualmente en remisión"),
        ("F33.8", "Otros trastornos depresivos recurrentes"),
        ("F33.9", "Trastorno depresivo recurrente no especificado"),
        ("F34.1", "Distimia (Trastorno depresivo persistente)"),
        ("F34.8", "Otros trastornos del humor persistentes"),
        ("F34.9", "Trastorno del humor persistente no especificado"),
        ("F38.00", "Trastorno de ansiedad y depresión mixtos"),
        ("F38.1", "Otro trastorno depresivo breve/recurrente"),
        ("F38.8", "Otros trastornos del humor especificados"),
        ("F39", "Trastorno del humor no especificado"),
        ("F06.32", "Trastorno del humor (afectivo) orgánico con síntomas depresivos"),
        ("F10.14", "Depresión inducida por consumo de alcohol / sustancias"),
        ("F53.0", "Trastorno mental leve asociado al puerperio (Depresión posparto)"),
    ],
    "Trastornos de ansiedad y fobias (F40-F41)": [
        ("F40.0", "Agorafobia sin trastorno de pánico"),
        ("F40.01", "Agorafobia con trastorno de pánico"),
        ("F40.1", "Fobia social (Trastorno de ansiedad social)"),
        ("F40.2", "Fobia específica: Zoofobia (animales)"),
        ("F40.21", "Fobia específica: Entorno natural (alturas, tormentas, agua)"),
        ("F40.22", "Fobia específica: Sangre / Inyecciones / Daño"),
        ("F40.23", "Fobia específica: Situacional (ascensores, espacios cerrados)"),
        ("F40.24", "Fobia específica: Otra (atragantamiento, ruidos)"),
        ("F40.8", "Otros trastornos de ansiedad fóbica"),
        ("F40.9", "Trastorno de ansiedad fóbica no especificado"),
        ("F41.0", "Trastorno de pánico (ansiedad paroxística episódica)"),
        ("F41.1", "Trastorno de ansiedad generalizada (TAG)"),
        ("F41.2", "Trastorno mixto ansioso-depresivo"),
        ("F41.3", "Otro trastorno de ansiedad mixto"),
        ("F41.8", "Otros trastornos de ansiedad especificados"),
        ("F41.9", "Trastorno de ansiedad no especificado"),
    ],
    "Trastorno obsesivo-compulsivo (F42)": [
        ("F42.0", "TOC con predominio de pensamientos e ideas obsesivas"),
        ("F42.1", "TOC con predominio de actos compulsivos (rituales)"),
        ("F42.2", "TOC con pensamientos y actos compulsivos mixtos"),
        ("F42.8", "Otros trastornos obsesivo-compulsivos"),
        ("F42.9", "Trastorno obsesivo-compulsivo no especificado"),
    ],
    "Reacciones a estrés grave y adaptación (F43)": [
        ("F43.0", "Reacción de estrés agudo"),
        ("F43.1", "Trastorno de estrés postraumático (TEPT)"),
        ("F43.10", "TEPT leve / moderado"),
        ("F43.11", "TEPT grave / crónico"),
        ("F43.20", "Trastorno de adaptación con reacción depresiva breve"),
        ("F43.21", "Trastorno de adaptación con reacción depresiva prolongada"),
        ("F43.22", "Trastorno de adaptación con reacción mixta de ansiedad y depresión"),
        ("F43.23", "Trastorno de adaptación con predominio de alteración de otras emociones"),
        ("F43.24", "Trastorno de adaptación con alteración de la conducta"),
        ("F43.25", "Trastorno de adaptación con alteración mixta de emociones y conducta"),
        ("F43.28", "Trastorno de adaptación con otros síntomas especificados"),
        ("F43.8", "Otras reacciones a estrés grave"),
        ("F43.9", "Reacción a estrés grave no especificada"),
    ],
    "Trastornos somatomorfos y de ansiedad por la salud (F45)": [
        ("F45.0", "Trastorno de somatización"),
        ("F45.1", "Trastorno somatomorfo indiferenciado"),
        ("F45.2", "Trastorno hipocondríaco (Ansiedad por la salud)"),
        ("F45.3", "Disfunción autonómica somatomorfa"),
        ("F45.4", "Trastorno de dolor somatomorfo persistente"),
        ("F45.8", "Otros trastornos somatomorfos"),
        ("F45.9", "Trastorno somatomorfo no especificado"),
    ],
}

# Índice plano código -> descripción, útil para autocompletar el diagnóstico formal
CIE10_DESCRIPCION_POR_CODIGO = {
    codigo: desc
    for categoria in CIE10_CATALOGO.values()
    for codigo, desc in categoria
}

# --------------------------------------------------------------
# BASE DE DATOS SIMULADA DE 20 PACIENTES
# (ordenada de mayor a menor prioridad clínica, 1 = máxima urgencia)
# --------------------------------------------------------------
PACIENTES = [
    # ================= PRIORIDAD 1-5: RIESGO MUY ALTO / URGENTE =================
    {
        "prioridad": 1,
        "id_nombre": "PAC-001 · J. Álvarez",
        "cie": "F32.3",
        "nivel_riesgo": "Urgente",
        "edad": 34, "sexo": "Masculino", "ocupacion": "Desempleado (hace 6 meses)",
        "red_apoyo": "Aislamiento social casi total, sin contacto familiar activo",
        "diagnostico_formal": "Episodio depresivo grave con síntomas psicóticos (CIE-10 F32.3)",
        "justificacion": (
            "Prioridad máxima: ideación suicida ACTIVA con plan estructurado y acceso a medios letales "
            "(verbalizado en la entrevista de admisión). Presenta síntomas psicóticos congruentes con el "
            "estado de ánimo (delirios de culpa y ruina). Red de apoyo prácticamente inexistente, lo que "
            "elimina factores protectores inmediatos. Requiere supervisión continua y evaluación de "
            "internación involuntaria si rechaza tratamiento voluntario."
        ),
        "anamnesis": (
            "Cuadro de 3 semanas de evolución con anhedonia total, insomnio de mantenimiento severo y "
            "pérdida de 6 kg. En las últimas 48 horas refiere ideas de muerte recurrentes que evolucionaron "
            "a un plan concreto. Antecedente de un intento previo hace 2 años (intoxicación medicamentosa)."
        ),
        "estado_mental": (
            "Consciente, orientado. Facies de dolor moral marcado. Discurso enlentecido, de tono monocorde. "
            "Contenido del pensamiento con ideas delirantes de culpa ('merezco morir por lo que hice'). "
            "Juicio de realidad comprometido. Alto riesgo autolítico inminente (escala de Columbia: riesgo alto)."
        ),
        "plan_tratamiento": (
            "INTERNACIÓN PSIQUIÁTRICA INMEDIATA (evaluar carácter involuntario según normativa local). "
            "Retiro de objetos de riesgo. Interconsulta con psiquiatría de guardia en menos de 1 hora. "
            "Inicio de antipsicótico + antidepresivo bajo supervisión hospitalaria. Contención mecánica/verbal "
            "según protocolo si hay agitación. Vigilancia estrecha (1:1) las primeras 24-48 horas."
        ),
    },
    {
        "prioridad": 2,
        "id_nombre": "PAC-002 · M. Fuentealba",
        "cie": "F32.3",
        "nivel_riesgo": "Urgente",
        "edad": 47, "sexo": "Femenino", "ocupacion": "Auxiliar contable, licencia médica activa",
        "red_apoyo": "Pareja presente pero con conflicto conyugal severo actual",
        "diagnostico_formal": "Episodio depresivo grave con síntomas psicóticos (CIE-10 F32.3)",
        "justificacion": (
            "Ideación suicida activa sin plan totalmente estructurado, pero con alta letalidad potencial por "
            "acceso a psicofármacos en el hogar. Síntomas psicóticos (alucinaciones auditivas imperativas que "
            "instan a autolesionarse). El conflicto de pareja actual reduce la efectividad de la red de apoyo "
            "existente. Se posiciona como prioridad 2 por tratarse de alucinaciones IMPERATIVAS, un factor de "
            "riesgo agravado frente a ideación sin voces de mando."
        ),
        "anamnesis": (
            "Evolución de 1 mes, con empeoramiento marcado en la última semana. Refiere escuchar una voz que "
            "le dice que 'no vale nada' y que 'debería terminar con todo'. Abandono de autocuidado personal."
        ),
        "estado_mental": (
            "Hipoprosexia, bradipsiquia. Afecto embotado. Alucinaciones auditivas imperativas activas durante "
            "la entrevista. Ideación suicida presente, niega plan concreto pero refiere 'pensar en las pastillas "
            "de la casa'. Insight parcialmente conservado."
        ),
        "plan_tratamiento": (
            "INTERNACIÓN PSIQUIÁTRICA INMEDIATA. Retiro de fármacos del domicilio con apoyo de familiar. "
            "Inicio de antipsicótico atípico asociado a antidepresivo. Evaluación diaria de riesgo suicida. "
            "Intervención familiar breve para abordar el conflicto conyugal como factor precipitante."
        ),
    },
    {
        "prioridad": 3,
        "id_nombre": "PAC-003 · R. Contreras",
        "cie": "F31.5",
        "nivel_riesgo": "Urgente",
        "edad": 29, "sexo": "Masculino", "ocupacion": "Técnico en refrigeración",
        "red_apoyo": "Madre presente, pero con recursos limitados de contención",
        "diagnostico_formal": "Trastorno afectivo bipolar, episodio actual depresivo grave con síntomas "
                               "psicóticos (CIE-10 F31.5)",
        "justificacion": (
            "Aunque no verbaliza plan suicida activo en este momento, presenta un cuadro de catatonía "
            "depresiva (estupor, negativismo, rechazo de alimentos e ingesta hídrica) que constituye una "
            "urgencia médica en sí misma por riesgo de deshidratación, trombosis venosa y desnutrición aguda. "
            "El diagnóstico de base bipolar exige además cautela extrema al indicar antidepresivos (riesgo de "
            "viraje maníaco), lo que complejiza y urge el manejo especializado."
        ),
        "anamnesis": (
            "Paciente con diagnóstico previo de trastorno bipolar tipo I, en tratamiento irregular. Últimas "
            "72 horas con mutismo progresivo, inmovilidad prolongada y rechazo de alimentos."
        ),
        "estado_mental": (
            "Estuporoso, con negativismo motor. Mutismo casi total. Postura catatónica sostenida. No se logra "
            "explorar ideación suicida de forma directa por la falta de respuesta verbal; riesgo considerado "
            "alto por el cuadro clínico global e imposibilidad de autocuidado."
        ),
        "plan_tratamiento": (
            "HOSPITALIZACIÓN INMEDIATA (riesgo médico y psiquiátrico combinado). Evaluación de hidratación y "
            "estado nutricional con manejo internista concomitante. Considerar benzodiacepinas para catatonía "
            "(prueba con lorazepam) y evaluar terapia electroconvulsiva (TEC) si no hay respuesta rápida. "
            "Estabilizador del ánimo en lugar de antidepresivo en monoterapia."
        ),
    },
    {
        "prioridad": 4,
        "id_nombre": "PAC-004 · S. Bahamondes",
        "cie": "F32.3",
        "nivel_riesgo": "Urgente",
        "edad": 22, "sexo": "Femenino", "ocupacion": "Estudiante universitaria",
        "red_apoyo": "Familia presente pero desconoce la gravedad del cuadro",
        "diagnostico_formal": "Episodio depresivo grave con síntomas psicóticos (CIE-10 F32.3)",
        "justificacion": (
            "Ideación suicida activa con plan parcialmente estructurado (mencionó fecha tentativa: 'después "
            "de que terminen las clases'). Autolesiones no suicidas recientes (cortes superficiales) como "
            "conducta de escape emocional, marcador de riesgo elevado en adultos jóvenes. La familia no está "
            "al tanto de la gravedad, por lo que la red de apoyo, aunque presente físicamente, no es efectiva "
            "aún como factor protector."
        ),
        "anamnesis": (
            "Inicio hace 2 meses coincidiendo con fracaso académico y ruptura de pareja. Cortes superficiales "
            "en antebrazo la última semana. Aislamiento progresivo de amistades."
        ),
        "estado_mental": (
            "Llanto fácil durante la entrevista. Discurso coherente pero con desesperanza marcada. Ideación "
            "suicida activa con plan temporal difuso. Niega alucinaciones; sin embargo, refiere episodios "
            "de despersonalización asociados a la angustia."
        ),
        "plan_tratamiento": (
            "Derivación a URGENCIA PSIQUIÁTRICA el mismo día para evaluación de internación. Psicoeducación "
            "urgente a la familia sobre gravedad y medidas de seguridad en el hogar (retiro de elementos "
            "cortopunzantes y fármacos). Inicio de antidepresivo con monitoreo estrecho (riesgo aumentado en "
            "menores de 25 años) y psicoterapia individual intensiva."
        ),
    },
    {
        "prioridad": 5,
        "id_nombre": "PAC-005 · H. Vera",
        "cie": "F32.3",
        "nivel_riesgo": "Urgente",
        "edad": 58, "sexo": "Masculino", "ocupacion": "Jubilado (ex operario industrial)",
        "red_apoyo": "Viudo, vive solo, hijos con contacto esporádico",
        "diagnostico_formal": "Episodio depresivo grave con síntomas psicóticos (CIE-10 F32.3)",
        "justificacion": (
            "Perfil de riesgo suicida clásicamente elevado: varón mayor de 55 años, viudo reciente (8 meses), "
            "que vive solo y con consumo de alcohol aumentado como automedicación. Ideación suicida pasiva "
            "que en la entrevista escaló a activa ('a veces pienso que sería más fácil no despertar'). Se "
            "prioriza en el puesto 5 por no tener aún un plan estructurado, a diferencia de los pacientes 1-4."
        ),
        "anamnesis": (
            "Duelo complicado tras fallecimiento de esposa. Aumento progresivo de consumo de alcohol (de "
            "social a diario). Insomnio severo, pérdida de peso no intencionada de 8 kg en 2 meses."
        ),
        "estado_mental": (
            "Aspecto desaliñado. Afecto triste, congruente. Ideación suicida pasiva con viraje a activa sin "
            "plan concreto. Minimiza el consumo de alcohol. Sin síntomas psicóticos francos, aunque refiere "
            "'sentir la presencia' de su esposa fallecida (a diferenciar de duelo normal vs. alteración "
            "sensoperceptiva patológica)."
        ),
        "plan_tratamiento": (
            "Derivación a URGENCIA para evaluación de internación breve u hospital de día intensivo. "
            "Evaluación de consumo de alcohol (posible sindrome de abstinencia a vigilar). Contacto activo "
            "con hijos para reforzar red de apoyo y activar plan de seguridad domiciliario. Inicio de "
            "antidepresivo y derivación a grupo de duelo."
        ),
    },

    # ================= PRIORIDAD 6-11: RIESGO ALTO =================
    {
        "prioridad": 6,
        "id_nombre": "PAC-006 · C. Muñoz",
        "cie": "F32.2",
        "nivel_riesgo": "Medio-Alto",
        "edad": 41, "sexo": "Femenino", "ocupacion": "Enfermera, turnos rotativos",
        "red_apoyo": "Pareja e hijos presentes, buen vínculo pero sobrecargados",
        "diagnostico_formal": "Episodio depresivo grave sin síntomas psicóticos (CIE-10 F32.2)",
        "justificacion": (
            "Depresión grave sin ideación suicida activa actualmente (última ideación hace 3 semanas, "
            "resuelta). Comorbilidad con burnout laboral severo. Se prioriza alto por el riesgo ocupacional "
            "(acceso profesional a fármacos de alta letalidad) y por historia de intento suicida previo hace "
            "5 años, factor de riesgo persistente aunque no esté activo hoy."
        ),
        "anamnesis": (
            "Síntomas depresivos graves de 6 semanas de evolución en contexto de sobrecarga laboral extrema "
            "post-pandemia. Fatiga, anhedonia, sentimientos de inutilidad marcados. Ideación suicida pasiva "
            "hace 3 semanas, actualmente niega ideación activa."
        ),
        "estado_mental": (
            "Discurso coherente, enlentecido. Afecto deprimido con congruencia ideoafectiva. Niega ideación "
            "suicida actual pero mantiene desesperanza moderada-alta. Sin alteraciones sensoperceptivas."
        ),
        "plan_tratamiento": (
            "Derivación preferente a psiquiatría (evaluación en 24-48 horas). Considerar licencia médica "
            "extendida. Inicio/ajuste de farmacoterapia antidepresiva con control semanal las primeras "
            "4 semanas. Psicoterapia (TCC) enfocada en burnout. Plan de seguridad escrito ante recaída."
        ),
    },
    {
        "prioridad": 7,
        "id_nombre": "PAC-007 · D. Rojas",
        "cie": "F33.2",
        "nivel_riesgo": "Medio-Alto",
        "edad": 36, "sexo": "Masculino", "ocupacion": "Chofer de transporte de carga",
        "red_apoyo": "Escasa, familia en otra ciudad",
        "diagnostico_formal": "Trastorno depresivo recurrente, episodio actual grave sin síntomas "
                               "psicóticos (CIE-10 F33.2)",
        "justificacion": (
            "Tercer episodio depresivo grave recurrente, con comorbilidad de trastorno por uso de alcohol "
            "moderado (automedicación). Sin ideación suicida activa en la entrevista, pero con antecedente "
            "de impulsividad bajo intoxicación. La combinación de recurrencia + consumo de sustancias + "
            "aislamiento geográfico de la red de apoyo determina la priorización alta."
        ),
        "anamnesis": (
            "Tercer episodio depresivo en 8 años. Consumo de alcohol los fines de semana en aumento como "
            "forma de 'desconectar'. Dificultad progresiva para mantener el ritmo laboral de largas rutas."
        ),
        "estado_mental": (
            "Alerta, orientado. Afecto disfórico. Minimiza el consumo de alcohol. Niega ideación suicida "
            "actual, aunque reconoce impulsividad previa bajo consumo. Insight parcial."
        ),
        "plan_tratamiento": (
            "Derivación a psiquiatría en un plazo de 48-72 horas. Evaluación y manejo del consumo de "
            "alcohol (interconsulta a programa de adicciones). Inicio de farmacoterapia antidepresiva "
            "considerando interacción con alcohol. Evaluación de aptitud laboral transitoria (conducción)."
        ),
    },
    {
        "prioridad": 8,
        "id_nombre": "PAC-008 · P. Sepúlveda",
        "cie": "F32.2",
        "nivel_riesgo": "Medio-Alto",
        "edad": 63, "sexo": "Femenino", "ocupacion": "Jubilada",
        "red_apoyo": "Hija cercana y presente, buen vínculo",
        "diagnostico_formal": "Episodio depresivo grave sin síntomas psicóticos (CIE-10 F32.2), "
                               "comórbido con Diabetes Mellitus tipo 2 e Hipertensión arterial",
        "justificacion": (
            "Depresión grave con importante comorbilidad médica (diabetes descompensada, HTA), lo que eleva "
            "el riesgo global por interacción entre enfermedad física y psiquiátrica (peor control metabólico "
            "asociado a depresión no tratada). Sin ideación suicida activa. Buena red de apoyo actúa como "
            "factor protector relevante, por lo que no se prioriza en el grupo más urgente."
        ),
        "anamnesis": (
            "Deterioro anímico de 2 meses coincidente con descompensación de diabetes (HbA1c en aumento). "
            "Abandono parcial de controles médicos y de adherencia a insulina por apatía y desmotivación."
        ),
        "estado_mental": (
            "Afecto triste, congruente. Fatiga marcada. Sin ideación suicida. Preocupación somática "
            "predominante relacionada con su condición médica. Buen contacto con la realidad."
        ),
        "plan_tratamiento": (
            "Derivación a psiquiatría preferente (dentro de la semana). Coordinación estrecha con equipo de "
            "diabetología/medicina interna (manejo integrado). Inicio de antidepresivo con perfil seguro en "
            "comorbilidad cardiometabólica. Psicoeducación en adherencia terapéutica."
        ),
    },
    {
        "prioridad": 9,
        "id_nombre": "PAC-009 · L. Castillo",
        "cie": "F33.2",
        "nivel_riesgo": "Medio-Alto",
        "edad": 26, "sexo": "Femenino", "ocupacion": "Diseñadora gráfica freelance",
        "red_apoyo": "Amistades cercanas, familia distante emocionalmente",
        "diagnostico_formal": "Trastorno depresivo recurrente, episodio actual grave sin síntomas "
                               "psicóticos (CIE-10 F33.2)",
        "justificacion": (
            "Episodio grave recurrente (segundo episodio) con antecedente de autolesiones no suicidas en la "
            "adolescencia (sin recurrencia actual). Sin ideación suicida activa en este momento. Se prioriza "
            "en riesgo alto por la intensidad sintomática funcional (incapacidad casi total para trabajar) "
            "más que por riesgo autolítico inminente."
        ),
        "anamnesis": (
            "Segundo episodio depresivo grave, esta vez sin el componente ansioso predominante del primero. "
            "Incapacidad para concentrarse en el trabajo desde hace 5 semanas, con pérdida de ingresos."
        ),
        "estado_mental": (
            "Discurso lento pero coherente. Anhedonia marcada. Niega ideación suicida actual y autolesiones "
            "recientes. Ansiedad concomitante moderada. Insight conservado."
        ),
        "plan_tratamiento": (
            "Derivación a psiquiatría dentro de la semana. Inicio de farmacoterapia antidepresiva. "
            "Psicoterapia cognitivo-conductual semanal. Evaluación de licencia médica breve dado el impacto "
            "funcional laboral."
        ),
    },
    {
        "prioridad": 10,
        "id_nombre": "PAC-010 · A. Herrera",
        "cie": "F32.2",
        "nivel_riesgo": "Medio-Alto",
        "edad": 50, "sexo": "Masculino", "ocupacion": "Comerciante independiente",
        "red_apoyo": "Esposa presente, relación tensa por estrés económico",
        "diagnostico_formal": "Episodio depresivo grave sin síntomas psicóticos (CIE-10 F32.2)",
        "justificacion": (
            "Depresión grave secundaria a estrés financiero severo (quiebra reciente del negocio). Sin "
            "ideación suicida activa, pero con desesperanza marcada respecto al futuro económico. Comorbilidad "
            "con insomnio severo y síntomas ansiosos. Prioridad alta por el estresor activo y no resuelto, "
            "que mantiene el riesgo de progresión del cuadro."
        ),
        "anamnesis": (
            "Cuadro de 1 mes tras cierre de su negocio por deudas. Insomnio de conciliación severo, "
            "irritabilidad, preocupación excesiva por el futuro económico familiar."
        ),
        "estado_mental": (
            "Afecto ansioso-depresivo. Discurso rápido al hablar de temas financieros, enlentecido en el "
            "resto. Niega ideación suicida. Rumiación marcada sobre pérdidas económicas."
        ),
        "plan_tratamiento": (
            "Derivación a psiquiatría dentro de la semana. Inicio de antidepresivo con componente ansiolítico "
            "asociado. Psicoterapia breve enfocada en resolución de problemas. Evaluación social/orientación "
            "a redes de apoyo comunitario por la situación económica."
        ),
    },
    {
        "prioridad": 11,
        "id_nombre": "PAC-011 · N. Pizarro",
        "cie": "F33.2",
        "nivel_riesgo": "Medio-Alto",
        "edad": 44, "sexo": "Femenino", "ocupacion": "Profesora de enseñanza básica",
        "red_apoyo": "Pareja presente, buen vínculo, sin hijos",
        "diagnostico_formal": "Trastorno depresivo recurrente, episodio actual grave sin síntomas "
                               "psicóticos (CIE-10 F33.2)",
        "justificacion": (
            "Cuarto episodio depresivo grave recurrente en paciente con adherencia irregular a tratamiento "
            "previo. Sin ideación suicida activa. Buena red de apoyo actúa como factor protector. Se prioriza "
            "en este nivel principalmente por la recurrencia elevada del cuadro y el riesgo de cronificación "
            "si no se reinstaura tratamiento de mantenimiento."
        ),
        "anamnesis": (
            "Cuarto episodio en 10 años, con patrón de abandono de tratamiento tras mejoría parcial en "
            "episodios previos. Actualmente con síntomas de 3 semanas de evolución tras suspender su "
            "medicación hace 4 meses por decisión propia."
        ),
        "estado_mental": (
            "Afecto deprimido, congruente. Discurso coherente. Niega ideación suicida. Reconoce el patrón de "
            "abandono terapéutico y muestra motivación parcial para retomar tratamiento."
        ),
        "plan_tratamiento": (
            "Derivación a psiquiatría dentro de la semana. Reinicio de farmacoterapia con psicoeducación "
            "reforzada sobre adherencia y prevención de recaídas. Psicoterapia de mantenimiento a mediano "
            "plazo. Plan de seguimiento estructurado con recordatorios de controles."
        ),
    },

    # ================= PRIORIDAD 12-16: RIESGO MEDIO =================
    {
        "prioridad": 12,
        "id_nombre": "PAC-012 · F. Toledo",
        "cie": "F32.1",
        "nivel_riesgo": "Medio",
        "edad": 31, "sexo": "Masculino", "ocupacion": "Programador informático",
        "red_apoyo": "Red social amplia, familia funcional",
        "diagnostico_formal": "Episodio depresivo moderado (CIE-10 F32.1)",
        "justificacion": (
            "Depresión moderada con impacto funcional significativo en el rendimiento laboral, pero sin "
            "ideación suicida ni comorbilidades relevantes. Buena red de apoyo social y familiar como factor "
            "protector consistente. Prioridad media: requiere atención oportuna pero no representa urgencia "
            "inmediata."
        ),
        "anamnesis": (
            "Síntomas de 6 semanas de evolución: bajo ánimo, disminución de la concentración, fatiga. "
            "Mantiene funcionamiento básico (higiene, alimentación) pero con notable disminución de "
            "productividad laboral y aislamiento social parcial."
        ),
        "estado_mental": (
            "Afecto levemente deprimido. Discurso coherente y fluido. Sin ideación suicida ni alteraciones "
            "sensoperceptivas. Insight conservado, buena disposición al tratamiento."
        ),
        "plan_tratamiento": (
            "Seguimiento ambulatorio programado (cita en 1-2 semanas). Inicio de psicoterapia (TCC) como "
            "primera línea; considerar farmacoterapia si no hay respuesta en 4-6 semanas. Psicoeducación "
            "sobre higiene del sueño y actividad física."
        ),
    },
    {
        "prioridad": 13,
        "id_nombre": "PAC-013 · V. Araya",
        "cie": "F33.1",
        "nivel_riesgo": "Medio",
        "edad": 39, "sexo": "Femenino", "ocupacion": "Dueña de casa / trabajo de cuidados",
        "red_apoyo": "Esposo presente, hijos adolescentes",
        "diagnostico_formal": "Trastorno depresivo recurrente, episodio actual moderado (CIE-10 F33.1)",
        "justificacion": (
            "Segundo episodio depresivo moderado con buen funcionamiento general de la red familiar. Sin "
            "ideación suicida ni comorbilidades significativas. La recurrencia se compensa con la buena "
            "respuesta documentada al tratamiento en el episodio previo, lo que sitúa a la paciente en "
            "prioridad media dentro de la lista."
        ),
        "anamnesis": (
            "Episodio de 4 semanas de evolución, similar en presentación al episodio previo hace 3 años que "
            "respondió bien a tratamiento combinado. Sobrecarga por rol de cuidadora principal del hogar."
        ),
        "estado_mental": (
            "Afecto deprimido leve-moderado. Discurso coherente. Sin ideación suicida. Preocupación por no "
            "poder cumplir con responsabilidades familiares habituales."
        ),
        "plan_tratamiento": (
            "Seguimiento ambulatorio (cita en 1-2 semanas). Reinicio de esquema farmacológico previamente "
            "efectivo. Psicoterapia de apoyo. Involucrar a la familia en redistribución de tareas del hogar "
            "como parte del plan terapéutico."
        ),
    },
    {
        "prioridad": 14,
        "id_nombre": "PAC-014 · O. Reyes",
        "cie": "F32.1",
        "nivel_riesgo": "Medio",
        "edad": 55, "sexo": "Masculino", "ocupacion": "Profesor universitario",
        "red_apoyo": "Familia extendida presente",
        "diagnostico_formal": "Episodio depresivo moderado (CIE-10 F32.1), con Hipotiroidismo "
                               "compensado en tratamiento",
        "justificacion": (
            "Depresión moderada con comorbilidad médica ya compensada y controlada (hipotiroidismo en "
            "tratamiento estable), por lo que no constituye un factor de riesgo agravante activo. Sin "
            "ideación suicida. Impacto funcional moderado en la esfera laboral. Prioridad media estándar."
        ),
        "anamnesis": (
            "Síntomas depresivos de 5 semanas, con descarte reciente de descompensación tiroidea (TSH en "
            "rango). Disminución del interés por actividades académicas habituales."
        ),
        "estado_mental": (
            "Afecto deprimido moderado. Discurso coherente, algo enlentecido. Sin ideación suicida. Buen "
            "juicio de realidad. Reconoce el cuadro y busca ayuda de forma proactiva."
        ),
        "plan_tratamiento": (
            "Seguimiento ambulatorio (cita en 1-2 semanas). Inicio de farmacoterapia antidepresiva con "
            "control de función tiroidea en paralelo. Psicoterapia de apoyo complementaria."
        ),
    },
    {
        "prioridad": 15,
        "id_nombre": "PAC-015 · G. Salinas",
        "cie": "F33.1",
        "nivel_riesgo": "Medio",
        "edad": 24, "sexo": "Femenino", "ocupacion": "Estudiante de postgrado",
        "red_apoyo": "Compañeros de curso, familia a distancia pero disponible",
        "diagnostico_formal": "Trastorno depresivo recurrente, episodio actual moderado (CIE-10 F33.1)",
        "justificacion": (
            "Episodio moderado recurrente (segundo episodio) asociado a estrés académico. Sin ideación "
            "suicida activa ni antecedentes de autolesión. Impacto funcional moderado en el rendimiento "
            "académico. Prioridad media, sin factores que la desplacen hacia riesgo alto."
        ),
        "anamnesis": (
            "Episodio de 4 semanas relacionado con sobrecarga de tesis de postgrado. Antecedente de un "
            "episodio similar durante el pregrado, resuelto con psicoterapia sola."
        ),
        "estado_mental": (
            "Afecto deprimido leve-moderado, reactivo parcialmente al contexto. Discurso coherente. Sin "
            "ideación suicida. Ansiedad de rendimiento asociada."
        ),
        "plan_tratamiento": (
            "Seguimiento ambulatorio (cita en 2 semanas). Psicoterapia como primera línea (TCC breve "
            "orientada a manejo del estrés académico). Evaluar farmacoterapia solo si no hay mejoría en "
            "4-6 semanas."
        ),
    },
    {
        "prioridad": 16,
        "id_nombre": "PAC-016 · E. Cárdenas",
        "cie": "F32.1",
        "nivel_riesgo": "Medio",
        "edad": 48, "sexo": "Masculino", "ocupacion": "Guardia de seguridad",
        "red_apoyo": "Familia nuclear presente y funcional",
        "diagnostico_formal": "Episodio depresivo moderado (CIE-10 F32.1)",
        "justificacion": (
            "Primer episodio depresivo moderado, sin comorbilidades ni antecedentes psiquiátricos previos. "
            "Sin ideación suicida. Buen soporte familiar. Se ubica en el límite inferior del grupo de riesgo "
            "medio por tratarse de un cuadro de inicio reciente con buen pronóstico esperado."
        ),
        "anamnesis": (
            "Primer episodio depresivo, de 3 semanas de evolución, sin claro factor precipitante "
            "identificado. Fatiga y desmotivación como síntomas predominantes."
        ),
        "estado_mental": (
            "Afecto levemente deprimido. Discurso coherente y espontáneo. Sin ideación suicida ni "
            "alteraciones sensoperceptivas. Buen insight."
        ),
        "plan_tratamiento": (
            "Seguimiento ambulatorio (cita en 2-3 semanas). Psicoeducación y activación conductual como "
            "primera línea. Reevaluación en 4 semanas para definir necesidad de farmacoterapia."
        ),
    },

    # ================= PRIORIDAD 17-20: RIESGO BAJO =================
    {
        "prioridad": 17,
        "id_nombre": "PAC-017 · I. Molina",
        "cie": "F32.0",
        "nivel_riesgo": "Bajo",
        "edad": 27, "sexo": "Femenino", "ocupacion": "Recepcionista",
        "red_apoyo": "Buena red social y familiar",
        "diagnostico_formal": "Episodio depresivo leve (CIE-10 F32.0)",
        "justificacion": (
            "Episodio depresivo leve de reciente inicio, sin ideación suicida, sin comorbilidades ni "
            "impacto funcional significativo. Buena red de apoyo. Corresponde a manejo ambulatorio estándar "
            "sin carácter de urgencia."
        ),
        "anamnesis": (
            "Síntomas leves de 2 semanas de evolución: tristeza intermitente, leve disminución del interés "
            "en actividades sociales. Mantiene rendimiento laboral normal."
        ),
        "estado_mental": (
            "Afecto eutímico a levemente disfórico. Discurso fluido y coherente. Sin ideación suicida. Buen "
            "juicio de realidad e insight completo."
        ),
        "plan_tratamiento": (
            "Seguimiento ambulatorio de rutina (cita en 3-4 semanas). Psicoeducación, activación conductual "
            "y estrategias de autocuidado. No se indica farmacoterapia en esta etapa."
        ),
    },
    {
        "prioridad": 18,
        "id_nombre": "PAC-018 · B. Navarro",
        "cie": "F33.4",
        "nivel_riesgo": "Bajo",
        "edad": 52, "sexo": "Masculino", "ocupacion": "Contador, actualmente activo laboralmente",
        "red_apoyo": "Familia funcional, buena adherencia previa",
        "diagnostico_formal": "Trastorno depresivo recurrente, actualmente en remisión (CIE-10 F33.4)",
        "justificacion": (
            "Paciente en fase de remisión de un episodio depresivo previo, actualmente asintomático y con "
            "buena adherencia a tratamiento de mantenimiento. Se incluye en la lista solo para control y "
            "seguimiento de mantenimiento, sin ningún indicador de riesgo actual."
        ),
        "anamnesis": (
            "Último episodio depresivo hace 8 meses, en remisión completa desde hace 4 meses con "
            "tratamiento de mantenimiento. Sin síntomas actuales."
        ),
        "estado_mental": (
            "Eutímico. Discurso normal en forma y contenido. Sin ideación suicida. Funcionamiento global "
            "adecuado en todas las esferas."
        ),
        "plan_tratamiento": (
            "Control de mantenimiento ambulatorio de rutina (cita en 4-6 semanas). Continuar farmacoterapia "
            "de mantenimiento actual sin cambios. Reforzar psicoeducación sobre señales tempranas de recaída."
        ),
    },
    {
        "prioridad": 19,
        "id_nombre": "PAC-019 · Y. Espinoza",
        "cie": "F32.0",
        "nivel_riesgo": "Bajo",
        "edad": 19, "sexo": "Femenino", "ocupacion": "Estudiante de pregrado",
        "red_apoyo": "Familia y amigos presentes y disponibles",
        "diagnostico_formal": "Episodio depresivo leve (CIE-10 F32.0)",
        "justificacion": (
            "Síntomas depresivos leves reactivos a un estresor identificable y transitorio (adaptación a "
            "vida universitaria). Sin ideación suicida, sin comorbilidades. Excelente red de apoyo. Bajo "
            "riesgo global con buen pronóstico esperado."
        ),
        "anamnesis": (
            "Síntomas leves de 10 días de evolución en contexto de adaptación al primer año universitario. "
            "Sin alteración significativa del funcionamiento académico."
        ),
        "estado_mental": (
            "Afecto levemente disfórico, reactivo al contexto. Discurso fluido. Sin ideación suicida. Buen "
            "insight y motivación para estrategias de afrontamiento."
        ),
        "plan_tratamiento": (
            "Seguimiento ambulatorio de rutina (cita en 4 semanas) u orientación a servicio de bienestar "
            "estudiantil. Estrategias de manejo del estrés y psicoeducación. No requiere farmacoterapia."
        ),
    },
    {
        "prioridad": 20,
        "id_nombre": "PAC-020 · T. Guajardo",
        "cie": "F33.4",
        "nivel_riesgo": "Bajo",
        "edad": 61, "sexo": "Femenino", "ocupacion": "Jubilada, voluntariado activo",
        "red_apoyo": "Amplia red social comunitaria y familiar",
        "diagnostico_formal": "Trastorno depresivo recurrente, actualmente en remisión (CIE-10 F33.4)",
        "justificacion": (
            "Paciente en remisión sostenida (más de 6 meses) de trastorno depresivo recurrente, con "
            "excelente funcionamiento psicosocial actual y participación activa en actividades comunitarias. "
            "Es la prioridad más baja de la lista: solo requiere control de mantenimiento rutinario."
        ),
        "anamnesis": (
            "Último episodio hace 14 meses. En remisión completa y sostenida desde hace más de 6 meses, "
            "con tratamiento de mantenimiento en dosis estable."
        ),
        "estado_mental": (
            "Eutímica. Discurso normal, espontáneo. Sin ideación suicida. Funcionamiento global excelente, "
            "activa socialmente."
        ),
        "plan_tratamiento": (
            "Control de mantenimiento de rutina (cita en 6-8 semanas). Continuar dosis actual de "
            "mantenimiento. Evaluar en controles futuros la posibilidad de reducción gradual de dosis según "
            "criterio de psiquiatra tratante."
        ),
    },
]

# --------------------------------------------------------------
# CAPA DE DATOS: SUPABASE (nube) con respaldo automático en memoria
# --------------------------------------------------------------
# Si existen las credenciales SUPABASE_URL y SUPABASE_KEY en los
# Secrets de Streamlit, todos los pacientes y sus cambios se leen y
# escriben directamente en la tabla "pacientes" de Supabase.
# Si no hay credenciales configuradas (ej. corriendo en local sin
# haberlas puesto), la app cae automáticamente a st.session_state,
# igual que antes, para que siga siendo utilizable sin configuración.
TABLA_PACIENTES = "pacientes"
INTERVALO_AUTOSYNC_SEGUNDOS = 20  # cada cuánto se refresca solo desde la nube


@st.cache_resource(show_spinner=False)
def _obtener_cliente_supabase():
    """Crea el cliente de Supabase si las credenciales están en Secrets.
    Devuelve None si no están configuradas o si falla la conexión."""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception as e:
        st.sidebar.error(f"No se pudo conectar a Supabase: {e}")
        return None


supabase_client = _obtener_cliente_supabase()
MODO_NUBE = supabase_client is not None


@st.cache_data(ttl=INTERVALO_AUTOSYNC_SEGUNDOS, show_spinner=False)
def _leer_pacientes_nube(_client, _marca_cache: int):
    """Lee todos los pacientes desde Supabase, ordenados por prioridad.
    Streamlit cachea el resultado hasta INTERVALO_AUTOSYNC_SEGUNDOS
    (auto-sincronización) o hasta que cambie `_marca_cache` (sincronización
    manual/forzada tras un agregar/editar/eliminar)."""
    respuesta = _client.table(TABLA_PACIENTES).select("*").order("prioridad").execute()
    return respuesta.data


def _siguiente_id_local() -> int:
    st.session_state.setdefault("siguiente_id_local", 1)
    nuevo_id = st.session_state["siguiente_id_local"]
    st.session_state["siguiente_id_local"] += 1
    return nuevo_id


def _semilla_local() -> list:
    """Copia los 20 pacientes de ejemplo y les asigna un id local,
    para que la app funcione igual de bien sin conexión a la nube."""
    semilla = copy.deepcopy(PACIENTES)
    for p in semilla:
        p["id"] = _siguiente_id_local()
    return semilla


def forzar_sincronizacion():
    """Invalida el caché de lectura y obliga a releer desde Supabase
    en la próxima llamada a cargar_pacientes()."""
    st.session_state["marca_cache"] = st.session_state.get("marca_cache", 0) + 1
    _leer_pacientes_nube.clear()


def cargar_pacientes() -> list:
    """Punto único de lectura de pacientes: Supabase si hay conexión,
    memoria de sesión si no."""
    if MODO_NUBE:
        marca = st.session_state.get("marca_cache", 0)
        return _leer_pacientes_nube(supabase_client, marca)
    if "pacientes" not in st.session_state:
        st.session_state.pacientes = _semilla_local()
    return st.session_state.pacientes


def _guardar_prioridad(paciente_id, nueva_prioridad):
    if MODO_NUBE:
        supabase_client.table(TABLA_PACIENTES).update(
            {"prioridad": nueva_prioridad}
        ).eq("id", paciente_id).execute()


def agregar_paciente(nuevo_paciente: dict, posicion_deseada: int) -> dict:
    """Inserta un paciente nuevo en la posición deseada, corre al resto
    una posición y persiste el cambio (nube o local). Devuelve el
    paciente guardado (con su id ya asignado)."""
    lista = cargar_pacientes()
    posicion_deseada = max(1, min(posicion_deseada, len(lista) + 1))

    for p in lista:
        if p["prioridad"] >= posicion_deseada:
            p["prioridad"] += 1
            _guardar_prioridad(p.get("id"), p["prioridad"])

    nuevo_paciente["prioridad"] = posicion_deseada

    if MODO_NUBE:
        respuesta = supabase_client.table(TABLA_PACIENTES).insert(nuevo_paciente).execute()
        nuevo_paciente["id"] = respuesta.data[0]["id"]
        forzar_sincronizacion()
    else:
        nuevo_paciente["id"] = _siguiente_id_local()
        st.session_state.pacientes.append(nuevo_paciente)

    return nuevo_paciente


def actualizar_paciente(paciente_obj: dict, datos_actualizados: dict, nueva_prioridad: int):
    """Actualiza los datos de un paciente existente y, si cambió la
    prioridad, reordena al resto y persiste el nuevo orden."""
    lista = cargar_pacientes()
    prioridad_actual = paciente_obj["prioridad"]

    if nueva_prioridad != prioridad_actual:
        for p in lista:
            if p["id"] == paciente_obj["id"]:
                continue
            if p["prioridad"] > prioridad_actual:
                p["prioridad"] -= 1
                _guardar_prioridad(p.get("id"), p["prioridad"])
        nueva_prioridad = max(1, min(nueva_prioridad, len(lista)))
        for p in lista:
            if p["id"] == paciente_obj["id"]:
                continue
            if p["prioridad"] >= nueva_prioridad:
                p["prioridad"] += 1
                _guardar_prioridad(p.get("id"), p["prioridad"])
        datos_actualizados["prioridad"] = nueva_prioridad

    if MODO_NUBE:
        supabase_client.table(TABLA_PACIENTES).update(datos_actualizados).eq(
            "id", paciente_obj["id"]
        ).execute()
        forzar_sincronizacion()
    else:
        paciente_obj.update(datos_actualizados)


def eliminar_paciente(paciente_obj: dict):
    """Elimina un paciente y cierra el hueco de prioridad que deja."""
    lista = cargar_pacientes()
    prioridad_eliminada = paciente_obj["prioridad"]

    for p in lista:
        if p["id"] == paciente_obj["id"]:
            continue
        if p["prioridad"] > prioridad_eliminada:
            p["prioridad"] -= 1
            _guardar_prioridad(p.get("id"), p["prioridad"])

    if MODO_NUBE:
        supabase_client.table(TABLA_PACIENTES).delete().eq("id", paciente_obj["id"]).execute()
        forzar_sincronizacion()
    else:
        st.session_state.pacientes = [p for p in lista if p["id"] != paciente_obj["id"]]


pacientes = sorted(cargar_pacientes(), key=lambda x: x["prioridad"])
df_pacientes = pd.DataFrame(pacientes)

# --------------------------------------------------------------
# SIDEBAR: LISTADO DE PACIENTES ORDENADO POR PRIORIDAD
# --------------------------------------------------------------
st.sidebar.title("🧠 HCE — Triage Psiquiátrico")
st.sidebar.caption(f"Depresión · {len(pacientes)} pacientes · Ordenados por urgencia clínica")

col_estado, col_sync = st.sidebar.columns([2, 1])
with col_estado:
    if MODO_NUBE:
        st.markdown("🟢 **Conectado a la nube** (Supabase)")
    else:
        st.markdown("🟡 **Modo local** (sin Supabase)")
with col_sync:
    if st.button("🔄 Sincronizar", disabled=not MODO_NUBE, width='stretch'):
        forzar_sincronizacion()
        st.rerun()

st.sidebar.divider()

# Construimos las etiquetas de la lista para el selector
opciones_sidebar = []
for p in pacientes:
    estilo = RISK_STYLE[p["nivel_riesgo"]]
    etiqueta = f"{estilo['emoji']} #{p['prioridad']:02d} · {p['id_nombre']} · {p['cie']}"
    opciones_sidebar.append(etiqueta)

# Si acabamos de agregar un paciente, lo dejamos seleccionado automáticamente
index_default = st.session_state.get("indice_seleccion_pendiente", 0)
index_default = min(index_default, len(opciones_sidebar) - 1)

seleccion = st.sidebar.radio(
    "Lista de pacientes (prioridad 1 = más urgente):",
    options=opciones_sidebar,
    index=index_default,
    label_visibility="visible",
)
st.session_state.pop("indice_seleccion_pendiente", None)

# Recuperamos el índice y el paciente seleccionado
idx_seleccionado = opciones_sidebar.index(seleccion)
paciente = pacientes[idx_seleccionado]
estilo_actual = RISK_STYLE[paciente["nivel_riesgo"]]

st.sidebar.divider()
st.sidebar.markdown("**Leyenda de riesgo:**")
for nivel, style in RISK_STYLE.items():
    st.sidebar.markdown(f"{style['emoji']} {style['label']}")

st.sidebar.divider()

# --------------------------------------------------------------
# SIDEBAR: PANEL PARA AGREGAR UN NUEVO PACIENTE
# --------------------------------------------------------------
with st.sidebar.expander("➕ Agregar nuevo paciente", expanded=False):
    with st.form("form_nuevo_paciente", clear_on_submit=True):
        st.markdown("**Datos básicos**")
        nombre_form = st.text_input("Nombre / ID simulado *", placeholder="Ej: PAC-021 · N. Soto")
        col_a, col_b = st.columns(2)
        with col_a:
            edad_form = st.number_input("Edad", min_value=0, max_value=120, value=30)
        with col_b:
            sexo_form = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro / No binario"])
        ocupacion_form = st.text_input("Ocupación", placeholder="Ej: Estudiante")
        red_apoyo_form = st.text_input("Red de apoyo", placeholder="Ej: Familia presente y funcional")

        st.markdown("**Clasificación clínica**")
        nivel_riesgo_form = st.selectbox(
            "Nivel de riesgo",
            options=list(RISK_STYLE.keys()),
            index=2,
            help="Determina el color/etiqueta de urgencia en la lista de triage.",
        )
        categoria_cie_form = st.selectbox(
            "Categoría diagnóstica CIE-10",
            options=list(CIE10_CATALOGO.keys()),
            key="categoria_cie_agregar",
        )
        opciones_codigo_form = [
            f"{codigo} — {desc}" for codigo, desc in CIE10_CATALOGO[categoria_cie_form]
        ]
        codigo_desc_form = st.selectbox(
            "Código CIE-10",
            options=opciones_codigo_form,
            key="codigo_cie_agregar",
        )
        cie_form = codigo_desc_form.split(" — ")[0]
        diagnostico_form = st.text_input(
            "Diagnóstico formal",
            value=CIE10_DESCRIPCION_POR_CODIGO.get(cie_form, ""),
            help="Se autocompleta según el código CIE-10 elegido; puedes editarlo.",
        )

        st.markdown("**Posición en la lista de prioridad**")
        posicion_form = st.number_input(
            "Prioridad deseada (1 = más urgente)",
            min_value=1,
            max_value=len(pacientes) + 1,
            value=len(pacientes) + 1,
            help="Los pacientes con igual o menor prioridad se desplazarán una posición hacia abajo.",
        )

        st.markdown("**Detalle clínico**")
        justificacion_form = st.text_area(
            "Justificación clínica de la priorización",
            placeholder="Por qué este paciente va en esta posición exacta...",
        )
        anamnesis_form = st.text_area("Anamnesis (síntomas y evolución)")
        estado_mental_form = st.text_area("Examen del estado mental actual")
        plan_form = st.text_area("Plan de tratamiento / conducta a seguir")

        enviado = st.form_submit_button("Agregar paciente a la lista", width='stretch')

        if enviado:
            if not nombre_form.strip():
                st.error("El nombre / ID del paciente es obligatorio.")
            else:
                nuevo = {
                    "id_nombre": nombre_form.strip(),
                    "cie": cie_form,
                    "nivel_riesgo": nivel_riesgo_form,
                    "edad": int(edad_form),
                    "sexo": sexo_form,
                    "ocupacion": ocupacion_form.strip() or "No especificada",
                    "red_apoyo": red_apoyo_form.strip() or "No especificada",
                    "diagnostico_formal": diagnostico_form.strip() or f"Sin especificar (CIE-10 {cie_form})",
                    "justificacion": justificacion_form.strip() or "Sin justificación registrada.",
                    "anamnesis": anamnesis_form.strip() or "Sin anamnesis registrada.",
                    "estado_mental": estado_mental_form.strip() or "Sin examen mental registrado.",
                    "plan_tratamiento": plan_form.strip() or "Sin plan de tratamiento registrado.",
                }
                nuevo_guardado = agregar_paciente(nuevo, int(posicion_form))
                # Recalculamos dónde quedó el paciente recién agregado para dejarlo seleccionado
                lista_actualizada = sorted(cargar_pacientes(), key=lambda x: x["prioridad"])
                nuevo_indice = next(
                    i for i, p in enumerate(lista_actualizada) if p["id"] == nuevo_guardado["id"]
                )
                st.session_state["indice_seleccion_pendiente"] = nuevo_indice
                st.success(f"Paciente agregado en la posición #{nuevo_guardado['prioridad']}.")
                st.rerun()

# --------------------------------------------------------------
# SIDEBAR: CATÁLOGO CIE-10 DE CONSULTA (referencia completa)
# --------------------------------------------------------------
with st.sidebar.expander("📖 Catálogo CIE-10 (consulta)", expanded=False):
    for categoria, codigos in CIE10_CATALOGO.items():
        st.markdown(f"**{categoria}**")
        for codigo, desc in codigos:
            st.markdown(f"- `{codigo}` — {desc}")
        st.markdown("")

st.sidebar.caption(
    "⚠️ Datos ficticios generados con fines demostrativos. "
    "No corresponde a pacientes reales ni debe usarse para decisiones clínicas."
)

# --------------------------------------------------------------
# ÁREA PRINCIPAL: FICHA DEL PACIENTE SELECCIONADO
# --------------------------------------------------------------
col_titulo, col_badge = st.columns([4, 1])
with col_titulo:
    st.title(paciente["id_nombre"])
    st.markdown(
        f'<span style="color:#111111;"><b>Diagnóstico formal:</b> {paciente["diagnostico_formal"]}</span>',
        unsafe_allow_html=True,
    )
with col_badge:
    st.markdown(
        f"""
        <div style="background: linear-gradient(180deg,
                        {estilo_actual['color']}dd 0%, {estilo_actual['color']} 55%, {estilo_actual['color']}bb 100%);
                    backdrop-filter: blur(6px);
                    border: 1px solid rgba(255,255,255,0.75);
                    color:white; padding:14px; border-radius:12px;
                    text-align:center; font-weight:bold; font-size:16px;
                    box-shadow: inset 0 1px 0 rgba(255,255,255,0.7), 0 3px 10px rgba(10,40,60,0.35);
                    text-shadow: 0 1px 2px rgba(0,0,0,0.35);">
            {estilo_actual['emoji']} {estilo_actual['label']}
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------------------
# PANEL: EDITAR / ELIMINAR EL PACIENTE SELECCIONADO
# --------------------------------------------------------------


def categoria_de_codigo(codigo: str) -> str:
    """Devuelve la categoría CIE-10 a la que pertenece un código dado."""
    for categoria, codigos in CIE10_CATALOGO.items():
        if codigo in [c for c, _ in codigos]:
            return categoria
    return list(CIE10_CATALOGO.keys())[0]


with st.expander(f"✏️ Editar / eliminar a {paciente['id_nombre']}", expanded=False):
    clave_form = f"form_editar_{idx_seleccionado}_{paciente['id_nombre']}"
    with st.form(clave_form):
        st.markdown("**Datos básicos**")
        nombre_edit = st.text_input("Nombre / ID simulado *", value=paciente["id_nombre"])
        col_a, col_b = st.columns(2)
        with col_a:
            edad_edit = st.number_input(
                "Edad", min_value=0, max_value=120, value=int(paciente["edad"])
            )
        with col_b:
            opciones_sexo = ["Femenino", "Masculino", "Otro / No binario"]
            idx_sexo = opciones_sexo.index(paciente["sexo"]) if paciente["sexo"] in opciones_sexo else 0
            sexo_edit = st.selectbox("Sexo", opciones_sexo, index=idx_sexo)
        ocupacion_edit = st.text_input("Ocupación", value=paciente["ocupacion"])
        red_apoyo_edit = st.text_input("Red de apoyo", value=paciente["red_apoyo"])

        st.markdown("**Clasificación clínica**")
        opciones_riesgo = list(RISK_STYLE.keys())
        idx_riesgo = opciones_riesgo.index(paciente["nivel_riesgo"])
        nivel_riesgo_edit = st.selectbox("Nivel de riesgo", opciones_riesgo, index=idx_riesgo)

        categoria_actual = categoria_de_codigo(paciente["cie"])
        opciones_categoria = list(CIE10_CATALOGO.keys())
        idx_categoria = opciones_categoria.index(categoria_actual)
        categoria_cie_edit = st.selectbox(
            "Categoría diagnóstica CIE-10",
            options=opciones_categoria,
            index=idx_categoria,
            key=f"categoria_cie_editar_{idx_seleccionado}",
        )
        opciones_codigo_edit = [
            f"{codigo} — {desc}" for codigo, desc in CIE10_CATALOGO[categoria_cie_edit]
        ]
        codigos_planos_edit = [c for c, _ in CIE10_CATALOGO[categoria_cie_edit]]
        idx_codigo_edit = (
            codigos_planos_edit.index(paciente["cie"]) if paciente["cie"] in codigos_planos_edit else 0
        )
        codigo_desc_edit = st.selectbox(
            "Código CIE-10",
            options=opciones_codigo_edit,
            index=idx_codigo_edit,
            key=f"codigo_cie_editar_{idx_seleccionado}",
        )
        cie_edit = codigo_desc_edit.split(" — ")[0]
        diagnostico_edit = st.text_input("Diagnóstico formal", value=paciente["diagnostico_formal"])

        st.markdown("**Posición en la lista de prioridad**")
        prioridad_edit = st.number_input(
            "Prioridad (1 = más urgente)",
            min_value=1,
            max_value=len(pacientes),
            value=int(paciente["prioridad"]),
            help="Si la cambias, el resto de la lista se reordena automáticamente.",
        )

        st.markdown("**Detalle clínico**")
        justificacion_edit = st.text_area(
            "Justificación clínica de la priorización", value=paciente["justificacion"]
        )
        anamnesis_edit = st.text_area("Anamnesis (síntomas y evolución)", value=paciente["anamnesis"])
        estado_mental_edit = st.text_area(
            "Examen del estado mental actual", value=paciente["estado_mental"]
        )
        plan_edit = st.text_area(
            "Plan de tratamiento / conducta a seguir", value=paciente["plan_tratamiento"]
        )

        eliminar_confirmado = st.checkbox(
            "Confirmo que quiero ELIMINAR a este paciente de la lista (en vez de guardar cambios)"
        )

        col_guardar, col_eliminar = st.columns(2)
        with col_guardar:
            guardar = st.form_submit_button("💾 Guardar cambios", width='stretch')
        with col_eliminar:
            eliminar = st.form_submit_button("🗑️ Eliminar paciente", width='stretch')

        if guardar:
            if not nombre_edit.strip():
                st.error("El nombre / ID del paciente es obligatorio.")
            else:
                datos_actualizados = {
                    "id_nombre": nombre_edit.strip(),
                    "cie": cie_edit,
                    "nivel_riesgo": nivel_riesgo_edit,
                    "edad": int(edad_edit),
                    "sexo": sexo_edit,
                    "ocupacion": ocupacion_edit.strip() or "No especificada",
                    "red_apoyo": red_apoyo_edit.strip() or "No especificada",
                    "diagnostico_formal": diagnostico_edit.strip() or f"Sin especificar (CIE-10 {cie_edit})",
                    "justificacion": justificacion_edit.strip() or "Sin justificación registrada.",
                    "anamnesis": anamnesis_edit.strip() or "Sin anamnesis registrada.",
                    "estado_mental": estado_mental_edit.strip() or "Sin examen mental registrado.",
                    "plan_tratamiento": plan_edit.strip() or "Sin plan de tratamiento registrado.",
                }
                actualizar_paciente(paciente, datos_actualizados, int(prioridad_edit))
                lista_actualizada = sorted(cargar_pacientes(), key=lambda x: x["prioridad"])
                nuevo_indice = next(
                    i for i, p in enumerate(lista_actualizada) if p["id"] == paciente["id"]
                )
                st.session_state["indice_seleccion_pendiente"] = nuevo_indice
                st.success("Cambios guardados.")
                st.rerun()

        elif eliminar:
            if not eliminar_confirmado:
                st.error("Marca la casilla de confirmación antes de eliminar al paciente.")
            else:
                eliminar_paciente(paciente)
                st.session_state["indice_seleccion_pendiente"] = 0
                st.success("Paciente eliminado.")
                st.rerun()

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Resumen de Triage",
    "🧾 Ficha del Paciente",
    "🗣️ Anamnesis y Estado Mental",
    "💊 Plan de Tratamiento",
])

# ---------------- TAB 1: RESUMEN DE TRIAGE ----------------
with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Prioridad en lista", f"#{paciente['prioridad']} de 20")
    c2.metric("Nivel de riesgo", estilo_actual["label"])
    c3.metric("Código CIE", paciente["cie"])

    st.markdown(f"""
    <div style="border-left: 6px solid {estilo_actual['color']}; padding: 10px 16px;
                background: rgba(255,255,255,0.35); backdrop-filter: blur(8px);
                border-radius: 0 10px 10px 0; border-top: 1px solid rgba(255,255,255,0.6);
                border-right: 1px solid rgba(255,255,255,0.6); border-bottom: 1px solid rgba(255,255,255,0.6);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);">
        <b>Nivel de riesgo asignado: {estilo_actual['emoji']} {estilo_actual['label']}</b>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Justificación clínica de la priorización")
    st.write(paciente["justificacion"])

# ---------------- TAB 2: FICHA DEL PACIENTE Y DIAGNÓSTICO ----------------
with tab2:
    st.subheader("Datos demográficos")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"**Edad:** {paciente['edad']} años")
        st.markdown(f"**Sexo:** {paciente['sexo']}")
    with d2:
        st.markdown(f"**Ocupación:** {paciente['ocupacion']}")
        st.markdown(f"**Red de apoyo:** {paciente['red_apoyo']}")

    st.divider()
    st.subheader("Diagnóstico formal")
    st.markdown(
        f"""
        <div style="background: rgba(255, 255, 255, 0.35); backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.6); border-radius: 12px;
                    padding: 12px 16px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
                    color:#111111;">
            <b>{paciente['diagnostico_formal']}</b><br>
            Código: <code>{paciente['cie']}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------- TAB 3: ANAMNESIS Y ESTADO MENTAL ----------------
with tab3:
    st.subheader("Anamnesis (síntomas y evolución)")
    st.write(paciente["anamnesis"])
    st.divider()
    st.subheader("Examen del estado mental actual")
    st.write(paciente["estado_mental"])

# ---------------- TAB 4: PLAN DE TRATAMIENTO ----------------
with tab4:
    st.subheader("Conducta a seguir")
    st.success(paciente["plan_tratamiento"])

# --------------------------------------------------------------
# TABLA RESUMEN GENERAL (opcional, al final de la página)
# --------------------------------------------------------------
st.divider()
with st.expander("📊 Ver tabla resumen de los 20 pacientes"):
    df_resumen = df_pacientes[[
        "prioridad", "id_nombre", "cie", "nivel_riesgo", "edad", "sexo"
    ]].rename(columns={
        "prioridad": "Prioridad",
        "id_nombre": "Paciente",
        "cie": "CIE",
        "nivel_riesgo": "Riesgo",
        "edad": "Edad",
        "sexo": "Sexo",
    })
    st.dataframe(df_resumen, width='stretch', hide_index=True)
# Cargar datos desde Supabase
try:
    res = supabase.table("pacientes").select("*").order("prioridad").execute()
    pacientes = res.data if res.data else []
except Exception:
    pacientes = []

# Lista de opciones para el selector
opciones_sidebar = [f"#{p['prioridad']} · {p['id_nombre']}" for p in pacientes]
opciones_sidebar.append("➕ Agregar nuevo paciente")

# Selector seguro en la barra lateral
seleccion = st.sidebar.radio(
    "Lista de pacientes (prioridad 1 = más urgente):", 
    options=opciones_sidebar
)