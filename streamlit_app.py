import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import os

# 1. SETUP
st.set_page_config(page_title="Qubikai Brief", page_icon="📩", layout="centered")

# 2. STYLING (Focus & Dark Mode)
st.markdown("""
<style>
    /* Donkere achtergrond, alles gecentreerd */
    .stApp {background-color: #0E1117; color: #FAFAFA;}
    
    /* Knoppen styling (Groot & Duidelijk) */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        border: none;
        background-color: #1F2937; /* Standaard grijs */
        color: white;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #FF4B4B; /* Rood bij hover */
        transform: scale(1.02);
    }
    
    /* De 'Primaire' actie knoppen vallen meer op */
    .primary-btn { border: 2px solid #FF4B4B !important; }

    /* Containers */
    .css-1r6slb0 {padding: 0;} /* Minder witruimte */
    
    /* Resultaat vak */
    .advice-box {
        background-color: #161B22;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. FUNCTIES & STATE
if "step" not in st.session_state:
    st.session_state.step = 1 # We beginnen bij stap 1
if "analysis" not in st.session_state:
    st.session_state.analysis = ""
if "letter_draft" not in st.session_state:
    st.session_state.letter_draft = ""

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ API Key mist.")
    st.stop()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def reset_app():
    st.session_state.step = 1
    st.session_state.analysis = ""
    st.session_state.letter_draft = ""
    st.rerun()

# --- HEADER (Altijd zichtbaar) ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.write("📩")
with col_title:
    st.markdown("### Snap-mijn-Brief")

st.markdown("---")

# ==========================================
# STAP 1: UPLOADEN (De enige taak)
# ==========================================
if st.session_state.step == 1:
    st.markdown("### 1. Wat heb je ontvangen?")
    st.write("Maak een foto of upload de brief. Ik vertel je wat je moet doen.")
    
    uploaded_file = st.file_uploader("Kies bestand", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    
    if uploaded_file:
        # Opslaan en door naar stap 2
        st.session_state.uploaded_file = uploaded_file
        st.session_state.step = 2
        st.rerun()

# ==========================================
# STAP 2: ANALYSE & KEUZE (Het Inzicht)
# ==========================================
elif st.session_state.step == 2:
    # Toon klein de brief (zodat je weet waar het over gaat)
    image = Image.open(st.session_state.uploaded_file)
    st.image(image, caption="Jouw document", width=200)
    
    # Als we nog geen analyse hebben, maak die nu
    if not st.session_state.analysis:
        with st.spinner('🔍 Analyseren...'):
            base64_image = encode_image(image)
            prompt = """
            Je bent Qubikai. Analyseer kort.
            Output Markdown:
            ### 📄 Wat is dit? (1 zin)
            ### 🚨 Actie & Deadline (Kort)
            ### 💡 Advies (Wat moet ik doen?)
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
            )
            st.session_state.analysis = response.choices[0].message.content
    
    # Toon Resultaat
    st.markdown(f'<div class="advice-box">{st.session_state.analysis}</div>', unsafe_allow_html=True)
    
    st.markdown("### 👉 Wat wil je doen?")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("✍️ Schrijf Bezwaar"):
            st.session_state.action_type = "bezwaar"
            st.session_state.step = 3
            st.rerun()
    with c2:
        if st.button("📧 Vraag Uitstel"):
            st.session_state.action_type = "uitstel"
            st.session_state.step = 3
            st.rerun()
    with c3:
        if st.button("🔙 Nieuwe Upload"):
            reset_app()

# ==========================================
# STAP 3: DE ACTIE (De Brief Generator)
# ==========================================
elif st.session_state.step == 3:
    st.markdown(f"### ✍️ Concept: {st.session_state.action_type.capitalize()}")
    
    # Brief genereren (als nog niet gedaan)
    if not st.session_state.letter_draft:
        with st.spinner('Brief aan het schrijven...'):
            # Hier zou je de AI vragen de brief te schrijven o.b.v. de analyse
            # Voor nu een dummy tekst om de flow te testen
            st.session_state.letter_draft = f"""
Betreft: Bezwaar tegen beschikking [NUMMER]

Geachte heer/mevrouw,

Hierbij maak ik bezwaar tegen de ontvangen brief d.d. [DATUM].
De reden hiervoor is dat de feiten niet kloppen.

Met vriendelijke groet,
[NAAM]
            """
            
    # Toon de editor
    txt = st.text_area("Pas de tekst aan indien nodig:", value=st.session_state.letter_draft, height=300)
    
    # Actie Knoppen
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("✅ Versturen (Demo)") # Doet nu niks
    with c2:
        st.button("💾 Opslaan")
    with c3:
        if st.button("🔙 Terug"):
            st.session_state.step = 2
            st.rerun()