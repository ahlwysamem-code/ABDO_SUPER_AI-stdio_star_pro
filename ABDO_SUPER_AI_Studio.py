import streamlit as st
import os
import sqlite3
from datetime import datetime
from PIL import Image
from gtts import gTTS
import tempfile
import zipfile
import openai

# --- إعداد الصفحة ---
st.set_page_config(page_title="ABDO SUPER AI V4", page_icon="🤖", layout="wide")

# --- تصميم واجهة الدردشة ---
st.markdown("""
<style>
body{background:black;color:white}
.chat-user{background:#0084ff;padding:10px;border-radius:10px;color:white;margin:5px;text-align:right}
.chat-ai{background:#222;padding:10px;border-radius:10px;color:white;margin:5px;text-align:left}
</style>
""", unsafe_allow_html=True)

st.title("🤖 ABDO SUPER AI V4")

# --- تسجيل الدخول ---
if "auth" not in st.session_state:
    st.session_state.auth=False

if not st.session_state.auth:
    password = st.text_input("كلمة المرور", type="password")
    if st.button("تسجيل الدخول"):
        if password=="ABDODEMON":
            st.session_state.auth=True
        else:
            st.error("كلمة المرور خاطئة")
    st.stop()

# --- إنشاء المجلدات ---
ROOT="abdo_data"
os.makedirs(ROOT, exist_ok=True)

# --- قاعدة البيانات ---
conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS memory(
command TEXT,
result TEXT,
time TEXT
)
""")
conn.commit()

def save_memory(cmd,res):
    cursor.execute(
        "INSERT INTO memory VALUES (?,?,?)",
        (cmd,res,datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()

# --- تنفيذ الأوامر ---
def execute(cmd):

    cmd_lower = cmd.lower()

    # أوامر مخصصة
    if "لعبة" in cmd_lower:
        os.makedirs("game_project", exist_ok=True)
        with open("game_project/game.py","w") as f:
            f.write("print('مشروع لعبة جديد')")
        result = "🎮 تم إنشاء مشروع لعبة"

    elif "صورة" in cmd_lower:
        img = Image.new("RGB",(512,512),(0,255,0))
        path = "image.png"
        img.save(path)
        st.image(path)
        result = "🖼️ تم إنشاء صورة"

    elif "موقع" in cmd_lower:
        os.makedirs("site", exist_ok=True)
        with open("site/index.html","w") as f:
            f.write("<h1>مرحبا بك في موقع ABDO</h1>")
        result = "🌐 تم إنشاء موقع HTML"

    else:
        # --- الذكاء الاصطناعي الحقيقي OpenAI ---
        try:
            openai.api_key = st.secrets["OPENAI_KEY"]
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role":"user","content":cmd}]
            )
            result = response.choices[0].message.content
        except Exception as e:
            result = f"[!] خطأ في الاتصال بـ OpenAI: {e}"

    save_memory(cmd,result)
    return result

# --- تخزين المحادثة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- عرض المحادثة السابقة ---
for msg in st.session_state.messages:
    if msg["role"]=="user":
        st.markdown(f"<div class='chat-user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-ai'>{msg['content']}</div>", unsafe_allow_html=True)

# --- إدخال رسالة جديدة ---
prompt = st.chat_input("اكتب رسالتك...")

if prompt:
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role":"user","content":prompt})

    # تنفيذ الأمر أو سؤال الذكاء الاصطناعي
    result = execute(prompt)

    # إضافة رد الذكاء الاصطناعي
    st.session_state.messages.append({"role":"assistant","content":result})

    # تحويل الرد إلى صوت
    tts = gTTS(result, lang="ar")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    st.audio(tmp.name)

# --- رفع الملفات ---
st.sidebar.title("📁 رفع ملفات")
uploaded_file = st.sidebar.file_uploader("اختر ملف")

if uploaded_file:
    path = os.path.join(ROOT, uploaded_file.name)
    with open(path,"wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("تم رفع الملف")

# --- عرض الذاكرة ---
if st.sidebar.checkbox("عرض الذاكرة"):
    rows = cursor.execute("SELECT * FROM memory").fetchall()
    for r in rows:
        st.sidebar.write(r)

# --- تنزيل المشاريع ZIP ---
if st.sidebar.button("تحميل المشاريع"):
    zip_path = "projects.zip"
    with zipfile.ZipFile(zip_path,"w") as z:
        for root_dir, dirs, files in os.walk("."):
            for file in files:
                z.write(os.path.join(root_dir, file))
    with open(zip_path,"rb") as f:
        st.download_button("تحميل المشاريع", f, "projects.zip")
