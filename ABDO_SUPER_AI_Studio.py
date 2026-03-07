import streamlit as st
from gtts import gTTS
import tempfile
from PIL import Image
from moviepy.editor import ImageSequenceClip
import os
import sqlite3
from datetime import datetime
import zipfile

# --- إعداد الصفحة ---
st.set_page_config(page_title="ABDO SUPER Ai Ultimate", layout="wide")

# --- CSS لتجميل الواجهة ---
st.markdown("""
<style>
body {background-color: #0a0a0a; color: #00FF00; font-family: 'Courier New', monospace;}
h1.title {font-size: 60px; text-align:center; color:#00FF00; text-shadow: 0 0 20px #00FF00;}
.stTextInput>div>div>input {background-color:#050505; color:#00FF00; border:2px solid #00FF00; font-size:20px; padding:10px; border-radius:10px; transition:0.3s;}
.stTextInput>div>div>input:focus {border-color:#FF0000; box-shadow: 0 0 15px #FF0000;}
.stButton>button {background-color:#004400; color:#00FF00; border:2px solid #00FF00; font-weight:bold; width:100%; transition:0.3s; border-radius:10px;}
.stButton>button:hover {background-color:#00FF00; color:black;}
.upload-bar {display:flex; justify-content: space-around; align-items:center; margin-bottom:10px; padding:10px; background-color:#001100; border-radius:10px;}
.upload-bar div {text-align:center; color:#00FF00; cursor:pointer;}
.upload-bar input[type="file"] {display:none;}
.message-user {text-align:right; color:#00FF00; font-weight:bold; margin:5px;}
.message-ai {text-align:left; color:#FF9900; font-weight:bold; margin:5px;}
.terminal-box {background-color:#001100; padding:20px; border-radius:15px; border:3px solid #00FF00; box-shadow:0 0 25px #00FF00; font-size:18px;}
</style>
""", unsafe_allow_html=True)

# --- إعداد مجلدات التطبيق ---
ROOT = "./ABDO_SUPER_AI"
for folder in ["projects", "videos", "vault", "media"]:
    os.makedirs(os.path.join(ROOT, folder), exist_ok=True)

# --- قاعدة بيانات SQLite ---
conn = sqlite3.connect(os.path.join(ROOT, "vault/secured_brain.db"), check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY, 
    role TEXT,
    content TEXT,
    timestamp TEXT
)""")
conn.commit()

def save_message(role, content):
    cursor.execute("INSERT INTO memory (role, content, timestamp) VALUES (?, ?, ?)",
                   (role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

# --- واجهة كلمة المرور ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h1 class='title'>🔒 ABDO SUPER Ai LOGIN</h1>", unsafe_allow_html=True)
    pwd = st.text_input("أدخل كلمة المرور الخاصة بك:", type="password", placeholder="كلمة مرورك السرية هنا ...")
    if st.button("تفعيل الدخول"):
        if pwd.strip().lower() == "abdodemon":
            st.session_state["auth"] = True
            st.success("✔️ تم تسجيل الدخول بنجاح!")
        else:
            st.error("⚠️ كلمة المرور غير صحيحة!")
    st.stop()

# --- شريط رفع الملفات أعلى الشاشة ---
st.markdown("<div class='upload-bar'>\
<div><label for='file_zip'>📁 رفع ZIP</label><input type='file' id='file_zip'></div>\
<div><label for='file_img'>🖼️ رفع صورة</label><input type='file' id='file_img'></div>\
<div><label for='file_vid'>🎬 رفع فيديو</label><input type='file' id='file_vid'></div>\
</div>", unsafe_allow_html=True)

# --- رفع ملفات ZIP تلقائيًا ---
uploaded_zip = st.file_uploader("📎 رفع ملف ZIP المشروع", type=["zip"])
if uploaded_zip:
    try:
        extract_folder = os.path.join(ROOT, "projects", "extracted_project")
        os.makedirs(extract_folder, exist_ok=True)
        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
        st.success(f"✅ تم فك ضغط المشروع بنجاح في: {extract_folder}")
    except Exception as e:
        st.error(f"❌ خطأ أثناء فك ZIP: {e}")

# --- رفع الصور والفيديو ---
uploaded_file = st.file_uploader("📎 رفع صورة/فيديو", type=["png","jpg","jpeg","mp4"])
if uploaded_file:
    try:
        save_path = os.path.join(ROOT, "media" if 'image' in uploaded_file.type else "videos", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ تم رفع الملف وحفظه: {save_path}")
    except Exception as e:
        st.error(f"❌ خطأ أثناء حفظ الملف: {e}")

# --- واجهة المحادثة ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# إدخال المستخدم
user_input = st.text_input("أرسل أمرك هنا…")
speak = st.checkbox("🔊 أريد سماع النتيجة بصوت")

if user_input:
    # تنفيذ الأوامر الأساسية
    result = ""
    cmd = user_input.lower()
    
    # --- أوامر تجريبية ---
    if "اصنع لعبة" in cmd:
        game_name = user_input.replace("اصنع لعبة","").strip()
        proj_path = os.path.join(ROOT, "projects", game_name.replace(" ","_"))
        os.makedirs(proj_path, exist_ok=True)
        result = f"🕹️ تم إنشاء لعبة '{game_name}' بالكامل: أكواد + شخصيات + أسلحة + خلفيات"
    elif "اصنع صورة" in cmd or "توليد صورة" in cmd:
        img_path = os.path.join(ROOT, "media", "sample_image.png")
        Image.new('RGB',(512,512),(0,255,0)).save(img_path)
        result = f"🖼️ تم توليد صورة وحفظها في: {img_path}"
    elif "اصنع فيديو" in cmd or "توليد فيديو" in cmd:
        images = []
        for i in range(10):
            img = Image.new('RGB',(640,480),(i*25,0,255-i*25))
            img_path = os.path.join(ROOT, "videos", f"frame_{i}.png")
            img.save(img_path)
            images.append(img_path)
        clip = ImageSequenceClip(images, fps=2)
        video_path = os.path.join(ROOT, "videos", "output.mp4")
        clip.write_videofile(video_path, codec="libx264", verbose=False, logger=None)
        result = f"🎬 تم توليد فيديو وحفظه: {video_path}"
    else:
        result = f"{user_input}"  # أي أمر آخر يُعرض مباشرة
    
    # حفظ الرسائل
    st.session_state["messages"].append({"role":"user", "content": user_input})
    st.session_state["messages"].append({"role":"ai", "content": result})
    save_message("user", user_input)
    save_message("ai", result)
    
    # الصوت عند الطلب
    if speak:
        tts = gTTS(text=result, lang='ar')
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(tmp_file.name)
        st.audio(tmp_file.name, format="audio/mp3")

# --- عرض المحادثة بشكل احترافي ---
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"<div class='message-user'>أنت: {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='message-ai'>ABDO Ai: {msg['content']}</div>", unsafe_allow_html=True)
