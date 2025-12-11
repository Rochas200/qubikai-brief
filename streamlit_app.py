import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import os
import datetime

# ==========================================
# 1. APP INSTELLINGEN (Jouw Huisstijl) 🎨
# ==========================================
APP_TITLE = "Snap-mijn-Brief"
APP_ICON = "📩"
APP_PRIMARY_COLOR = "#FF4B4B"  # Rood accent
APP_BG_COLOR = "#0E1117"       # Donkere achtergrond
APP_TEXT_COLOR = "#FAFAFA"     # Witte tekst

# ==========================================
# 2. CONFIGURATIE & CSS 🛠️
# ==========================================
st.set_page_config(page_title=f"Qubikai - {APP_TITLE}", page_icon=APP_ICON, layout="centered")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    /* Algemene Stijl */
    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
    }}
    .stApp {{
        background-color: {APP_BG_COLOR};
        color: {APP_TEXT_COLOR};
    }}
    
    /* Navigatie Balk */
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
        border-left: 6px solid {APP_PRIMARY_COLOR};
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* Knoppen */
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
    }}
    .stButton > button:hover {{
        background-color: {APP_PRIMARY_COLOR};
        color: white;
        transform: translateY(-2px);
    }}
    
    /* Resultaat Kaarten */
    .result-box {{
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {APP_PRIMARY_COLOR};
        margin-top: 20px;
    }}

    /* Geschiedenis Kaarten */
    .history-card {{
        background-color: #1F2937;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 4px solid {APP_PRIMARY_COLOR};
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SETUP & GEHEUGEN 🧠
# ==========================================

# Sessie status initialiseren (zodat hij onthoudt waar je bent)
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
    st.error("⚠️ CRITICAAL: Geen API Key gevonden in Secrets!")
    st.stop()

# ==========================================
# 4. HULPFUNCTIES
# ==========================================

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

# --- DE INTELLIGENTIE (Prompt) ---
def get_agent_prompt():
    return """
    Jij bent de Post-Expert van Qubikai.
    Bekijk de afbeelding. Geef antwoord in strak Markdown format.
    
    Output structuur:
    # [Bedenk een korte, duidelijke titel]
    
    ### 🚨 Actie & Urgentie
    * **Urgentie:** [HOOG/MIDDEN/LAAG]
    * **Deadline:** [Datum of "Geen datum"]
    * **Kosten:** [Bedrag of "Geen"]
    
    ### 📄 Wat is dit?
    [Eén duidelijke zin uitleg in jip-en-janneke taal]
    
    ### 💡 Qubikai Advies
    [Jouw concrete advies: Wat is de slimste volgende stap?]
    """

# ==========================================
# 5. DE INTERFACE (De Schermen) 📱
# ==========================================

# --- HEADER (Altijd zichtbaar) ---
c1, c2, c3 = st.columns([1, 5, 1])
with c1:
    if st.button("🏠", help="Terug naar Home"):
        nav_to("home")
with c2:
    st.markdown(f"<div class='nav-bar'>{APP_TITLE}</div>", unsafe_allow_html=True)
with c3:
    if len(st.session_state.history) > 0:
        if st.button("📂", help="Geschiedenis"):
            nav_to("history")

# --- SCHERM 1: HOME (Met Uitleg) ---
if st.session_state.step == "home":
    # Logo check
    if os.path.exists("logo.png"):
        c_l, c_r = st.columns([1, 4])
        with c_l: st.image("logo.png", width=80)
        with c_r: st.markdown("## Geen paniek over post.")
    else:
        st.markdown("<h2 style='text-align: center;'>Geen paniek over post. 📮</h2>", unsafe_allow_html=True)
        
    st.write("<div style='text-align: center; color: #ccc; margin-bottom: 20px;'>Ik vertaal ambtelijke taal naar actiepunten.</div>", unsafe_allow_html=True)

    # De "Hoe werkt het?" Gids (Strakke UX)
    with st.expander("ℹ️ Hoe werkt deze app?", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 1. Upload")
            st.caption("Maak een foto van je brief.")
        with c2:
            st.markdown("#### 2. Analyse")
            st.caption("Ik zoek datums en bedragen.")
        with c3:
            st.markdown("#### 3. Advies")
            st.caption("Jij krijgt een stappenplan.")

    st.markdown("<br>", unsafe_allow_html=True)

    # De Grote Actieknop
    c_left, c_btn, c_right = st.columns([1, 2, 1])
    with c_btn:
        if st.button("📸  SCAN MIJN BRIEF NU", type="primary"):
            nav_to("upload")
            
    st.markdown("<br><div style='text-align: center; font-size: 0.8em; color: #666;'>Veilig & Privé • Geen opslag van data</div>", unsafe_allow_html=True)

# --- SCHERM 2: UPLOAD ---
elif st.session_state.step == "upload":
    st.markdown("### 1. Maak foto of kies bestand")
    
    uploaded_file = st.file_uploader("Kies bestand", label_visibility="collapsed")
    
    if uploaded_file:
        st.session_state.current_image = uploaded_file
        nav_to("processing")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 Terug"):
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
            
            # Titel uit het antwoord vissen voor geschiedenis
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
    # 2 kolommen: Links foto, rechts tekst
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
        st.button("📅 Zet in Agenda")
    with col_b:
        st.button("✉️ Delen / Mailen")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📸 Volgende Scannen"):
        nav_to("upload")

# --- SCHERM 5: GESCHIEDENIS ---
elif st.session_state.step == "history":
    st.markdown("### 📂 Mijn Scans")
    
    if not st.session_state.history:
        st.info("Nog geen scans gemaakt in deze sessie.")
    
    for item in reversed(st.session_state.history):
        st.markdown(f"""
        <div class="history-card">
            <div style="display:flex; justify-content:space-between; color:#888; font-size:0.8em;">
                <span>{item['time']}</span>
                <span>Gescand</span>
            </div>
            <div style="font-weight:700; font-size:1.1em; margin: 5px 0;">{item['title']}</div>
            <details>
                <summary>Bekijk advies</summary>
                <div style="margin-top: 10px; color: #ddd; font-size: 0.95em;">
                    {item['advice']}
                </div>
            </details>
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("🔙 Terug naar Home"):
        nav_to("home")