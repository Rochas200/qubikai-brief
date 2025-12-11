import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import os
import datetime

# ==========================================
# 1. CONFIGURATIE & STYLING (Het Chassis) 🏎️
# ==========================================
st.set_page_config(page_title="Qubikai Brief", page_icon="📩", layout="centered")

st.markdown("""
<style>
    /* Dark Mode Basis */
    .stApp {background-color: #0E1117; color: #FAFAFA;}
    
    /* Navigatie Balk */
    .nav-bar {
        padding: 15px;
        background-color: #161B22;
        border-bottom: 1px solid #30363D;
        margin-bottom: 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2em;
        border-left: 5px solid #FF4B4B; /* Qubikai Rood Accent */
    }
    
    /* Resultaat Kaarten */
    .history-card {
        background-color: #1F2937;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #FF4B4B;
    }
    
    /* Knoppen */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1rem;
        background-color: #21262d;
        color: white;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #FF4B4B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GEHEUGEN & VERBINDING 🧠
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

# ==========================================
# 3. HULPFUNCTIES 🛠️
# ==========================================

def nav_to(step_name):
    st.session_state.step = step_name
    st.rerun()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def add_to_history(title, advice):
    timestamp = datetime.datetime.now().strftime("%H:%M")
    st.session_state.history.append({"time": timestamp, "title": title, "advice": advice})

# --- DE MOTOR (HIER ZIT DE INTELLIGENTIE) ---
def get_agent_prompt():
    """
    Dit is de specifieke instructie voor de BRIEF APP.
    Voor VerfBuddy veranderen we alleen dit stukje tekst.
    """
    return """
    Jij bent de Post-Expert van Qubikai.
    Bekijk de afbeelding. Geef antwoord in strak Markdown format.
    
    Output structuur:
    # [Bedenk een korte titel van 3 woorden]
    
    ### 📄 Wat is dit?
    [Eén zin uitleg in jip-en-janneke taal]
    
    ### 🚨 Actie & Deadline
    * **Urgentie:** [HOOG/MIDDEN/LAAG]
    * **Deadline:** [Datum of "Geen datum"]
    * **Te betalen:** [Bedrag of "Niets"]
    
    ### 💡 Qubikai Advies
    [Concreet advies: Betalen, Bewaren, of Bezwaar maken?]
    """

# ==========================================
# 4. DE INTERFACE (De Schermen) 📱
# ==========================================

# --- BOVENBALK ---
c1, c2, c3 = st.columns([1, 5, 1])
with c1:
    if st.button("🏠"):
        nav_to("home")
with c2:
    st.markdown("<div class='nav-bar'>Snap-mijn-Brief</div>", unsafe_allow_html=True)
with c3:
    if len(st.session_state.history) > 0:
        if st.button("📂"):
            nav_to("history")

# --- SCHERM 1: HOME ---
if st.session_state.step == "home":
    st.write("### Welkom 👋")
    st.write("Heb je een ingewikkelde brief of boete?")
    st.info("Upload hem hieronder, dan zoek ik uit wat je moet doen.")
    
    st.markdown("---")
    
    # Grote opvallende startknop
    c_start, _ = st.columns([1, 0.1])
    with c_start:
        if st.button("📸  Start Nieuwe Scan"):
            nav_to("upload")

# --- SCHERM 2: UPLOAD ---
elif st.session_state.step == "upload":
    st.markdown("### Foto maken of uploaden")
    
    uploaded_file = st.file_uploader("Kies bestand", label_visibility="collapsed")
    
    if uploaded_file:
        st.session_state.current_image = uploaded_file
        nav_to("processing")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 Terug"):
        nav_to("home")

# --- SCHERM 3: PROCESSING (AI aan het werk) ---
elif st.session_state.step == "processing":
    # Leuke laad-animatie
    with st.spinner('🕵️‍♂️ De kleine lettertjes lezen...'):
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
            
            # Slimme titel extractie voor geschiedenis
            first_line = result_text.split('\n')[0].replace('#', '').strip()
            add_to_history(first_line, result_text)
            
            nav_to("result")
            
        except Exception as e:
            st.error(f"Fout: {e}")
            if st.button("Opnieuw proberen"):
                nav_to("upload")

# --- SCHERM 4: RESULTAAT ---
elif st.session_state.step == "result":
    # Toon foto klein links
    img = Image.open(st.session_state.current_image)
    st.image(img, width=150)
    
    st.markdown("---")
    # Het advies in een mooi kader
    st.markdown(st.session_state.current_result)
    st.markdown("---")
    
    st.write("### Wat wil je doen?")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.button("📅 In Agenda (Demo)")
    with col_b:
        st.button("✉️ Delen (Demo)")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📸 Volgende Brief Scannen"):
        nav_to("upload")

# --- SCHERM 5: GESCHIEDENIS ---
elif st.session_state.step == "history":
    st.markdown("### 📂 Eerder gescand")
    
    for item in reversed(st.session_state.history):
        st.markdown(f"""
        <div class="history-card">
            <small style="color: #888">{item['time']}</small><br>
            <strong>{item['title']}</strong>
            <details>
                <summary style="cursor: pointer; color: #FF4B4B;">Bekijk advies</summary>
                <div style="margin-top: 10px; color: #ccc;">{item['advice']}</div>
            </details>
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("🔙 Terug naar Home"):
        nav_to("home")