import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io

# 1. SETUP
st.set_page_config(page_title="Qubikai Brief", page_icon="📩")

# Styling
st.markdown("""
<style>
    .stApp {background-color: #FFFFFF;} 
    div.stButton > button {background-color: #FF4B4B; color: white; width: 100%; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# 2. CONFIGURATIE
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Zet je OPENAI_API_KEY in de Secrets!")
    st.stop()

# Hulpfunctie: Afbeelding omzetten naar tekst voor OpenAI
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# 3. INTERFACE
st.title("📩 Snap-mijn-Brief")
st.write("Upload je brief. Direct advies.")

uploaded_file = st.file_uploader("Maak een foto of kies bestand", type=['jpg', 'jpeg', 'png'])

# 4. DE LOGICA (OpenAI GPT-4o-mini)
if uploaded_file:
    # Toon plaatje
    image = Image.open(uploaded_file)
    st.image(image, width=300)
    
    # Direct starten
    with st.spinner('Analyseren...'):
        try:
            # Codeer plaatje
            base64_image = encode_image(image)
            
            # De Prompt (Jouw Agent)
            prompt_text = """
            Jij bent de brief-expert van Qubikai. Analyseer deze afbeelding.
            Geef antwoord in dit format:
            1. **WAT IS DIT?** (1 zin)
            2. **ACTIE NODIG?** (JA/NEE + Deadline)
            3. **SAMENVATTING** (Kort)
            4. **ADVIES** (Wat moet ik doen?)
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Dit is het snelle, goedkope model!
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ],
                    }
                ],
                max_tokens=500,
            )
            
            # Resultaat tonen
            st.success("Klaar!")
            st.markdown(response.choices[0].message.content)

        except Exception as e:
            st.error("Er ging iets mis met OpenAI:")
            st.code(e)