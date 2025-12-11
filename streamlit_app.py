import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import os

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
        font-size: 0.95em;
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
# 4. DE QUBIKAI MASTER PROMPTS (Jouw nieuwe brein) 🎓
# ==========================================

def get_agent_prompt(agent_role: str) -> str:
    """
    Hier zitten de systeem-instructies die je van de Architect hebt gekregen.
    """
    
    if agent_role.lower() == "analist":
        return """
# SYSTEM PROMPT: DE JURIDISCH ANALIST

## 1. PERSONA
Jij bent een Senior Juridisch Dossier Analist met 20 jaar ervaring. Jouw specialiteit is forensische documentanalyse.
Jouw nauwkeurigheid is 100%. Jij hallucineert nooit feiten.

## 2. CONTEXT ANALYSE & INSTRUCTIES
Je ontvangt een afbeelding van een officiële brief.
Jouw doel is het extraheren van de 'harde feiten'.

## 3. REDENEERSTAPPEN
1. Document Classificatie: Wat is dit voor brief?
2. Entiteit Extractie: Zoek Afzender, Kenmerk, Dagtekening, Bedrag, Feit.
3. Synthese: Vul de tabel in.

## 4. OUTPUT FORMAAT
Geef **alleen** de onderstaande Markdown tabel terug.

# ANALYSERAPPORT

| Veld | Waarde |
| :--- | :--- |
| **Instantie** | [Naam Instantie] |
| **Soort Brief** | [Bijv. Mulderbeschikking] |
| **Beschikkingsnummer** | [Het nummer] |
| **Datum Dagtekening** | [DD-MM-JJJJ] |
| **Bedrag** | [€ 0,00] |
| **Feit / Omschrijving** | [Korte omschrijving] |

**Notitie Analist:** [Korte zin over leesbaarheid of urgentie.]
"""

    elif agent_role.lower() == "jurist":
        return """
# SYSTEM PROMPT: DE ADVOCAAT BESTUURSRECHT

## 1. PERSONA
Jij bent een doorgewinterde Advocaat Bestuursrecht. Je schrijft formeel, juridisch sterk, maar helder.

## 2. CONTEXT ANALYSE
Je ontvangt een ANALYSERAPPORT.
Jouw taak is om deze feiten om te zetten in een formeel, 'pro forma' bezwaarschrift.

## 3. STRATEGIE
We maken 'pro forma' bezwaar om de termijn veilig te stellen en vragen om het dossier (art. 7:18 Awb) en uitstel voor de gronden.

## 4. OUTPUT FORMAAT
Schrijf de brief in Markdown.

# CONCEPT BEZWAARSCHRIFT

**Betreft:** Bezwaar tegen beschikking met kenmerk [BESCHIKKINGSNUMMER UIT INPUT]

Edelachtbaar College / Geachte heer/mevrouw,

Hierbij maak ik, [UW NAAM], wonende te [UW ADRES], tijdig bezwaar tegen de bovengenoemde beschikking d.d. [DATUM UIT INPUT] waarin mij een sanctie is opgelegd van [BEDRAG UIT INPUT] wegens [FEIT UIT INPUT].

**Pro Forma Bezwaar**
Op dit moment beschik ik niet over het volledige dossier om mijn bezwaren inhoudelijk te onderbouwen. Derhalve teken ik *pro forma* bezwaar aan.

**Verzoek om stukken (Art. 7:18 Awb)**
Om mijn bezwaar nader te kunnen motiveren, verzoek ik u mij – conform artikel 7:18 van de Algemene wet bestuursrecht – kosteloos alle op deze zaak betrekking hebbende stukken toe te zenden (zaakoverzicht, proces-verbaal, ijkrapporten, foto's).

**Termijn voor gronden**
Ik verzoek u mij een redelijke termijn te gunnen voor het indienen van de aanvullende gronden van het bezwaar, ingaande na ontvangst van de gevraagde stukken.

In afwachting van de toezending van de stukken, verblijf ik,

Hoogachtend,

[UW NAAM]
[UW BSN]
"""
    return ""

# ==========================================
# 5. DE AGENT FUNCTIES (De Uitvoering) 🏃‍♂️
# ==========================================

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- AGENT 1: DE ANALIST ---
def agent_analyze(base64_image):
    # Haal de slimme prompt op
    system_prompt = get_agent_prompt("analist")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "Hier is de foto van de brief. Maak het analyserapport."}, 
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fout: {e}"

# --- AGENT 2: DE JURIST ---
def agent_write_letter(analysis_text):
    # Haal de slimme prompt op
    system_prompt = get_agent_prompt("jurist")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Hier zijn de feiten uit het analyserapport:\n\n{analysis_text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fout: {e}"

# ==========================================
# 6. PAGINA'S & FLOW 📱
# ==========================================

# --- HEADER ---
c1, c2 = st.columns([1, 5])
with c1:
    if st.button("🏠", help="Home"):
        st.session_state.page = 'home'
        st.rerun()
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
            st.rerun()

# --- UPLOAD ---
elif st.session_state.page == 'upload':
    st.markdown("### 1. Upload je brief")
    uploaded_file = st.file_uploader("Kies bestand", label_visibility="collapsed")
    if uploaded_file:
        st.session_state.current_image = uploaded_file
        st.session_state.page = 'processing'
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 Terug"):
        st.session_state.page = 'home'
        st.rerun()

# --- PROCESSING (AGENT 1) ---
elif st.session_state.page == 'processing':
    with st.spinner('🕵️‍♂️ Dossier Analist leest mee...'):
        image = Image.open(st.session_state.current_image)
        base64_img = encode_image(image)
        # Agent 1 aan het werk
        st.session_state.analysis_result = agent_analyze(base64_img)
        st.session_state.page = 'result'
        st.rerun