import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- DE QUBIKAI STANDAARD TEMPLATE v1.0 ---

# 1. CONFIGURATIE & SETUP
st.set_page_config(page_title="Qubikai App", page_icon="🚀")

# Probeer de sleutel op te halen
try:
    # Zorg dat in je Secrets exact staat: GOOGLE_API_KEY = "..."
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("⚠️ Fout: Geen API Key gevonden. Check je Secrets!")
    st.stop()

# 2. HET BREIN (Hier pas je de Prompt aan!) 🧠
def get_ai_response(image_input):
    # Dit model is razendsnel en goedkoop
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # --- PLAK HIERONDER JOUW AI STUDIO PROMPT ---
    system_prompt = """
    Jij bent een expert. Bekijk de afbeelding en doe het volgende:
    1. Wat is dit voor document?
    2. Welke actie moet de gebruiker ondernemen?
    3. Geef een korte samenvatting.
    
    Geef antwoord in helder Nederlands.
    """
    # --------------------------------------------
    
    response = model.generate_content([system_prompt, image_input])
    return response.text

# 3. DE INTERFACE (Het Lichaam) 📱
st.markdown("""
<style>
    .stApp {background-color: #FFFFFF;} 
    div.stButton > button {background-color: #4B0082; color: white; width: 100%;}
</style>
""", unsafe_allow_html=True)

st.title("Admin Assistant")
st.write("Upload een foto. Krijg direct advies.")

uploaded_file = st.file_uploader("Kies een bestand...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Toon foto
    image = Image.open(uploaded_file)
    st.image(image, width=300)
    
    # Draai de AI
    with st.spinner('Thinking...'):
        try:
            resultaat = get_ai_response(image)
            st.success("Klaar!")
            st.markdown(resultaat)
        except Exception as e:
            st.error(f"Er ging iets mis: {e}")