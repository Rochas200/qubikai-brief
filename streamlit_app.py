import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import os
import time

# ==========================================
# 1. APP CONFIGURATIE (Rood voor Brief) 🔴
# ==========================================
APP_NAME = "Snap-mijn-Brief"
APP_ICON = "📮"
ACCENT_COLOR = "#FF4B4B"  # Qubikai Rood
BACKGROUND_COLOR = "#0E1117"

# ==========================================
# 2. SETUP & STYLING 🎨
# ==========================================
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
        color: #FAFAFA;
        background-color: {BACKGROUND_COLOR};
    }}
    
    [data-testid="stSidebarNav"] {{display: none;}}
    
    /* HEADER */
    .nav-bar {{
        padding: 15px;
        background-color: #161B22;
        border-bottom: 1px solid #30363D;
        margin-bottom: 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3em;
        border-left: 6px solid {ACCENT_COLOR};
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}

    /* KNOPPEN */
    div.stButton > button {{
        background-color: {ACCENT_COLOR};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        width: 100%;
        text-transform: uppercase;
        transition: 0.2s;
    }}
    div.stButton > button:hover {{
        background-color: #D93838;
        transform: translateY(-2px);
    }}

    /* RESULTAAT KAART */
    .result-card {{
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {ACCENT_COLOR};
        margin-top: 15px;
        margin-bottom: 20px;
    }}
    
    /* BRIEF PAPIER LOOK */
    .letter-paper {{
        background-color: #FAFAFA;
        color: #000;
        padding: 40px;
        border-radius: 2px;
        font-family: 'Courier New', Courier, monospace;
        line-height: 1.6;
        margin-top: 20px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. STATE & API 🧠
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = ""
if 'generated_letter' not in st.session_state:
    st.session_state.generated_letter = ""

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ CRITICAAL: Geen API Key gevonden in Secrets!")
    st.stop()

# ==========================================
# 4. HULPFUNCTIES (Met de FIX!) 🛠️
# ==========================================

# DE "VEILIGE" RERUN FUNCTIE
# Deze crasht niet, ongeacht welke versie je gebruikt.
def force_rerun():
    try:
        st.rerun()
    except AttributeError:
        # Fallback voor oudere versies
        st.experimental_rerun()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- AGENT PROMPTS ---
def get_agent_prompt(agent_role: str) -> str:
    if agent_role.lower() == "analist":
        return """
# SYSTEM PROMPT: DE JURIDISCH ANALIST
## 1. PERSONA
Jij bent een Senior Juridisch Dossier Analist. Jouw specialiteit is documentanalyse.
## 2. INSTRUCTIES
Haal de harde feiten uit de brief.
## 3. OUTPUT
Geef **alleen** de onderstaande Markdown tabel terug.

# ANALYSERAPPORT
| Veld | Waarde |
| :--- | :--- |
| **Instantie** | [Naam Instantie] |
| **Soort Brief** | [Bijv. Mulderbeschikking] |
| **Beschikkingsnummer** | [Het nummer] |
| **Datum Dagtekening** | [DD-MM-JJJJ] |
| **Bedrag** | [€ 0,00] |
| **Feit** | [Korte omschrijving] |
"""
    elif agent_role.lower() == "jurist":
        return """
# SYSTEM PROMPT: DE ADVOCAAT BESTUURSRECHT
## 1. PERSONA
Jij bent een Advocaat Bestuursrecht. Schrijf formeel maar helder.
## 2. STRATEGIE
Maak 'pro forma' bezwaar om de termijn veilig te stellen en vraag dossierstukken op.
## 3. OUTPUT
Schrijf een concept bezwaarschrift in Markdown met placeholders [NAAM], [ADRES].
Verwijs naar Art 7:18 Awb (recht op stukken).
"""
    return ""

# --- AGENT FUNCTIES ---
def agent_analyze(base64_image):
    system_prompt = get_agent_prompt("analist")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyseer deze brief."}, 
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fout: {e}"

def agent_write_letter(analysis_text):
    system_prompt = get_agent_prompt("jurist")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Hier zijn de feiten:\n\n{analysis_text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fout: {e}"

# ==========================================
# 5. PAGINA'S & FLOW 📱
# ==========================================

# --- HEADER ---
c1, c2 = st.columns([1, 5])
with c1:
    if st.button("🏠", help="Home"):
        st.session_state.page = 'home'
        force_rerun()
with c2:
    st.markdown(f"<div class='nav-bar'>{APP_NAME}</div>", unsafe_allow_html=True)

# --- HOME ---
if st.session_state.page == 'home':
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
    st.markdown("<h2 style='text-align: center;'>Geen paniek over post. 📮</h2>", unsafe_allow_html=True)
    st.write("<div style='text-align: center; color: #ccc;'>Ik vertaal ambtelijke taal naar actiepunten.</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c_l, c_b, c_r = st.columns([1,2,1])
    with c_b:
        if st.button("📸 SCAN MIJN BRIEF", type="primary"):
            st.session_state.page = 'upload'
            force_rerun()

# --- UPLOAD ---
elif st.session_state.page == 'upload':
    st.markdown("### 1. Upload je brief")
    uploaded_file = st.file_uploader("Kies bestand", label_visibility="collapsed")
    if uploaded_file:
        st.session_state.current_image = uploaded_file
        st.session_state.page = 'processing'
        force_rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 Terug"):
        st.session_state.page = 'home'
        force_rerun()

# --- PROCESSING ---
elif st.session_state.page == 'processing':
    with st.spinner('🕵️‍♂️ Dossier Analist leest mee...'):
        # Simpele vertraging voor UX
        time.sleep(0.5)
        image = Image.open(st.session_state.current_image)
        base64_img = encode_image(image)
        
        st.session_state.analysis_result = agent_analyze(base64_img)
        
        st.session_state.page = 'result'
        force_rerun()

# --- RESULTAAT ---
elif st.session_state.page == 'result':
    c_img, c_txt = st.columns([1, 2])
    with c_img:
        img = Image.open(st.session_state.current_image)
        st.image(img, use_container_width=True, caption="Scan")
    with c_txt:
        st.markdown("### 📋 Analyserapport")
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.analysis_result)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.write("### Wat wil je doen?")
    
    c1, c2 = st.columns(2)
    with c1:
        # ACTIE: Estafette naar Jurist
        if st.button("✍️ Maak Pro-Forma Bezwaar"):
            st.session_state.page = 'writing'
            force_rerun()
    with c2:
        if st.button("✅ Ik regel het zelf"):
             st.success("Top! Succes.")
             
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Nieuwe Scan"):
        st.session_state.page = 'home'
        force_rerun()

# --- WRITING (JURIST) ---
elif st.session_state.page == 'writing':
    st.markdown("### ⚖️ De Advocaat schrijft...")
    
    if not st.session_state.generated_letter:
        with st.spinner("Wetten en regels checken..."):
            brief = agent_write_letter(st.session_state.analysis_result)
            st.session_state.generated_letter = brief
    
    st.markdown('<div class="letter-paper">', unsafe_allow_html=True)
    st.markdown(st.session_state.generated_letter)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Tip: Kopieer deze tekst naar Word en vul je gegevens in.")
    
    if st.button("🔄 Begin Opnieuw"):
        st.session_state.analysis_result = ""
        st.session_state.generated_letter = ""
        st.session_state.page = 'home'
        force_rerun()