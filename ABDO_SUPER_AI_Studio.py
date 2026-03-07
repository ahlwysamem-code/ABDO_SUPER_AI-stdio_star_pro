import streamlit as st
from datetime import datetime
from PIL import Image
import io, requests
import docx
import fitz  # PyMuPDF
import openai
import os

###########################################
# إعداد OpenAI API
###########################################
# ضع مفتاح API الخاص بك هنا
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

###########################################
# إعداد الصفحة Streamlit
###########################################
st.set_page_config(page_title="DEMON 😈 GPT AI By ABDO", layout="wide")

st.markdown("""
<style>
body{background:#050505;color:white;font-family:Arial;}
.title{
font-size:50px;color:#ff0000;text-align:center;
text-shadow:0 0 10px red,0 0 20px red,0 0 40px #ff0000,0 0 60px #ff0000;font-weight:bold;}
.chat-user{background:#111;padding:14px;border-radius:20px;margin:5px;text-align:right;border:1px solid #333;box-shadow: 0 0 10px #00ffff;}
.chat-ai{background:#0f0f0f;padding:14px;border-radius:20px;margin:5px;text-align:left;border:1px solid #ff0000;color:#ff4444;box-shadow: 0 0 15px #ff0000;}
textarea{background:#111;color:white;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>DEMON 😈 GPT AI By ABDO</div>", unsafe_allow_html=True)

###########################################
# ذاكرة المحادثة طويلة
###########################################
if "memory" not in st.session_state:
    st.session_state.memory = []

###########################################
# دالة الذكاء الاصطناعي GPT
###########################################
def ai_chat(prompt, model="gpt-4"):
    """التحدث مع GPT الحقيقي مع استخدام الذاكرة الطويلة"""
    context = ""
    for chat in st.session_state.memory[-20:]:  # آخر 20 رسالة
        context += f"User: {chat['user']}\nAI: {chat['ai']}\n"
    context += f"User: {prompt}\nAI:"
    
    response = openai.Completion.create(
        engine=model,
        prompt=context,
        max_tokens=300,
        temperature=0.7,
        top_p=0.95,
        n=1,
        stop=["User:", "AI:"]
    )
    return response.choices[0].text.strip()

###########################################
# رفع وتحليل الملفات
###########################################
st.sidebar.title("📂 File Analyzer")
file = st.sidebar.file_uploader("Upload txt, pdf, or docx")

if file:
    content_preview = ""
    if file.name.endswith(".txt"):
        try:
            content = file.read().decode("utf-8")
        except:
            content = str(file.read())
        content_preview = content[:1000]
    elif file.name.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        content = ""
        for page in doc:
            content += page.get_text()
        content_preview = content[:1000]
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        content = "\n".join([p.text for p in doc.paragraphs])
        content_preview = content[:1000]
    st.sidebar.write("Preview (first 1000 chars):")
    st.sidebar.write(content_preview)

###########################################
# توليد الصور AI
###########################################
st.sidebar.title("🖼 Image Generator")
img_prompt = st.sidebar.text_input("Enter prompt for image")

if st.sidebar.button("Generate Image"):
    try:
        hf_token = st.secrets.get("HUGGINGFACE_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        url="https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
        headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
        response = requests.post(url,json={"inputs":img_prompt}, headers=headers)
        if response.status_code==200:
            img = Image.open(io.BytesIO(response.content))
            st.image(img)
        else:
            st.sidebar.write("Image generation failed")
    except Exception as e:
        st.sidebar.write("Error:", e)

###########################################
# الترجمة
###########################################
st.sidebar.title("🌐 Translator")
translate_text = st.sidebar.text_input("Text to translate")

if st.sidebar.button("Translate"):
    try:
        url="https://api.mymemory.translated.net/get"
        r=requests.get(url,params={"q":translate_text,"langpair":"auto|en"})
        st.sidebar.write(r.json()["responseData"]["translatedText"])
    except Exception as e:
        st.sidebar.write("Translation error:", e)

###########################################
# توليد أكواد مشاريع كاملة
###########################################
st.sidebar.title("💻 Project Code Generator")
code_prompt = st.sidebar.text_input("Describe code you want")

if st.sidebar.button("Generate Code"):
    try:
        code_output = ai_chat(code_prompt)
        st.sidebar.code(code_output)
    except Exception as e:
        st.sidebar.write("Code generation error:", e)

###########################################
# الدردشة
###########################################
user_message = st.text_input("Your Message")

if st.button("Send") and user_message.strip():
    ai_response = ai_chat(user_message)
    st.session_state.memory.append({
        "user": user_message,
        "ai": ai_response,
        "time": datetime.now()
    })

###########################################
# عرض المحادثة
###########################################
for chat in reversed(st.session_state.memory):
    st.markdown(f"<div class='chat-user'>{chat['user']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='chat-ai'>{chat['ai']}</div>", unsafe_allow_html=True)
