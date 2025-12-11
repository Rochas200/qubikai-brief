import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io

# 1. SETUP & CONFIGURATIE ⚙️
st.set_page_config(page_title="Qubikai Brief", page_icon="📩", layout="centered")

# --- DE DARK MODE STYLING ---
# We maken een strakke, donkere interface.
st.markdown("""
<style>
    /* 1. De Hoofdachtergrond: Donker (Qubikai Dark) */
    .stApp {
        background-color: #111827 !important;
        color: #FFFFFF !important;
    }
    
    /* 2. Alle tekst wit maken */
    p, h1, h2, h3, h4, h5, h6, li, span, div, label {
        color: #FFFFFF !important;
    }
    
    /* 3. De Upload Box mooi maken (zodat tekst leesbaar is) */
    div[data-testid="stFileUploader"] {
        background-color: #1F2937;
        padding: 20px;
        border-radius: 12px;
        border: 1px dashed #4B0082;
    }
    
    /* 4. De Knoppen (Rood accent) */
    div.stButton > button {
        background-color: #FF4B4B !important; 
        color: white !important;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    /* 5. De Spinner (Laden) */
    div.stSpinner > div {
        border-top-color: #FF4B4B !important;
    }
    
    /* 6. Success meldingen stylen */
    div.stAlert {
        background-color: #1F2937 !important;
        color: white !important;
        border: 1px solid #059669;
    }
</style>
""", unsafe_allow_html=True)

# 2. OPENAI VERBINDING 🔌
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Setup Fout: Geen API Key gevonden.")
    st.stop()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# 3. DE INTERFACE (Voorkant) 📱
st.title("📩 Snap-mijn-Brief")
st.write("Upload een foto van je brief. Ik analyseer hem direct.")

# Upload vak
uploaded_file = st.file_uploader("Kies foto of maak een nieuwe", type=['jpg', 'jpeg', 'png'])

# 4. DE INTELLIGENTIE (Agent) 🧠
if uploaded_file:
    # Toon de foto
    image = Image.open(uploaded_file)
    st.image(image, caption="Jouw upload", width=300)
    
    st.markdown("---")
    
    with st.spinner('🚀 Bezig met analyseren...'):
        try:
            base64_image = encode_image(image)
            
            # De Qubikai Agent Prompt
            prompt_text = """
            Jij bent de bureaucratie-expert van Qubikai.
            Bekijk de afbeelding en geef antwoord in dit exacte format (gebruik Markdown):
            
            ### 📄 1. Wat is dit?
            (Eén duidelijke zin)
            
            ### 🚨 2. Actie & Deadline
            * **Actie nodig:** [JA / NEE]
            * **Urgentie:** [HOOG / GEMIDDELD / LAAG]
            * **Deadline:** [Datum of "Geen datum"]
            
            ### 💶 3. Kosten
            (Bedrag of "Geen kosten")
            
            ### 💡 4. Qubikai Advies
            (Kort, praktisch advies wat ik nu moet doen)
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
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ],
                    }
                ],
                max_tokens=500,
            )
            
            full_response = response.choices[0].message.content
            
            # Resultaat tonen
            st.success("Analyse voltooid!")
            st.markdown(full_response)

        except Exception as e:
            st.error("Oeps, er ging iets mis.")
            st.info(f"Foutmelding: {e}")