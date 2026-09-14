import os
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# 1. SETUP & GEMINI API CONFIGURATION
api_key = "AQ.Ab8RN6JrU1wxH09quj0Myb6R9QV9gO0GXlowy3pGdHBX0PUX9g"

if api_key:
    genai.configure(api_key=api_key)

# 2. VOICE SYNTHESIS HELPER & ANIMATED AVATAR WITH BUTTON PLAY
def clean_text_for_speech(text):
    cleaned = text.replace("$", " ")
    cleaned = cleaned.replace("->", " yields ")
    cleaned = cleaned.replace("+", " plus ")
    cleaned = cleaned.replace("=", " equals ")
    cleaned = cleaned.replace("²", " squared ")
    cleaned = cleaned.replace("³", " cubed ")
    return " ".join(cleaned.split())

def speak_text(text):
    speech_ready_text = clean_text_for_speech(text)
    clean_text = speech_ready_text.replace("'", "\\'").replace("\n", " ")
    js_code = f"""
    <div style="background: #1e1e2f; padding: 15px; border-radius: 12px; border: 2px solid #4f46e5; font-family: sans-serif; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 35px;">🤖</div>
            <div>
                <h4 style="margin: 0; color: #a5b4fc;">Johnny Audio Ready</h4>
                <p style="margin: 3px 0 0 0; color: #9ca3af; font-size: 13px;">Click play to hear explanation</p>
            </div>
        </div>
        <button onclick="playSpeech()" style="background: #4f46e5; color: white; border: none; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 14px;">▶ Play Voice</button>
    </div>

    <script>
    function playSpeech() {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance('{clean_text}');
        msg.rate = 1.0;
        msg.pitch = 1.0;
        
        var voices = window.speechSynthesis.getVoices();
        var maleVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Microsoft') || v.name.includes('David')));
        if (maleVoice) msg.voice = maleVoice;

        window.speechSynthesis.speak(msg);
    }}
    </script>
    """
    components.html(js_code, height=90, width=800)

# 3. SESSION STATE INITIALIZATION
if "app_screen" not in st.session_state:
    st.session_state.app_screen = "intro"

if "presentation_step" not in st.session_state:
    st.session_state.presentation_step = 0

if "presentation_mode" not in st.session_state:
    st.session_state.presentation_mode = "long"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. PRESENTATION STEPS & PROMPTS
PRESENTATION_STEPS_LONG = {
    1: {
        "title": "PART 1 — Project Vision & Architecture",
        "icon": "🚀",
        "fallback": "We begin with our interdisciplinary IB Science Project developed by Mane Seyranyan, alongside the research team: Maya Quaye, Lovisa Sagwa, Ziv Keren Karras Levanon, and Ben Engel."
    },
    2: {
        "title": "PART 2 — The Food & Ingredients",
        "icon": "🥗",
        "fallback": "Our recipe features fresh homemade pasta layered with zucchini, bell peppers, spinach, tomatoes, garlic, onion, and homemade cheese, featuring vibrant red-orange and green aesthetics and savory aromas."
    },
    3: {
        "title": "PART 3 — Biology: Cellular Structure & Nutrition",
        "icon": "🧬",
        "fallback": "In Biology, managed by Maya, Lovisa, Ziv, and Ben, we examine GMO resilience, egg nutrition and cholesterol, milk complete proteins and calcium, salt fluid balance, plant fiber, and import logistics from Jordan and the Netherlands."
    },
    4: {
        "title": "PART 4 — Chemistry: Reactions & Transformations",
        "icon": "🧪",
        "fallback": "In Chemistry, managed by Lovisa and Ziv, we analyze gluten formation, starch gelatinization, protein denaturation, acid-induced casein coagulation for homemade cheese, Maillard browning in roasted vegetables, and allicin formation in garlic."
    },
    5: {
        "title": "PART 5 — Physics: Thermodynamics & Heat Transfer",
        "icon": "⚛️",
        "fallback": "In Physics, managed by Mane Seyranyan, we govern heat transfer via conduction and convection, sauce evaporation, energy relationships, and layered structural textures."
    },
    6: {
        "title": "PART 6 — Computer Science: AI Architecture",
        "icon": "💻",
        "fallback": "In Computer Science, built entirely by Mane Seyranyan, we power this interactive application using Python, Streamlit, and Gemini LLM."
    },
    7: {
        "title": "PART 7 — Presentation Conclusion",
        "icon": "🎓",
        "fallback": "That concludes our presentation! You can now ask me questions about our dish and the interdisciplinary science behind it."
    }
}

PRESENTATION_STEPS_SHORT = {
    1: {
        "title": "EXPRESS PITCH — Core Science & Architecture",
        "icon": "⚡",
        "fallback": "Welcome to our 3-minute overview of our vegetable lasagna project. Developed by Mane Seyranyan, who built this application alongside the research team—Maya, Lovisa, Ziv, and Ben—we integrated Biology, Chemistry, Physics, and Computer Science into one unified dish. From nutritional profiles and biochemical transformations to thermodynamic heat transfer and Python code, this project bridges culinary arts with rigorous science."
    },
    2: {
        "title": "EXPRESS PITCH — Conclusion & Q&A",
        "icon": "🎓",
        "fallback": "That wraps up our quick express pitch! We combined teamwork, coding, and experimental science to bring this lasagna to life. You are now welcome to ask any questions about the science behind our project."
    }
}

SLIDE_PROMPTS_LONG = {
    1: "Provide an engaging opening for the IB Science Project presentation about homemade vegetable lasagna. Explicitly credit the team and roles: Mane Seyranyan (Computer Science & Physics), Maya Quaye (Biology), Lovisa Sagwa (Biology & Chemistry), Ziv Keren Karras Levanon (Biology), and Ben Engel (Biology). DO NOT introduce yourself as Johnny or mention your name.",
    2: "Explain the food science, ingredient profile (flour, eggs, tomatoes, zucchini, peppers, spinach, garlic, onion, lemon, milk, spices), and physical properties of our fresh vegetable lasagna. DO NOT introduce yourself.",
    3: "Conduct a detailed biological analysis (led by Maya, Lovisa, Ziv, and Ben) covering GMO safety, egg nutrients, salt balance, milk proteins, and import supply chains. DO NOT introduce yourself.",
    4: "Conduct a detailed chemical analysis (led by Lovisa and Ziv) covering gluten formation, starch gelatinization, protein denaturation, casein coagulation, Maillard browning, and allicin formation. DO NOT introduce yourself.",
    5: "Conduct a detailed physical analysis (led by Mane Seyranyan) of thermodynamic heat transfer, sauce evaporation, thermal energy calculations, and final textures. DO NOT introduce yourself.",
    6: "Explain the computer science architecture (built by Mane Seyranyan) powering this project: Python, Streamlit, and Gemini LLM. DO NOT introduce yourself.",
    7: "Provide a concise conclusion summarizing this interdisciplinary IB Science Project. DO NOT introduce yourself."
}

SLIDE_PROMPTS_SHORT = {
    1: "Provide a fast, engaging 3-minute executive pitch of our IB Science Project on vegetable lasagna. Cover the team roles (Mane for CS/Physics, Maya, Lovisa, Ziv, Ben for Biology/Chemistry) and briefly touch upon how biology, chemistry, physics, and computer science come together. Keep it punchy and under 180 words. DO NOT introduce yourself.",
    2: "Provide a quick, punchy conclusion for our 3-minute express pitch, summarizing the core achievement and opening the floor to questions. DO NOT introduce yourself."
}

# ==========================================
# SCREEN 1: INTRO SCREEN
# ==========================================
if st.session_state.app_screen == "intro":
    st.set_page_config(page_title="Johnny — Welcome", page_icon="🤖", layout="centered")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #a5b4fc;'>🤖 Meet Johnny</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #9ca3af;'>Your AI Science Assistant for the IB Project</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    intro_text = (
        "Hello everyone! My name is Johnny, an autonomous AI science assistant "
        "developed specifically for this IB Science Project by Mane Seyranyan. "
        "I am here to guide you through our interdisciplinary research spanning "
        "Biology, Chemistry, Physics, and Computer Science. "
        "Click the button below to initialize my systems and enter the main application."
    )

    speak_text(intro_text)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 LAUNCH JOHNNY'S INTERFACE", type="primary", use_container_width=True):
            st.session_state.app_screen = "main"
            st.rerun()

# ==========================================
# SCREEN 2: MAIN INTERFACE
# ==========================================
else:
    st.set_page_config(page_title="Johnny — IB Science Assistant", page_icon="🤖", layout="wide")

    st.title("🤖 JOHNNY — AI SCIENCE ASSISTANT")
    st.caption("Created by Mane Seyranyan & Team | IB Science Project")
    st.markdown("---")

    st.subheader("📢 Stage 1: Official Project Presentation")

    col_mode1, col_mode2, col_reset = st.columns([1, 1, 1])

    with col_mode1:
        if st.button("⚡ Short Presentation (3 min)", type="secondary" if st.session_state.presentation_mode == "long" else "primary", use_container_width=True):
            st.session_state.presentation_mode = "short"
            st.session_state.presentation_step = 1
            st.rerun()

    with col_mode2:
        if st.button("🚀 Full Presentation (10+ min)", type="primary" if st.session_state.presentation_mode == "long" else "secondary", use_container_width=True):
            st.session_state.presentation_mode = "long"
            st.session_state.presentation_step = 1
            st.rerun()

    with col_reset:
        if st.button("🔄 Reset Presentation", use_container_width=True):
            st.session_state.presentation_step = 0
            st.rerun()

    current_steps_dict = PRESENTATION_STEPS_SHORT if st.session_state.presentation_mode == "short" else PRESENTATION_STEPS_LONG
    current_prompts_dict = SLIDE_PROMPTS_SHORT if st.session_state.presentation_mode == "short" else SLIDE_PROMPTS_LONG
    max_steps = len(current_steps_dict)

    if 0 < st.session_state.presentation_step <= max_steps:
        col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 2])
        with col_nav1:
            if st.session_state.presentation_step > 1:
                if st.button("⏮ Prev Slide", use_container_width=True):
                    st.session_state.presentation_step -= 1
                    st.rerun()
        with col_nav2:
            if st.session_state.presentation_step < max_steps:
                if st.button("⏩ Next Slide", use_container_width=True):
                    st.session_state.presentation_step += 1
                    st.rerun()

    current_step = st.session_state.presentation_step

    if 0 < current_step <= max_steps:
        step_data = current_steps_dict[current_step]
        st.info(f"**Mode: {'Short (3-min)' if st.session_state.presentation_mode == 'short' else 'Full (10-min)'} | Part {current_step} of {max_steps} — {step_data['icon']} {step_data['title']}**")
        
        cache_key = f"slide_content_{st.session_state.presentation_mode}_{current_step}"
        if cache_key not in st.session_state:
            with st.spinner("Johnny is researching and performing AI analysis for this section..."):
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt = (
                        "You are Johnny, the AI science assistant powered by Gemini. "
                        "ABSOLUTE CRITICAL RULE: DO NOT introduce yourself, DO NOT say your name, DO NOT say 'Hello' or use any greetings whatsoever. "
                        "Start your response immediately with the scientific facts. "
                        "Provide a thorough, scientifically rigorous explanation for: " + current_prompts_dict[current_step]
                    )

                    response = model.generate_content(prompt)
                    text_result = response.text
                    
                    # Жесткая очистка на случай, если модель все же попытается представиться
                    if "Johnny" in text_result[:50] or "Hello" in text_result[:30]:
                        parts = text_result.split('.')
                        text_result = '.'.join([p for p in parts if not ('Johnny' in p or 'hello' in p.lower())]).strip()
                    
                    st.session_state[cache_key] = text_result if text_result else step_data["fallback"]
                except Exception as e:
                    st.session_state[cache_key] = step_data["fallback"]

        ai_slide_text = st.session_state[cache_key]
        st.markdown("### 🤖 Johnny (AI-Generated):")
        st.write(ai_slide_text)
        speak_text(ai_slide_text)

    elif current_step > max_steps:
        st.success("✅ Presentation complete! You may now proceed to Stage 2 below.")

    st.markdown("---")

    st.subheader("💬 Stage 2: Interactive AI Q&A")

    user_question = st.text_input("Type your question for Johnny about the dish or the science behind it:")
    col_ask, col_clear = st.columns([1, 4])

    with col_ask:
        ask_btn = st.button("ASK JOHNNY", type="primary")

    with col_clear:
        if st.button("🧹 Clear History"):
            st.session_state.chat_history = []
            st.rerun()

    if ask_btn and user_question:
        if not api_key:
            st.error("Cannot answer: API Key is missing!")
        else:
            with st.spinner("Johnny is analyzing your question..."):
                system_prompt = (
                    "You are Johnny, an interactive AI science assistant powered by Gemini for an IB Science Project. "
                    "STRICT TEAM ROLES: "
                    "1. Mane Seyranyan built this entire AI application (Computer Science) and leads the Physics research (thermodynamics & heat transfer). "
                    "2. Maya Quaye, Ziv Keren Karras Levanon, and Ben Engel handle Biology (GMOs, eggs, salt, milk nutrients, import logistics). "
                    "3. Lovisa Sagwa handles Biology and Chemistry (gluten formation, starch gelatinization, protein denaturation, casein coagulation, Maillard reaction, allicin formation). "
                    "CRITICAL CONTEXT: The dish is a vegetable-based lasagna with fresh homemade pasta, zucchini, bell peppers, spinach, tomatoes, garlic, onion, lemon, milk, and spices. "
                    "CRITICAL RULE: Answer directly without greetings, self-identifications, or mentioning your name (never say 'I am Johnny'). "
                    "Focus purely on the dynamic AI-driven scientific answer in under 150 words. "
                    "AVOID complex chemical equation symbols like $ signs or arrows that break text-to-speech."
                )
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(f"{system_prompt}\n\nUser Question: {user_question}")
                    answer_text = response.text
                    
                    st.session_state.chat_history.append({"q": user_question, "a": answer_text})
                    st.markdown(f"**🤖 Johnny (AI Response):** {answer_text}")
                    speak_text(answer_text)
                except Exception as e:
                    st.error(f"Error communicating with Gemini API: {e}")

    if st.session_state.chat_history:
        st.markdown("### 📜 Q&A History")
        for item in reversed(st.session_state.chat_history):
            st.write(f"**Q:** {item['q']}")
            st.write(f"**A:** {item['a']}")
            st.markdown("---")
