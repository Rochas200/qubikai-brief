import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. SETUP
st.set_page_config(page_title="Qubikai Brief", page_icon="📩")

# Styling
st.markdown("""
<style>
    .stApp {background-color: #FFFFFF;} 
    div.stButton > button {background-color: #FF4B4B; color: white; width: 100%;}
</style>
""", unsafe_allow_html=True)

# 2. CONFIGURATIE (De Veiligheidscheck)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⚠️ Zet je GOOGLE_API_KEY in de Secrets!")
    st.stop()

# 3. HET MODEL (De Veilige Keuze) 🛡️
# We gebruiken 'gemini-pro' (1.0). Die werkt altijd.
model = genai.GenerativeModel('models/gemini-pro')

# 4. DE LOGICA (Jouw Agent)
def analyze_image(img):
    # --- PLAK HIERONDER JOUW AI STUDIO PROMPT ---
    prompt = """
    Jij bent de brief-expert van Qubikai. Analyseer deze afbeelding.
    Geef antwoord in dit format:
    
    1. **WAT IS DIT?** (1 zin, jip-en-janneke taal)
    2. **ACTIE NODIG?** (JA/NEE + Deadline)
    3. **SAMENVATTING** (De 3 belangrijkste punten)
    4. **ADVIES** (Stap voor stap wat ik nu moet doen)
    """
    # --------------------------------------------
    
    response = model.generate_content([prompt, img])
    return response.text

# 5. DE INTERFACE
st.title("📩 Snap-mijn-Brief")
st.write("Upload je brief. Ik vertel je direct wat je moet doen.")

uploaded_file = st.file_uploader("Kies foto of PDF", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=300)
    
    with st.spinner('Bezig met lezen...'):
        try:
            resultaat = analyze_image(image)
            st.success("Klaar!")
            st.markdown(resultaat)
        except Exception as e:
            st.error("Er ging iets mis.")
            st.code(e)