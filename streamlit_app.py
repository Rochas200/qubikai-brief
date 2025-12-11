import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. SETUP
st.set_page_config(page_title="Qubikai - Snap Brief", page_icon="📩")

# Styling: Strak & Modern (Past bij je site)
st.markdown("""
<style>
    .stApp {background-color: #FFFFFF;}
    div.stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 2. CONFIGURATIE
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⚠️ Zet je GOOGLE_API_KEY in de Secrets!")
    st.stop()

# KIES JE MODEL (Precies zoals in jouw lijstje!)
# We pakken Flash voor snelheid. Wil je slimmer? Verander in 'models/gemini-1.5-pro-latest'
model = genai.GenerativeModel('models/gemini-pro')

# 3. INTERFACE
st.title("📩 Snap-mijn-Brief")
st.write("Maak een foto van je brief. Ik vertel je direct wat je moet doen.")

# Camera input voor mobiel gemak (of upload)
uploaded_file = st.file_uploader("Kies foto of PDF", type=['jpg', 'jpeg', 'png'])

# 4. LOGICA
def analyze_image(img):
    prompt = """
    Jij bent de brief-expert van Qubikai. Analyseer deze afbeelding.
    Geef antwoord in dit format:
    
    1. **WAT IS DIT?** (1 zin, jip-en-janneke taal)
    2. **ACTIE NODIG?** (JA/NEE + Deadline)
    3. **SAMENVATTING** (De 3 belangrijkste punten)
    4. **ADVIES** (Stap voor stap wat ik nu moet doen)
    
    Wees kort en direct.
    """
    response = model.generate_content([prompt, img])
    return response.text

# 5. AUTO-PILOT ACTIE (Geen knop meer nodig!)
if uploaded_file is not None:
    # Toon de foto klein
    image = Image.open(uploaded_file)
    st.image(image, caption='Jouw bestand', width=200)
    
    # Direct starten
    with st.spinner('✨ Gemini is aan het lezen...'):
        try:
            resultaat = analyze_image(image)
            st.success("Analyse klaar!")
            st.markdown("---")
            st.markdown(resultaat)
            
        except Exception as e:
            st.error("Oeps! Er ging iets mis.")
            st.write(f"Technische fout: {e}")