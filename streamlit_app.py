import streamlit as st
import google.generativeai as genai

st.title("🕵️‍♂️ De Model-Detective")

# 1. Configureer met je sleutel
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("Sleutel niet gevonden in Secrets!")
    st.stop()

# 2. Vraag Google om de lijst
st.write("Ik vraag nu aan Google welke modellen beschikbaar zijn voor jouw sleutel...")

try:
    # We vragen de lijst op
    model_list = genai.list_models()
    
    found_any = False
    for m in model_list:
        # We laten alleen modellen zien die content kunnen genereren (zoals Gemini)
        if 'generateContent' in m.supported_generation_methods:
            st.success(f"✅ Gevonden: **{m.name}**")
            found_any = True
            
    if not found_any:
        st.warning("⚠️ Google reageert wel, maar geeft geen modellen terug. Check je API Key rechten!")
        
except Exception as e:
    st.error(f"❌ Fout bij verbinden: {e}")