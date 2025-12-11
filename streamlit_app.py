import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io

# 1. SETUP
st.set_page_config(page_title="Qubikai Brief", page_icon="📩")

# --- DE COLOR FIX ---
# Hier dwingen we ZWART lettertype af op de WITTE achtergrond
st.markdown("""
<style>
    /* Forceer de hele app naar wit met donkere tekst */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Zorg dat alle tekst (paragrafen, koppen, lijstjes) donkergrijs zijn */
    p, h1, h2, h3, h4, h5, h6, li, span, div, label {
        color: #111827 !important;
    }
    
    /* Zorg dat de spinner ook zichtbaar is */
    div.stSpinner > div {
        border-top-color: #4B0082 !important;
    }
    
    /* Knoppen styling */
    div.stButton > button {
        background-color: #FF4B4B !important; 
        color: white !important; 
        border: none;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 2. CONFIGURATIE
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Systeemfout: API Key ontbreekt. Check de settings.")
    st.stop()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# 3. INTERFACE
st.title("📩 Snap-mijn-Brief")
st.write("Brief van de overheid of een ingewikkelde rekening? Upload hem hieronder. Ik vertel je in gewone mensentaal wat je moet doen.")

uploaded_file = st.file_uploader("Maak een foto of kies een bestand", type=['jpg', 'jpeg', 'png'])

# 4. INTELLIGENTIE
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=300, caption="Jouw document")
    
    st.markdown("---")
    
    with st.spinner('🔍 Brief lezen en kleine lettertjes checken...'):
        try:
            base64_image = encode_image(image)
            
            # --- JOUW AGENT SCRIPT ---
            prompt_text = """
            Jij bent de bureaucratie-expert van Qubikai. Je helpt mensen die post niet snappen.
            Analyseer de afbeelding grondig (zoek naar datums, bedragen, afzenders en juridische taal).
            
            Geef je antwoord EXACT in dit format (gebruik Markdown):
            
            ### 📄 1. Wat is dit?
            (Eén zin in simpele taal. Bijvoorbeeld: "Dit is een verkeersboete voor te hard rijden.")
            
            ### 🚨 2. Moet ik iets doen?
            * **Actie:** [JA / NEE]
            * **Urgentie:** [HOOG / GEMIDDELD / LAAG]
            * **Deadline:** [Datum indien gevonden, anders "Geen harde datum"]
            
            ### 💶 3. Kosten?
            (Staat er een bedrag? Zo ja: Hoeveel? Zo nee: "Geen kosten")
            
            ### 📝 4. Samenvatting
            (De 3 belangrijkste punten in bulletpoints)
            
            ### 💡 5. Qubikai Advies
            (Een vriendelijk, praktisch advies: "Betaal voor vrijdag via iDeal" of "Bewaar dit in je map".)
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
                max_tokens=600,
            )
            
            full_response = response.choices[0].message.content
            
            # Succes melding (ook styling force)
            st.success("✅ Analyse voltooid!")
            
            # Resultaat tonen
            st.markdown(full_response)

        except Exception as e:
            st.error("Oeps, er ging iets mis bij de verwerking.")
            st.info(f"Technische melding: {e}")