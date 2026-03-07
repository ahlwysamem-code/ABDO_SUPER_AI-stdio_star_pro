import streamlit as st
import requests, os, sqlite3, tempfile
from PIL import Image
from gtts import gTTS
from datetime import datetime

# --- إعداد الصفحة ---
st.set_page_config(page_title="ABDO SUPER AI", page_icon="👹", layout="wide")

# --- واجهة Cyberpunk ---
st.markdown("""
<style>
body { background-color: #000; color: #00FF00; font-family: 'Courier New', monospace; }
h1.title { font-size: 45px; color: #00FF00; text-align: center; margin-bottom:10px; }
.stTextInput>div>div>input { background-color: #050505; color: #00FF00; border: 2px solid #00FF00; font-size: 18px; padding: 10px; border-radius: 8px; }
.stButton>button { background-color: #004400; color: #00FF00; border: 2px solid #00FF00; font-weight: bold; width: 100%; transition: 0.3s; border-radius: 8px; }
.stButton>button:hover { background-color: #00FF00; color: black; }
.chat-box { padding: 15px; margin:5px 0; }
.user-msg { background-color:#004400; padding:10px; border-radius:10px; color:#00FF00; margin-left:auto; max-width:80%; }
.ai-msg { background-color:#000044; padding:10px; border-radius:10px; color:#00FF00; margin-right:auto; max-width:80%; }
.upload-bar { border: 2px solid #00FF00; border-radius: 8px; padding: 8px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- كلمة المرور ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("<h1 class='title'>🔒 ABDO SUPER AI LOGIN</h1>", unsafe_allow_html=True)
    pwd = st.text_input("أدخل كلمة المرور:", type="password")
    if st.button("تفعيل الدخول"):
        if pwd == "ABDODEMON":
            st.session_state["auth"] = True
            st.experimental_rerun()
        else:
            st.error("⚠️ كلمة المرور غير صحيحة!")
    st.stop()

# --- بعد تسجيل الدخول ---
st.markdown("<h1 class='title'>ABDO SUPER AI Ultimate</h1>", unsafe_allow_html=True)

# --- إعداد مجلدات المشروع ---
ROOT = "./ABDO_SUPER_AI"
for p in ["projects","videos","media","vault"]:
    os.makedirs(os.path.join(ROOT,p), exist_ok=True)

# --- قاعدة بيانات SQLite ---
conn = sqlite3.connect(os.path.join(ROOT,"vault/memory.db"), check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY, command TEXT, output TEXT, timestamp TEXT
)""")
conn.commit()

def save_memory(command, output):
    cursor.execute("INSERT INTO memory (command, output, timestamp) VALUES (?,?,?)",
                   (command, output, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

# --- رفع الملفات ---
st.markdown("<div class='upload-bar'>📎 رفع ملف ZIP، صورة أو فيديو</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["zip","png","jpg","jpeg","mp4"])
if uploaded_file:
    save_path = os.path.join(ROOT, "media" if 'image' in uploaded_file.type else "videos", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ تم رفع الملف: {uploaded_file.name}")

# --- واجهة الدردشة ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

query = st.text_input("أصدر أمرك يا ABDO…")
speak_btn = st.checkbox("🔊 تحويل الرد إلى صوت عند الطلب")

if st.button("إرسال") and query:
    try:
        headers = {"Authorization": f"Bearer {st.secrets['OPENAI_KEY']}"}
        data = {"model": "gpt-4", "prompt": query, "max_tokens": 500}
        res = requests.post("https://api.openai.com/v1/completions", headers=headers, json=data).json()
        ai_response = res["choices"][0]["text"]

        st.session_state.chat_history.append(("user", query))
        st.session_state.chat_history.append(("ai", ai_response))
        save_memory(query, ai_response)

        if speak_btn:
            tts = gTTS(text=ai_response, lang="ar")
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tmp_file.name)
            st.audio(tmp_file.name, format="audio/mp3")

    except Exception as e:
        st.error(f"[!] خطأ في الاتصال بالذكاء الاصطناعي: {e}")

# --- عرض المحادثة ---
for sender, msg in st.session_state.chat_history:
    if sender=="user":
        st.markdown(f"<div class='user-msg'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai-msg'>{msg}</div>", unsafe_allow_html=True)

# --- عرض آخر 20 مهمة ---
if st.checkbox("📂 عرض ذاكرة المهام السابقة"):
    cursor.execute("SELECT * FROM memory ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    for r in rows:
        st.markdown(f"**{r[3]}** → `{r[1]}` → {r[2]}")
