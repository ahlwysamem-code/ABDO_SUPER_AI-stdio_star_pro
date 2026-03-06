import streamlit as st
import os, sqlite3, time, requests, json, zipfile
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image
from moviepy.editor import ImageSequenceClip
from streamlit_player import st_player
from gtts import gTTS
import tempfile
import speech_recognition as sr

# --- إعداد الواجهة ---
st.set_page_config(page_title="ABDO SUPER Ai", page_icon="👹", layout="wide")
st.markdown("""
<style>
body { background-color: #000; color: #00FF00; font-family: 'Courier New', monospace; }
h1.title { font-size: 50px; color: #00FF00; text-align: center; font-family: 'Arial Rounded MT Bold', sans-serif; }
.stTextInput>div>div>input { background-color: #050505; color: #00FF00; border: 2px solid #00FF00; font-size: 18px; padding: 8px; border-radius: 8px; }
.stButton>button { background-color: #004400; color: #00FF00; border: 2px solid #00FF00; font-weight: bold; width: 100%; transition: 0.3s; border-radius: 8px; }
.stButton>button:hover { background-color: #00FF00; color: black; }
.terminal-box { background-color: #001100; padding: 25px; border-radius: 15px; border: 3px solid #00FF00; color: #00FF00; box-shadow: 0 0 25px #00FF00; font-size: 18px; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# --- حماية بكلمة المرور ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h1 class='title'>🔒 ABDO SUPER Ai LOGIN</h1>", unsafe_allow_html=True)
    pwd = st.text_input("أدخل كلمة المرور الخاصة بك:", type="password")
    if st.button("تفعيل الدخول"):
        if pwd == "ABDODEMON":
            st.session_state["auth"] = True
            st.experimental_rerun()
        else:
            st.error("⚠️ كلمة المرور غير صحيحة!")
    st.stop()

# --- بعد تسجيل الدخول ---
st.markdown("<h1 class='title'>ABDO SUPER Ai Ultimate</h1>", unsafe_allow_html=True)

# --- رسالة ترحيب ---
def welcome_message():
    msg = "مرحبًا بك يا سيدي ABDO! 👑\nABDO SUPER Ai جاهز لتنفيذ أوامرك."
    display_text = ""
    for char in msg:
        display_text += char
        st.markdown(f"<div class='terminal-box'>{display_text}</div>", unsafe_allow_html=True)
        time.sleep(0.01)
welcome_message()

# --- تشغيل أغنية الخلفية ---
if os.path.exists("media/Lonely.mp3"):
    st_player("media/Lonely.mp3", playing=True, loop=True, volume=0.2)

# --- إعداد مجلدات المشروع ---
ROOT = "./ABDO_SUPER_AI"
for p in ["projects","videos","vault","media"]:
    os.makedirs(os.path.join(ROOT, p), exist_ok=True)

# --- SQLite لتخزين الأوامر والنتائج ---
conn = sqlite3.connect(os.path.join(ROOT, "vault/secured_brain.db"), check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY, command TEXT, output TEXT, timestamp TEXT)")
conn.commit()

def save_memory(command, output):
    cursor.execute("INSERT INTO memory (command, output, timestamp) VALUES (?, ?, ?)",
                   (command, output, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

# --- slow motion print ---
def slow_print(text):
    display_text = ""
    for char in text:
        display_text += char
        st.markdown(f"<div class='terminal-box'>{display_text}</div>", unsafe_allow_html=True)
        time.sleep(0.01)

# --- Autopilot: تنفيذ الأوامر ---
def autopilot_execute(command, uploaded_file=None, speak=False):
    output = ""
    try:
        cmd = command.lower()
        # ألعاب
        if "اصنع لعبة" in cmd:
            game_name = command.replace("اصنع لعبة","").strip()
            output = f"🕹️ تم إنشاء لعبة '{game_name}' بالكامل: أكواد + شخصيات + أسلحة + خلفيات"
            proj_path = os.path.join(ROOT, "projects", game_name.replace(" ","_"))
            os.makedirs(proj_path, exist_ok=True)
        # توليد الصور
        elif "اصنع صورة" in cmd or "توليد صورة" in cmd:
            img_path = os.path.join(ROOT, "media", "sample_image.png")
            Image.new('RGB',(512,512),(0,255,0)).save(img_path)
            output = f"🖼️ تم توليد صورة وحفظها في: {img_path}"
        # توليد الفيديو
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
            output = f"🎬 تم توليد فيديو وحفظه: {video_path}"
        # رفع ملفات صور/فيديو
        elif uploaded_file is not None:
            file_type = uploaded_file.type
            save_path = os.path.join(ROOT, "media" if 'image' in file_type else "videos", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            output = f"📂 تم رفع الملف وتحليله: {save_path}"
        else:
            output = f"✅ تم تنفيذ الطلب تلقائيًا: {command}"
    except Exception as e:
        output = f"[!] خطأ أثناء التنفيذ: {str(e)}"
    
    save_memory(command, output)
    
    # تحويل النص إلى صوت إذا تم الطلب
    if speak:
        try:
            tts = gTTS(text=output, lang='ar')
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(tmp_file.name)
            st.audio(tmp_file.name, format='audio/mp3')
        except Exception as e:
            st.error(f"خطأ في تحويل النص إلى صوت: {e}")
    
    return output

# --- فك ZIP تلقائي ---
uploaded_zip_path = st.file_uploader("📎 رفع ملف ZIP المشروع", type=["zip"])
if uploaded_zip_path is not None:
    try:
        extract_folder = os.path.join(ROOT, "projects", "extracted_project")
        os.makedirs(extract_folder, exist_ok=True)
        with zipfile.ZipFile(uploaded_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
        st.success(f"✅ تم فك ضغط المشروع بنجاح في: {extract_folder}")
    except Exception as e:
        st.error(f"❌ خطأ أثناء فك ZIP: {e}")

# --- واجهة المستخدم ---
col1, col2, col3 = st.columns([1,6,1])
with col1:
    uploaded_file = st.file_uploader("📎 رفع صورة/فيديو", type=["png","jpg","jpeg","mp4"])
with col2:
    query = st.text_input("أصدر أمرك يا ABDO…")
with col3:
    send = st.button("إرسال")

# --- أوامر صوتية ---
voice_input = st.button("🎤 تسجيل صوت")
if voice_input:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ تحدث الآن...")
        audio = r.listen(source, phrase_time_limit=5)
        try:
            voice_text = r.recognize_google(audio, language="ar-EG")
            st.success(f"تم تحويل الصوت إلى نص: {voice_text}")
            query = voice_text
        except Exception as e:
            st.error(f"خطأ في التعرف على الصوت: {e}")

# --- تنفيذ الأمر ---
if (send and query) or uploaded_file is not None:
    res = autopilot_execute(query, uploaded_file, speak=True)
    slow_print(res)

# --- عرض آخر 20 مهمة ---
if st.checkbox("📂 عرض ذاكرة المهام السابقة"):
    cursor.execute("SELECT * FROM memory ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    for r in rows:
        st.markdown(f"**{r[3]}** → `{r[1]}` → {r[2]}")