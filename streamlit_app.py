import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io

# 1. SETUP
st.set_page_config(page_title="Qubikai Debug", page_icon="🐞")

# Styling
st.markdown("""
<style>
    .stApp {background-color: #FFFFFF;} 
    div.stButton > button {background-color: #FF4B4B; color: white; width: 100%; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# 2. CONFIGURATIE CHECK
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ CRITICAAL: Geen OPENAI_API_KEY in Secrets gevonden!")
    st.stop()

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"⚠️ Fout bij starten OpenAI client: {e}")
    st.stop()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# 3. INTERFACE
st.title("🐞 Brief App (Debug Modus)")
st.warning("Deze versie laat ruwe data zien om de fout te vinden.")

uploaded_file = st.file_uploader("Kies bestand", type=['jpg', 'jpeg', 'png'])

# 4. DE LOGICA
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=250, caption="Jouw upload")
    
    with st.spinner('OpenAI aanroepen...'):
        try:
            base64_image = encode_image(image)
            
            # Simpele test prompt om zeker te weten dat hij reageert
            prompt_text = "Beschrijf heel kort wat je op deze afbeelding ziet. Als je niets ziet, zeg dat dan."

            response = client.chat.completions.create(
                model="gpt-4o-mini",
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
                max_tokens=300,
            )
            
            # --- DEBUG INFO ---
            full_response = response.choices[0].message.content
            
            if not full_response:
                st.error("❌ OpenAI stuurde een LEEG antwoord terug!")
                st.write("Ruwe response object:", response)
            else:
                st.success("✅ Antwoord ontvangen!")
                st.markdown("### Het resultaat:")
                st.info(full_response)
                
        except Exception as e:
            st.error("❌ CRASH tijdens aanroep:")
            st.code(e)