import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import os

# 1. PAGE CONFIG (Breedbeeld & Titel)
st.set_page_config(
    page_title="Qubikai Brief Assistant",
    page_icon="📩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. STYLING (De 'Pro' Look)
st.markdown("""
<style>
    /* Hoofdachtergrond */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Knoppen */
    div.stButton > button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        border: none;
        width: 100%;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #D93838;
    }
    
    /* Resultaat Blokken */
    .result-card {
        background-color: #1F2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. SETUP
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Geen API Key gevonden. Check je Secrets.")
    st.stop()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- 4. DE LAYOUT ---

with st.sidebar:
    # --- LOGO CHECK ---
    # Hij kijkt of 'logo.png' bestaat. Zo ja, laat hij hem zien.
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)
    else:
        # Geen logo? Dan tekst.
        st.header("Qubikai 📩")

    st.markdown("---")
    st.markdown("### 1. Upload Document")
    uploaded_file = st.file_uploader("Sleep bestand of kies foto", type=['jpg', 'jpeg', 'png'])
    
    st.info("💡 Tip: Zorg voor goed licht als je een foto maakt.")
    
    st.markdown("---")
    st.caption("🔒 Qubikai Privacy: Je data wordt niet opgeslagen.")

# --- HOOFDSCHERM ---

if not uploaded_file:
    # Welkomstscherm
    st.title("Welkom bij Snap-mijn-Brief 👋")
    st.markdown("""
    Geen stress meer over post. 
    Upload je brief in de zijbalk (links) en ik vertel je direct:
    
    * 📄 Wat het is
    * 🚨 Of er haast bij is
    * 💶 Wat het kost
    """)

if uploaded_file:
    # Indeling: 2 kolommen
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Jouw Bestand")
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
    
    with col2:
        st.subheader("🕵️‍♂️ Analyse")
        
        with st.spinner('Kleine lettertjes lezen...'):
            try:
                base64_image = encode_image(image)
                
                # De Agent
                prompt_text = """
                Je bent de Qubikai Post-Expert.
                Scan dit document en geef output in Markdown.
                
                Ik wil 4 duidelijke blokken:
                ### 📄 1. Wat is dit?
                (Korte titel/zin)
                
                ### 🚨 2. Actie & Deadline
                * **Actie:** [JA/NEE] - [Wat?]
                * **Deadline:** [Datum]
                
                ### 💶 3. Kosten
                (Bedrag of "Geen")
                
                ### 💡 4. Advies
                (Jip-en-janneke uitleg wat ik moet doen)
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=500,
                )
                
                result = response.choices[0].message.content
                
                # Toon resultaat in mooie kaart
                st.markdown(f'<div class="result-card">{result}</div>', unsafe_allow_html=True)
                
                # Dummy knoppen
                b1, b2 = st.columns(2)
                with b1:
                    st.button("📅 Zet in Agenda")
                with b2:
                    st.button("📧 Delen")
                
            except Exception as e:
                st.error("Er ging iets mis.")
                st.code(e)