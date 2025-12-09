import streamlit as st
import base64
from openai import OpenAI

# 1. Configuratie van de pagina
st.set_page_config(page_title="Qubikai - Snap-mijn-Brief", page_icon="📩")

# Verberg standaard Streamlit menuutjes voor strakke look
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
# --- STYLING START ---
st.markdown("""
<style>
    /* 1. Haal de standaard Streamlit balken weg */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. Achtergrond en spatiëring strak trekken */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 3. De upload knop (Drag & Drop vak) */
    [data-testid='stFileUploader'] {
        width: 100%;
        margin-bottom: 20px;
    }

    /* 4. De Actie-knop (Groot en Oranje/Rood) */
    div.stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-size: 20px;
        font-weight: 700;
        padding: 15px 0px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    
    /* Hover effect (als je muis erop staat) */
    div.stButton > button:hover {
        background-color: #D43F3F;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.2);
        color: white;
    }

    /* 5. Resultaat vakken mooier maken */
    div[data-testid="stMarkdownContainer"] h3 {
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)
# --- STYLING END ---

# 2. Titel en Intro
st.title("📩 Snap-mijn-Brief")
st.write("Maak een foto van je brief. Wij vertellen je binnen 10 seconden wat je moet doen.")

# 3. API Key ophalen (veilig via Secrets, leg ik zo uit)
# Voor nu kun je hem even testen door hem hier in te vullen, maar voor livegang gebruiken we secrets.
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)
# 4. De Upload Knop
uploaded_file = st.file_uploader("Upload hier je brief (Foto of PDF)", type=['png', 'jpg', 'jpeg'])

def analyze_image(image_bytes):
    # Dit is de functie die praat met het slimme brein (GPT-4o)
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Jij bent de Qubikai brief-assistent. Analyseer de afbeelding. Geef output in dit format: \n1. URGENTIE (Rood/Oranje/Groen)\n2. SAMENVATTING (Jip en Janneke taal)\n3. ACTIE (Wat moet ik doen?)\n4. DEADLINE."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Wat staat er in deze brief en wat moet ik doen?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ],
            }
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

# 5. De Actie
if uploaded_file is not None:
    st.image(uploaded_file, caption='Jouw brief', use_column_width=True)
    
    if st.button('🚀 Analyseer mijn Brief'):
        with st.spinner('Qubikai leest nu met je mee...'):
            try:
                # Lees de bytes van de file
                bytes_data = uploaded_file.getvalue()
                resultaat = analyze_image(bytes_data)
                
                st.success("Analyse compleet!")
                st.markdown("### Het Qubikai Oordeel:")
                st.markdown(resultaat)
                
                st.info("💡 Tip: Wil je dat Qubikai dit onthoudt? Maak dan binnenkort een account aan.")
                
            except Exception as e:
                st.error(f"Er ging iets mis: {e}")