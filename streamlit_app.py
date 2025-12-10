import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. SETUP
st.set_page_config(page_title="Qubikai - Snap Brief Pro", page_icon="📩")

# Styling (Rood/Oranje voor Admin)
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        padding: 15px;
        border-radius: 10px;
        border: none;
    }
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 2. CONFIGURATIE (Google Key)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⚠️ Zet je GOOGLE_API_KEY in de Secrets!")
    st.stop()

# Model kiezen (Flash is snel en goedkoop)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. INTERFACE
st.title("📩 Snap-mijn-Brief")
st.write("Upload je brief. Qubikai analyseert hem direct.")

uploaded_file = st.file_uploader("Kies foto of PDF", type=['jpg', 'jpeg', 'png'])

# 4. LOGICA
def analyze_image(img):
    prompt = """
    Jij bent de brief-expert van Qubikai. Analyseer deze afbeelding.
    Geef antwoord in dit format:
    1. **WAT IS DIT?** (1 zin)
    2. **ACTIE NODIG?** (Ja/Nee + Deadline)
    3. **SAMENVATTING** (Belangrijkste punten)
    4. **ADVIES** (Wat moet ik doen?)
    """
    response = model.generate_content([prompt, img])
    return response.text

# 5. ACTIE
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Jouw bestand', use_column_width=True)
    
    if st.button('🚀 Analyseer Brief'):
        with st.spinner('Bezig met lezen...'):
            try:
                resultaat = analyze_image(image)
                st.success("Klaar!")
                st.markdown(resultaat)
            except Exception as e:
                st.error(f"Foutmelding: {e}")