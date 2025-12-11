import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import os
import datetime

# ==========================================
# 1. APP SETTINGS (Jouw Huisstijl Schuifjes) 🎛️
# ==========================================
# PAS DIT AAN PER APP:
APP_TITLE = "Snap-mijn-Brief"
APP_ICON = "📩"
APP_PRIMARY_COLOR = "#FF4B4B"  # Rood voor Brief. (Gebruik #0078D7 voor Verf)
APP_BG_COLOR = "#0E1117"       # Corporate Dark
APP_TEXT_COLOR = "#FAFAFA"     # Corporate White

# DE "AGENT" (Het Brein van deze specifieke app)
def get_agent_prompt():
    return """
    Jij bent de Post-Expert van Qubikai.
    Bekijk de afbeelding. Geef antwoord in strak Markdown format.
    
    Output structuur:
    # [Korte, pakkende titel van het document]
    
    ### 🚨 Actie & Urgentie
    * **Urgentie:** [HOOG/MIDDEN/LAAG]
    * **Deadline:** [Datum of "Geen datum gevonden"]
    * **Kosten:** [Bedrag of "Geen"]
    
    ### 📄 Wat is dit?
    [Eén duidelijke zin uitleg in jip-en-janneke taal]
    
    ### 💡 Qubikai Advies
    [Jouw concrete advies: Betalen, Bezwaar maken, of Archiveren?]
    """

# ==========================================
# 2. CONFIGURATIE & CSS (Het Fundament) 🏗️
# ==========================================
st.set_page_config(page_title=f"Qubikai - {APP_TITLE}", page_icon=APP_ICON, layout="centered")

# Hier laden we het 'Montserrat' lettertype in voor die strakke website-look
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    /* ALGEMEEN */
    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
    }}
    .stApp {{
        background-color: {APP_BG_COLOR};
        color: {APP_TEXT_COLOR};
    }}
    
    /* NAVIGATIE BALK */
    .nav-bar {{
        padding: 15px;
        background-color: #161B22;
        border-bottom: 1px solid #30363D;
        margin-bottom: 25px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3em;
        letter-spacing: 1px;
        border-left: 6px solid {APP_PRIMARY_COLOR}; /* De App-Kleur */
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* RESULTAAT KAARTEN */
    .history-card {{
        background-color: #1F2937;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 4px solid {APP_PRIMARY_COLOR};
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    
    /* KNOPPEN */
    .stButton > button {{
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1rem;
        background-color: #21262d;
        color: white;
        transition: 0.3s;
        text-transform: uppercase;
        font-size: 0.9em;
        letter-spacing: 0.5px;
    }}
    .stButton > button:hover {{
        background-color: {APP_PRIMARY_COLOR};
        color: white;
        transform: translateY(-2px);
    }}
    
    /* DETAILS (Uitklap tekst) */
    details > summary {{
        list-style: none;
        cursor: pointer;
        font-weight: 600;
        color: {APP_PRIMARY_COLOR};
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. GEHEUGEN & LOGICA 🧠
# ==========================================

if "step" not in st.session_state:
    st.session_state.step = "home"
if "history" not in st.session_state:
    st.session_state.history = [] 
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = ""

# API Check
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Geen API Key. Check je Secrets!")
    st.stop()

def nav_to(step_name):
    st.session_state.step = step_name
    st.rerun()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def add_to_history(title, advice):
    timestamp = datetime.datetime.now().strftime("%d-%m %H:%M")
    st.session_state.history.append({"time": timestamp, "title": title, "advice": advice})

# ==========================================
# 4. DE INTERFACE (Schermen) 📱
# ==========================================

# --- HEADER (Altijd zichtbaar) ---
c1, c2, c3 = st.columns([1, 5, 1])
with c1:
    if st.button("🏠", help="Terug naar Home"):
        nav_to("home")
with c2:
    # De titelbalk pakt automatisch de APP_TITLE
    st.markdown(f"<div class='nav-bar'>{APP_TITLE}</div>", unsafe_allow_html=True)
with c3:
    if len(st.session_state.history) > 0:
        if st.button("📂", help="Geschiedenis"):
            nav_to("history")

# --- SCHERM 1: HOME ---
if st.session_state.step == "home":
    st.markdown("### Welkom 👋")
    st.write("Upload je document. Ik analyseer de inhoud, deadlines en acties.")
    
    st.markdown("---")
    
    # Grote Startknop
    c_start, _ = st.columns([1, 0.01])
    with c_start:
        if st.button(f"📸  Start Nieuwe Scan"):
            nav_to("upload")

# --- SCHERM 2: UPLOAD ---
elif st.session_state.step == "upload":
    st.markdown("### 1. Maak foto of kies bestand")
    
    uploaded_file = st.file_uploader("Kies bestand", label_visibility="collapsed")
    
    if uploaded_file:
        st.session_state.current_image = uploaded_file
        nav_to("processing")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 Annuleren"):
        nav_to("home")

# --- SCHERM 3: PROCESSING ---
elif st.session_state.step == "processing":
    with st.spinner('🕵️‍♂️ Qubikai AI is aan het lezen...'):
        try:
            image = Image.open(st.session_state.current_image)
            base64_img = encode_image(image)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": get_agent_prompt()},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]}
                ]
            )
            result_text = response.choices[0].message.content
            st.session_state.current_result = result_text
            
            # Slimme titel extractie
            first_line = result_text.split('\n')[0].replace('#', '').strip()
            if not first_line: first_line = "Document Scan"
            add_to_history(first_line, result_text)
            
            nav_to("result")
            
        except Exception as e:
            st.error(f"Fout: {e}")
            if st.button("Opnieuw proberen"):
                nav_to("upload")

# --- SCHERM 4: RESULTAAT ---
elif st.session_state.step == "result":
    # Linkerkolom: Foto, Rechterkolom: Tekst
    c_img, c_txt = st.columns([1, 2])
    
    with c_img:
        img = Image.open(st.session_state.current_image)
        st.image(img, use_container_width=True, caption="Jouw scan")
    
    with c_txt:
        st.markdown(st.session_state.current_result)
    
    st.markdown("---")
    st.write("### Vervolgacties")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.button("📅 Zet in Agenda (Demo)")
    with col_b:
        st.button("✉️ Delen / Mailen (Demo)")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📸 Volgende Scannen"):
        nav_to("upload")

# --- SCHERM 5: GESCHIEDENIS ---
elif st.session_state.step == "history":
    st.markdown("### 📂 Mijn Scans")
    
    for item in reversed(st.session_state.history):
        st.markdown(f"""
        <div class="history-card">
            <div style="display:flex; justify-content:space-between; color:#888; font-size:0.8em;">
                <span>{item['time']}</span>
                <span>Gescand</span>
            </div>
            <div style="font-weight:700; font-size:1.1em; margin: 5px 0;">{item['title']}</div>
            <details>
                <summary>Toon Advies</summary>
                <div style="margin-top: 10px; color: #ddd; font-size: 0.95em;">
                    {item['advice']}
                </div>
            </details>
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("🔙 Terug naar Home"):
        nav_to("home")