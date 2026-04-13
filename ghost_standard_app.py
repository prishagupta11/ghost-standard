import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import streamlit.components.v1 as components
import json

def init_db():
    conn = sqlite3.connect('ghost_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, name TEXT, password_hash TEXT,
                  dob TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (username TEXT, original TEXT, rewritten TEXT,
                  vibe TEXT, tone TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(email, name, password, dob):
    conn = sqlite3.connect('ghost_data.db')
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE email=?", (email,))
    if c.fetchone():
        conn.close()
        return False, "Email already registered."
    c.execute("INSERT INTO users VALUES (?,?,?,?,?)",
              (email, name, hash_password(password), dob,
               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return True, "ok"

def login_user(email, password):
    conn = sqlite3.connect('ghost_data.db')
    c = conn.cursor()
    c.execute("SELECT name, password_hash FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, None, "No account found with that email."
    if row[1] != hash_password(password):
        return False, None, "Wrong password."
    return True, row[0], "ok"

def save_history(username, original, rewritten, vibe, tone):
    conn = sqlite3.connect('ghost_data.db')
    conn.execute("INSERT INTO history VALUES (?,?,?,?,?,?)",
                 (username, original, rewritten, vibe, tone,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_history(username):
    conn = sqlite3.connect('ghost_data.db')
    c = conn.cursor()
    c.execute("""SELECT original, rewritten, vibe, tone, timestamp
                 FROM history WHERE username=?
                 ORDER BY timestamp DESC LIMIT 8""", (username,))
    data = c.fetchall()
    conn.close()
    return data

init_db()

st.set_page_config(page_title="Ghost-Standard Pro", page_icon="👻", layout="wide")
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  [data-testid="stAppViewContainer"] { background: #0a0a14 !important; }
  iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

for k, v in {
    "logged_in": False, "user_email": "", "user_name": "", "auth_error": ""
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

qp = st.query_params
if "action" in qp:
    action = qp["action"]
    if action == "register":
        ok, msg = register_user(qp.get("email",""), qp.get("name",""), qp.get("password",""), qp.get("dob",""))
        if ok:
            st.session_state.logged_in  = True
            st.session_state.user_email = qp.get("email","")
            st.session_state.user_name  = qp.get("name","")
            st.session_state.auth_error = ""
        else:
            st.session_state.auth_error = msg
        st.query_params.clear(); st.rerun()
    elif action == "login":
        ok, name, msg = login_user(qp.get("email",""), qp.get("password",""))
        if ok:
            st.session_state.logged_in  = True
            st.session_state.user_email = qp.get("email","")
            st.session_state.user_name  = name or ""
            st.session_state.auth_error = ""
        else:
            st.session_state.auth_error = msg
        st.query_params.clear(); st.rerun()
    elif action == "logout":
        st.session_state.logged_in  = False
        st.session_state.user_email = ""
        st.session_state.user_name  = ""
        st.session_state.auth_error = ""
        st.query_params.clear(); st.rerun()
    elif action == "save_history":
        save_history(qp.get("user",""), qp.get("original",""), qp.get("rewritten",""), qp.get("vibe",""), qp.get("tone",""))
        st.query_params.clear()

history_json = json.dumps([
    {"original": r[0], "rewritten": r[1], "vibe": r[2], "tone": r[3], "ts": r[4]}
    for r in (get_history(st.session_state.user_email) if st.session_state.logged_in else [])
])
logged_in_js  = "true" if st.session_state.logged_in else "false"
user_email_js = json.dumps(st.session_state.user_email)
user_name_js  = json.dumps(st.session_state.user_name)
auth_error_js = json.dumps(st.session_state.auth_error)
st.session_state.auth_error = ""

try:
    # This grabs your Gemini key from secrets.toml
    G_KEY = json.dumps(st.secrets["GEMINI_API_KEY"])
except Exception:
    G_KEY = json.dumps("")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Pacifico&family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=Dancing+Script:wght@600;700&family=Nunito:wght@400;600;700;800&family=Quicksand:wght@500;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow-x:hidden;-webkit-font-smoothing:antialiased}
body{font-family:'Nunito',sans-serif;background:#0a0a14;color:#e2d9ff;transition:background .5s,color .5s}

#loginWrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1.5rem;background:#0f0e1f}
.auth-card{background:#17153a;border:1px solid #2a2460;border-radius:24px;padding:clamp(1.5rem,4vw,2.5rem);width:100%;max-width:440px}
.auth-logo{text-align:center;margin-bottom:1.5rem}
.auth-logo-icon{font-size:36px}
.auth-logo-name{font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:700;color:#c8b8ff;display:block;margin-top:.3rem}
.auth-logo-sub{font-size:.8rem;color:#6a5ea8;margin-top:.15rem}
.auth-tabs{display:flex;background:#0f0e1f;border-radius:12px;padding:3px;margin-bottom:1.5rem;gap:3px}
.auth-tab{flex:1;text-align:center;padding:8px;border-radius:10px;font-size:13px;font-weight:700;cursor:pointer;color:#6a5ea8;transition:all .2s;font-family:'Nunito',sans-serif;border:none;background:transparent}
.auth-tab.active{background:#2d2860;color:#c8b8ff}
.form-panel{display:none}
.form-panel.active{display:block}
.field-label{font-size:11px;font-weight:700;color:#7a70b8;text-transform:uppercase;letter-spacing:.08em;margin-bottom:5px;display:block}
.field-input{width:100%;background:#0f0e1f;border:1.5px solid #2a2460;border-radius:10px;color:#e2d9ff;font-size:14px;padding:11px 14px;margin-bottom:1rem;outline:none;font-family:'Nunito',sans-serif;transition:border-color .2s}
.field-input:focus{border-color:#7b5cf0}
.field-row{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}
.auth-btn{width:100%;background:#6b3fe8;color:#fff;border:none;border-radius:12px;padding:12px;font-size:15px;font-weight:800;cursor:pointer;font-family:'Nunito',sans-serif;transition:background .2s;margin-top:.25rem}
.auth-btn:hover{background:#8255f0}
.divider-row{display:flex;align-items:center;gap:10px;margin:1rem 0}
.divider-line{flex:1;height:1px;background:#2a2460}
.divider-text{font-size:11px;color:#4a4270;white-space:nowrap}
.google-btn{width:100%;background:transparent;color:#a098d8;border:1.5px solid #2a2460;border-radius:12px;padding:11px;font-size:13px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;font-family:'Nunito',sans-serif;transition:all .2s}
.google-btn:hover{border-color:#7b5cf0;color:#c8b8ff}
.auth-error{background:#2a1520;border:1px solid #6b2d3a;color:#f0a0b0;border-radius:10px;padding:10px 12px;font-size:13px;margin-bottom:1rem;font-weight:600;display:none}
.auth-error.show{display:block}

#appWrap{display:none;min-height:100vh}

body.beach{background:#faf3d8;color:#1e3a2a}
.beach #appWrap{background:#faf3d8}
.beach .sidebar{background:#fff8e8;border-right:2px solid #e8d888}
.beach .s-logo-name{font-family:'Pacifico',cursive;color:#5a7a00;font-size:15px}
.beach .s-badge{background:#ffe566;color:#6a5000;font-weight:800}
.beach .s-user{background:#fff3c0;border:1.5px solid #e8d888}
.beach .s-avatar{background:#ffd700;color:#5a4000;font-weight:800}
.beach .s-email{color:#7a6a30;font-weight:700}
.beach .h-mood{color:#c07800;font-weight:800}
.beach .h-txt{color:#8a7a40;font-weight:600}
.beach .vibe-banner{background:#fff3c0;border:1.5px solid #e8d888}
.beach .banner-title{font-family:'Pacifico',cursive;color:#3a5a00;font-size:15px}
.beach .banner-sub{color:#7a6a30;font-weight:600}
.beach .step-num{background:#ffd700;border:2px solid #c8a800;color:#5a4000;font-weight:800}
.beach .step-title{font-family:'Pacifico',cursive;color:#2a4a00;font-size:14px}
.beach .step-card{background:#fff8e8;border:1.5px solid #e8d888}
.beach .msg-box{background:#fff8e8;border:2px solid #d8c868;color:#1e3a2a;font-weight:600}
.beach .msg-box::placeholder{color:#b8a858}
.beach .tone-card{border:2px solid #e0d080;background:#fff8e8}
.beach .tone-card:hover{background:#fff3c0;border-color:#c8a800}
.beach .tone-card.active{background:#fff0a0;border-color:#b89000;border-width:2.5px}
.beach .tone-name{color:#2a4a00;font-weight:800}
.beach .tone-desc{color:#8a7a40;font-weight:600}
.beach .feel-chip{border:2px solid #d8c868;color:#4a5a20;background:#fff8e8;font-weight:700}
.beach .feel-chip:hover{border-color:#a89000}
.beach .feel-chip.active{background:#fff0a0;border-color:#b89000;color:#2a4a00}
.beach .go-btn{background:#e8a800;color:#2a2000;font-family:'Pacifico',cursive;font-size:16px}
.beach .go-btn:hover:not(:disabled){background:#d09000}
.beach .result-box{background:#fff8e8;border:2px solid #d8c868}
.beach .res-tag{background:#ffe566;color:#5a4000;font-weight:800}
.beach .res-text{font-family:'Pacifico',cursive;color:#1e3a2a;font-size:16px;line-height:1.9}
.beach .res-btn{border:2px solid #d8c868;color:#5a5020;font-weight:700}
.beach .s-out{border-color:#d8c868;color:#8a7a40;font-weight:700}

body.firm{background:#111008;color:#f0e8d0}
.firm #appWrap{background:#111008}
.firm .sidebar{background:#0c0a05;border-right:2px solid #2a2410}
.firm .s-logo-name{font-family:'Playfair Display',serif;color:#d4aa60;font-size:14px;font-weight:700}
.firm .s-badge{background:#2a2010;color:#d4aa60;font-weight:800;border:1px solid #4a3a18}
.firm .s-user{background:#1a1508;border:1.5px solid #2a2410}
.firm .s-avatar{background:#3a2c10;color:#d4aa60;font-weight:800}
.firm .s-email{color:#8a7a50;font-weight:600}
.firm .h-mood{color:#c09040;font-weight:800}
.firm .h-txt{color:#6a5a38;font-weight:600}
.firm .vibe-banner{background:#1a1508;border:1.5px solid #2a2410}
.firm .banner-title{font-family:'Playfair Display',serif;color:#e8d0a0;font-size:14px;font-weight:700}
.firm .banner-sub{color:#8a7a50;font-weight:600}
.firm .step-num{background:#2a2010;border:2px solid #4a3a18;color:#d4aa60;font-weight:800}
.firm .step-title{font-family:'Playfair Display',serif;color:#e8d8b0;font-size:14px;font-weight:700}
.firm .step-card{background:#0c0a05;border:2px solid #2a2410}
.firm .msg-box{background:#0c0a05;border:2px solid #2a2410;color:#f0e8d0;font-weight:600}
.firm .msg-box::placeholder{color:#3a3020}
.firm .tone-card{border:2px solid #2a2410;background:#0c0a05}
.firm .tone-card:hover{background:#1a1508;border-color:#4a3a18}
.firm .tone-card.active{background:#1e1a08;border-color:#c09040;border-width:2.5px}
.firm .tone-name{color:#f0e8d0;font-weight:800}
.firm .tone-desc{color:#8a7a50;font-weight:600}
.firm .feel-chip{border:2px solid #2a2410;color:#c0a870;background:transparent;font-weight:700}
.firm .feel-chip.active{background:#1e1a08;border-color:#c09040;color:#f0e0a0}
.firm .go-btn{background:#2a2010;color:#f0e0b0;font-family:'Playfair Display',serif;font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;border:2px solid #c09040}
.firm .go-btn:hover:not(:disabled){background:#3a3018}
.firm .result-box{background:#1a1508;border:2px solid #2a2410}
.firm .res-tag{background:#2a2010;color:#d4aa60;font-weight:800}
.firm .res-text{font-family:'Playfair Display',serif;color:#f0e8d0;font-size:15px;font-style:italic;line-height:1.85}
.firm .res-btn{border:2px solid #2a2410;color:#c0a870;font-weight:700}
.firm .s-out{border-color:#2a2410;color:#6a5a38;font-weight:700}

body.homely{background:#1a1005;color:#f4e8cc}
.homely #appWrap{background:#1a1005}
.homely .sidebar{background:#120c03;border-right:2px solid #2e2010}
.homely .s-logo-name{font-family:'Quicksand',sans-serif;color:#e0a050;font-size:14px;font-weight:700}
.homely .s-badge{background:#241608;color:#e0a050;font-weight:800}
.homely .s-user{background:#201408;border:1.5px solid #2e2010}
.homely .s-avatar{background:#3a2010;color:#e0a050;font-weight:800}
.homely .s-email{color:#8a7048;font-weight:700}
.homely .h-mood{color:#c88030;font-weight:800}
.homely .h-txt{color:#6a5838;font-weight:600}
.homely .vibe-banner{background:#201408;border:1.5px solid #2e2010}
.homely .banner-title{font-family:'Quicksand',sans-serif;color:#f0d090;font-size:14px;font-weight:700}
.homely .banner-sub{color:#8a7048;font-weight:600}
.homely .step-num{background:#3a2010;border:2px solid #5a3818;color:#e0a050;font-weight:800}
.homely .step-title{font-family:'Quicksand',sans-serif;color:#f4e0b0;font-size:14px;font-weight:700}
.homely .step-card{background:#120c03;border:2px solid #2e2010}
.homely .msg-box{background:#120c03;border:2px solid #2e2010;color:#f4e8cc;font-weight:600}
.homely .msg-box::placeholder{color:#3a2c18}
.homely .tone-card{border:2px solid #2e2010;background:#120c03}
.homely .tone-card.active{background:#241408;border-color:#c88030;border-width:2.5px}
.homely .tone-name{color:#f4e8cc;font-weight:800}
.homely .tone-desc{color:#8a7048;font-weight:600}
.homely .feel-chip{border:2px solid #2e2010;color:#b09050;background:transparent;font-weight:700}
.homely .feel-chip.active{background:#241408;border-color:#c88030;color:#f0d090}
.homely .go-btn{background:#3a2010;color:#f8e0b0;font-family:'Quicksand',sans-serif;font-size:15px;font-weight:800;border:2px solid #c88030}
.homely .go-btn:hover:not(:disabled){background:#4a2c18}
.homely .result-box{background:#201408;border:2px solid #2e2010}
.homely .res-tag{background:#3a2010;color:#e0a050;font-weight:800}
.homely .res-text{font-family:'Quicksand',sans-serif;color:#f4e8cc;font-size:15px;font-weight:600;line-height:1.85}
.homely .res-btn{border:2px solid #2e2010;color:#b09050;font-weight:700}
.homely .s-out{border-color:#2e2010;color:#6a5838;font-weight:700}

body.pookie{background:#fdf0f5;color:#3a1828}
.pookie #appWrap{background:#fdf0f5}
.pookie .sidebar{background:#fce8f2;border-right:2px solid #f0b8d0}
.pookie .s-logo-name{font-family:'Dancing Script',cursive;color:#c03070;font-size:16px;font-weight:700}
.pookie .s-badge{background:#fcd0e8;color:#a02060;font-weight:800;border:1px solid #f0a0c8}
.pookie .s-user{background:#fde0ec;border:1.5px solid #f0b8d0}
.pookie .s-avatar{background:#fcc0e0;color:#901850;font-weight:800}
.pookie .s-email{color:#a07088;font-weight:700}
.pookie .h-mood{color:#c03070;font-weight:800}
.pookie .h-txt{color:#b08090;font-weight:600}
.pookie .vibe-banner{background:#fde8f4;border:1.5px solid #f0b8d0}
.pookie .banner-title{font-family:'Dancing Script',cursive;color:#a02060;font-size:18px;font-weight:700}
.pookie .banner-sub{color:#a07088;font-weight:600}
.pookie .step-num{background:#fcc0e0;border:2px solid #f090c0;color:#901850;font-weight:800}
.pookie .step-title{font-family:'Dancing Script',cursive;color:#901850;font-size:17px;font-weight:700}
.pookie .step-card{background:#fce8f2;border:1.5px solid #f0b8d0}
.pookie .msg-box{background:#fce8f2;border:2px solid #f0b8d0;color:#3a1828;font-weight:700}
.pookie .msg-box::placeholder{color:#d090b0}
.pookie .tone-card{border:2px solid #f0b8d0;background:#fce8f2}
.pookie .tone-card:hover{background:#fde0ec;border-color:#e090b8}
.pookie .tone-card.active{background:#fcc8e4;border-color:#c03070;border-width:2.5px}
.pookie .tone-name{color:#3a1828;font-weight:800}
.pookie .tone-desc{color:#b080a0;font-weight:600}
.pookie .feel-chip{border:2px solid #f0b8d0;color:#a06080;background:#fce8f2;font-weight:700}
.pookie .feel-chip.active{background:#fcc8e4;border-color:#c03070;color:#7a1040}
.pookie .go-btn{background:#d04080;color:#fff;font-family:'Dancing Script',cursive;font-size:20px;font-weight:700}
.pookie .go-btn:hover:not(:disabled){background:#b83060}
.pookie .result-box{background:#fce8f2;border:2px solid #f0b8d0}
.pookie .res-tag{background:#fcc0e0;color:#901850;font-weight:800}
.pookie .res-text{font-family:'Dancing Script',cursive;color:#3a1828;font-size:20px;font-weight:700;line-height:1.9}
.pookie .res-btn{border:2px solid #f0b8d0;color:#a06080;font-weight:700}
.pookie .s-out{border-color:#f0b8d0;color:#b08090;font-weight:700}

body.default{background:#0a0a14;color:#e2d9ff}
.default #appWrap{background:#0a0a14}
.default .sidebar{background:#0d0b1e;border-right:2px solid #252048}
.default .s-logo-name{color:#b8a8f8;font-size:14px;font-weight:800}
.default .s-badge{background:#1e1a40;color:#8b78d4;font-weight:800}
.default .s-user{background:#13112a;border:1.5px solid #252048}
.default .s-avatar{background:#2a2060;color:#9b85e8;font-weight:800}
.default .s-email{color:#7060a8;font-weight:600}
.default .h-mood{color:#7060d0;font-weight:800}
.default .h-txt{color:#5a4e7a;font-weight:600}
.default .vibe-banner{background:#13112a;border:1.5px solid #252048}
.default .banner-title{color:#c8b8ff;font-size:15px;font-weight:800}
.default .banner-sub{color:#7060a8;font-weight:600}
.default .step-num{background:#1e1a40;border:2px solid #352e78;color:#8b78d4;font-weight:800}
.default .step-title{color:#d0c0ff;font-size:14px;font-weight:800}
.default .step-card{background:#0d0b1e;border:2px solid #252048}
.default .msg-box{background:#0d0b1e;border:2px solid #252048;color:#e2d9ff;font-weight:600}
.default .msg-box::placeholder{color:#302858}
.default .tone-card{border:2px solid #252048;background:#0d0b1e}
.default .tone-card.active{background:#1a1840;border-color:#6b5cf0;border-width:2.5px}
.default .tone-name{color:#e2d9ff;font-weight:800}
.default .tone-desc{color:#6a5e98;font-weight:600}
.default .feel-chip{border:2px solid #252048;color:#9080c8;font-weight:700}
.default .feel-chip.active{background:#1a1840;border-color:#6b5cf0;color:#c8b8ff}
.default .go-btn{background:#6b3fe8;color:#fff;font-size:15px;font-weight:800}
.default .go-btn:hover:not(:disabled){background:#8255f0}
.default .result-box{background:#13112a;border:2px solid #252048}
.default .res-tag{background:#1e1a40;color:#8b78d4;font-weight:800}
.default .res-text{color:#e2d9ff;font-size:15px;font-weight:600;line-height:1.85}
.default .res-btn{border:2px solid #252048;color:#9080c8;font-weight:700}
.default .s-out{border-color:#252048;color:#5a4e7a;font-weight:700}

.sidebar{width:200px;flex-shrink:0;display:flex;flex-direction:column;padding:1.2rem 1rem;position:fixed;top:0;left:0;height:100vh;z-index:100;overflow-y:auto;transition:background .5s,border-color .5s}
.s-logo{display:flex;align-items:center;gap:8px;margin-bottom:1.4rem}
.s-logo-icon{font-size:20px}
.s-badge{font-size:10px;padding:2px 8px;border-radius:20px;margin-left:auto;font-family:'Nunito',sans-serif}
.s-user{display:flex;align-items:center;gap:8px;padding:9px 10px;border-radius:10px;margin-bottom:1.3rem}
.s-avatar{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;flex-shrink:0}
.s-email{font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.s-sec{font-size:10px;text-transform:uppercase;letter-spacing:.1em;opacity:.5;margin-bottom:8px;font-family:'Nunito',sans-serif;font-weight:700}
.h-item{padding:8px 9px;border-radius:8px;margin-bottom:4px;cursor:pointer}
.h-item:hover{background:rgba(128,100,50,.08)}
.h-mood{font-size:10px;margin-bottom:2px;text-transform:uppercase;letter-spacing:.05em}
.h-txt{font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.s-out{margin-top:auto;background:transparent;border:1.5px solid;border-radius:8px;padding:7px;font-size:12px;cursor:pointer;width:100%;color:inherit;font-family:'Nunito',sans-serif;font-weight:700;opacity:.7;transition:opacity .2s}
.s-out:hover{opacity:1}

.main-panel{margin-left:200px;padding:clamp(1.2rem,3vw,2rem);display:flex;flex-direction:column;align-items:center;min-height:100vh}
.main-inner{width:100%;max-width:680px;display:flex;flex-direction:column;gap:1.3rem}

.vibe-banner{border-radius:14px;padding:14px 18px;display:flex;align-items:center;gap:12px;transition:all .5s}
.banner-icon{font-size:26px;flex-shrink:0}
.banner-sub{font-size:12px;margin-top:2px;font-family:'Nunito',sans-serif}

.step{display:flex;gap:10px;align-items:flex-start}
.step-card{border-radius:14px;padding:1.1rem 1.2rem;flex:1;transition:all .5s}
.step-num{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;flex-shrink:0;margin-top:2px;transition:all .5s}
.step-title{font-size:13px;margin-bottom:10px;transition:all .4s}

textarea.msg-box{width:100%;border-radius:10px;font-size:14px;padding:12px 14px;resize:none;outline:none;line-height:1.65;transition:all .5s;font-family:'Nunito',sans-serif}

.tone-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:8px}
.tone-card{border-radius:12px;padding:10px 8px;cursor:pointer;text-align:center;transition:all .2s}
.tone-card.card-hidden{display:none}
.tone-icon{font-size:18px;margin-bottom:4px}
.tone-name{font-size:12px;margin-bottom:2px;font-family:'Nunito',sans-serif}
.tone-desc{font-size:11px;opacity:.55;font-family:'Nunito',sans-serif;font-weight:600}

.feel-row{display:flex;flex-wrap:wrap;gap:7px}
.feel-chip{border-radius:20px;padding:6px 13px;font-size:12px;cursor:pointer;transition:all .2s;font-family:'Nunito',sans-serif}

.who-step{overflow:hidden;transition:opacity .3s}
.who-step.step-hidden{max-height:0!important;opacity:0;pointer-events:none;margin:0!important}

.go-btn{border:none;border-radius:12px;padding:13px;cursor:pointer;width:100%;font-weight:800;font-size:15px;transition:all .3s}
.go-btn:disabled{opacity:.4;cursor:not-allowed;filter:none!important}

.result-box{border-radius:14px;padding:1.2rem;display:none;transition:all .5s;animation:fadeUp .35s ease}
.result-box.show{display:block}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.res-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:6px}
.res-label{font-size:11px;text-transform:uppercase;letter-spacing:.08em;opacity:.5;font-family:'Nunito',sans-serif;font-weight:700}
.res-tag{font-size:11px;padding:3px 10px;border-radius:20px;font-family:'Nunito',sans-serif}
.res-text{margin-bottom:12px}
.res-actions{display:flex;gap:8px}
.res-btn{background:transparent;border:1.5px solid;border-radius:8px;padding:6px 14px;font-size:12px;cursor:pointer;color:inherit;font-family:'Nunito',sans-serif;opacity:.7;transition:opacity .2s}
.res-btn:hover{opacity:1}

.spinner-wrap{display:none;justify-content:center;align-items:center;gap:6px;padding:.5rem 0}
.spinner-wrap.show{display:flex}
.spin-dot{width:9px;height:9px;border-radius:50%;background:currentColor;opacity:.5;animation:bop 1.1s infinite}
.spin-dot:nth-child(2){animation-delay:.18s}
.spin-dot:nth-child(3){animation-delay:.36s}
@keyframes bop{0%,80%,100%{transform:scale(.7);opacity:.35}40%{transform:scale(1.25);opacity:1}}

.toast{position:fixed;bottom:1.5rem;right:1.5rem;background:#222;color:#fff;padding:9px 16px;border-radius:10px;font-size:13px;font-family:'Nunito',sans-serif;font-weight:700;opacity:0;transition:opacity .3s;pointer-events:none;z-index:999}
.toast.show{opacity:1}

@media(max-width:680px){
  .sidebar{position:fixed;bottom:0;top:auto;width:100%;height:auto;flex-direction:row;align-items:center;padding:.6rem 1rem;border-right:none;border-top:2px solid rgba(128,100,50,.2);overflow-y:visible;z-index:200}
  .s-logo{margin-bottom:0;flex:1}
  .s-badge,.s-sec,.h-item{display:none}
  .s-logo-name{font-size:13px!important}
  .s-user{margin-bottom:0;padding:5px 8px}
  .s-email{max-width:70px}
  .s-out{margin-top:0;width:auto;padding:5px 12px}
  .main-panel{margin-left:0;padding-bottom:5rem}
  .tone-grid{grid-template-columns:repeat(2,1fr)}
}
@media(min-width:681px) and (max-width:960px){
  .sidebar{width:175px}
  .main-panel{margin-left:175px}
  .tone-grid{grid-template-columns:repeat(3,1fr)}
}
</style>
</head>
<body class="default">

<div id="loginWrap">
  <div class="auth-card">
    <div class="auth-logo">
      <span class="auth-logo-icon">👻</span>
      <span class="auth-logo-name">Ghost-Standard Pro</span>
      <span class="auth-logo-sub">Words not wording? We got you.</span>
    </div>
    <div class="auth-error" id="authError"></div>
    <div class="auth-tabs">
      <button class="auth-tab active" id="tabLogin" onclick="switchTab('login')">Log In</button>
      <button class="auth-tab" id="tabSignup" onclick="switchTab('signup')">Sign Up</button>
    </div>
    <div class="form-panel active" id="panelLogin">
      <label class="field-label">Email address</label>
      <input class="field-input" id="loginEmail" type="email" placeholder="your@gmail.com"/>
      <label class="field-label">Password</label>
      <input class="field-input" id="loginPw" type="password" placeholder="••••••••"/>
      <button class="auth-btn" id="loginBtn">Log In</button>
      <div class="divider-row"><div class="divider-line"></div><span class="divider-text">or</span><div class="divider-line"></div></div>
      <button class="google-btn" id="googleBtn">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.47 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        Continue with Google (demo)
      </button>
    </div>
    <div class="form-panel" id="panelSignup">
      <div class="field-row">
        <div><label class="field-label">Full name</label><input class="field-input" id="signupName" type="text" placeholder="Your name"/></div>
        <div><label class="field-label">Date of birth</label><input class="field-input" id="signupDob" type="date"/></div>
      </div>
      <label class="field-label">Email address</label>
      <input class="field-input" id="signupEmail" type="email" placeholder="your@gmail.com"/>
      <label class="field-label">Password</label>
      <input class="field-input" id="signupPw" type="password" placeholder="Min 6 characters"/>
      <button class="auth-btn" id="signupBtn">Create Account</button>
    </div>
  </div>
</div>

<div id="appWrap">
  <div class="sidebar">
    <div class="s-logo">
      <span id="sIcon" style="font-size:18px">🌴</span>
      <span class="s-logo-name" id="sLogoName">Ghost-Standard</span>
      <span class="s-badge">PRO</span>
    </div>
    <div class="s-user">
      <div class="s-avatar" id="sAvatar">GS</div>
      <div class="s-email" id="sEmail">ghost@gmail.com</div>
    </div>
    <div class="s-sec">Recent</div>
    <div id="histList"></div>
    <button class="s-out" id="logoutBtn">log out</button>
  </div>
  <div class="main-panel">
    <div class="main-inner">
      <div class="vibe-banner" id="banner">
        <div class="banner-icon" id="bannerIcon">🌊</div>
        <div>
          <div class="banner-title" id="bannerTitle">Sun, salt & zero drama</div>
          <div class="banner-sub" id="bannerSub">Breezy, warm, totally unbothered</div>
        </div>
      </div>
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-card">
          <div class="step-title">Pick your vibe first</div>
          <div class="feel-row" id="feelRow">
            <span class="feel-chip active" data-feel="Chill & unbothered" data-theme="beach">🌊 Chill & unbothered</span>
            <span class="feel-chip" data-feel="Firm but polite" data-theme="firm">🪨 Firm but polite</span>
            <span class="feel-chip" data-feel="Sweet & caring" data-theme="homely">🍞 Sweet & caring</span>
            <span class="feel-chip" data-feel="Lovey dovey" data-theme="pookie">🩷 Lovey dovey</span>
            <span class="feel-chip" data-feel="Funny & playful" data-theme="default">😄 Funny & playful</span>
            <span class="feel-chip" data-feel="Confident & direct" data-theme="firm">⚡ Confident & direct</span>
          </div>
        </div>
      </div>
      <div class="step who-step step-hidden" id="whoStep">
        <div class="step-num">2</div>
        <div class="step-card">
          <div class="step-title" id="whoTitle">Who are you texting?</div>
          <div class="tone-grid" id="toneGrid">
            <div class="tone-card active" data-tone="a close friend"><div class="tone-icon">🤝</div><div class="tone-name">Friend</div><div class="tone-desc">Casual & real</div></div>
            <div class="tone-card" data-tone="a crush"><div class="tone-icon">💘</div><div class="tone-name">Crush</div><div class="tone-desc">Smooth & nervous</div></div>
            <div class="tone-card" data-tone="my partner"><div class="tone-icon">💑</div><div class="tone-name">Partner</div><div class="tone-desc">Close & loving</div></div>
            <div class="tone-card" data-tone="family"><div class="tone-icon">🏠</div><div class="tone-name">Family</div><div class="tone-desc">Warm & caring</div></div>
            <div class="tone-card" data-tone="boss or coworker"><div class="tone-icon">💼</div><div class="tone-name">Boss / work</div><div class="tone-desc">Professional</div></div>
            <div class="tone-card" data-tone="an acquaintance"><div class="tone-icon">👋</div><div class="tone-name">Acquaintance</div><div class="tone-desc">Polite & friendly</div></div>
          </div>
        </div>
      </div>
      <div class="step">
        <div class="step-num" id="msgStepNum">2</div>
        <div class="step-card">
          <div class="step-title">What do you want to say?</div>
          <textarea class="msg-box" id="msgInput" rows="4" placeholder="Type your rough message here..."></textarea>
        </div>
      </div>
      <div class="spinner-wrap" id="spinner">
        <div class="spin-dot"></div><div class="spin-dot"></div><div class="spin-dot"></div>
      </div>
      <button class="go-btn" id="goBtn">Rewrite my message ✦</button>
      <div class="result-box" id="resultBox">
        <div class="res-head">
          <span class="res-label">✦ your rewritten message</span>
          <span class="res-tag" id="resTag">chill · friend</span>
        </div>
        <div class="res-text" id="resText"></div>
        <div class="res-actions">
          <button class="res-btn" id="copyBtn">Copy</button>
          <button class="res-btn" id="tryAgainBtn">Try again</button>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const LOGGED_IN  = PYLOGGED;
const USER_EMAIL = PYEMAIL;
const USER_NAME  = PYNAME;
const HISTORY    = PYHISTORY;
const AUTH_ERROR = PYAUTHERR;
const API_KEY    = PYAPIKEY;

const VIBE_PROMPTS = {
  "Chill & unbothered": "casual, breezy, totally relaxed like texting from a hammock. Sun-soaked and easy.",
  "Firm but polite":    "firm, composed, and clear. Polite but strong energy. No fluff.",
  "Sweet & caring":     "warm, sweet, genuinely caring. Like a cosy hug in text form.",
  "Lovey dovey":        "lovey-dovey, soft, full of affection. Cute pookie energy. Big heart.",
  "Funny & playful":    "funny, witty and playful with light humour. A little cheeky.",
  "Confident & direct": "confident, direct, no-nonsense. Exactly what needs to be said, boldly.",
};
const THEMES = {
  beach:  {icon:'🌊',sIcon:'🌴',title:'Sun, salt & zero drama',sub:'Breezy, warm, totally unbothered'},
  firm:   {icon:'🪨',sIcon:'⚡',title:'Say it with your chest.',sub:'Composed. Clear. No fluff.'},
  homely: {icon:'🍞',sIcon:'🏡',title:'Warm like a home-cooked meal',sub:'Gentle, genuine, full of heart.'},
  pookie: {icon:'🩷',sIcon:'💕',title:'Full pookie mode activated',sub:'Soft, bright & absolutely adorable.'},
  default:{icon:'👻',sIcon:'👻',title:'Funny & playful energy',sub:'Witty, light and a little cheeky.'}
};
const TONE_FILTERS = {
  firm:   ['a close friend','boss or coworker','an acquaintance','family'],
  pookie: ['a close friend','a crush','my partner','family'],
};

let selTheme='beach', selFeel='Chill & unbothered', selTone='a close friend';
let localHistory=[...HISTORY];

function showToast(msg){
  const t=document.getElementById('toast');
  t.textContent=msg; t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),2200);
}

function pushAuth(params){
  const url=new URL(window.parent.location.href);
  Object.entries(params).forEach(([k,v])=>url.searchParams.set(k,v));
  window.parent.history.pushState({},'',url);
  window.parent.location.reload();
}
async function callAI(original, vibe, tone){
  if(!API_KEY) throw new Error("Add GEMINI_API_KEY to .streamlit/secrets.toml");
  const vibeDesc = VIBE_PROMPTS[vibe] || "casual and natural";
  const toLabel = tone || "someone";
  
  const prompt = `You are Ghost-Standard Pro, a Gen-Z text rewriter. Rewrite this message for texting ${toLabel}. Vibe: ${vibeDesc}. Keep it 1-3 sentences, authentic, not cringe. End with exactly 1 relevant emoji.\n\nMessage: "${original}"`;

  // Replace the fetch block inside callAI with this:
  // We are using v1beta and gemini-2.0-flash which showed up in your list!
  // Change 'gemini-2.0-flash' to 'gemini-2.5-flash-lite'
// This model has the highest free limits (15 RPM)
const res = await fetch(`https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash-lite:generateContent?key=${API_KEY}`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }]
  })
});

  if(!res.ok) {
    const e = await res.json();
    throw new Error(e?.error?.message || "API error");
  }
  
  const data = await res.json();
  return data.candidates[0].content.parts[0].text || "Ghost dropped the signal 👻";
}

function switchTab(tab){
  document.getElementById('tabLogin').classList.toggle('active',tab==='login');
  document.getElementById('tabSignup').classList.toggle('active',tab==='signup');
  document.getElementById('panelLogin').classList.toggle('active',tab==='login');
  document.getElementById('panelSignup').classList.toggle('active',tab==='signup');
  document.getElementById('authError').classList.remove('show');
}

if(AUTH_ERROR){
  const el=document.getElementById('authError');
  el.textContent=AUTH_ERROR; el.classList.add('show');
  if(AUTH_ERROR.includes('registered')) switchTab('signup');
}

document.getElementById('loginBtn').onclick=()=>{
  const email=document.getElementById('loginEmail').value.trim();
  const pw=document.getElementById('loginPw').value;
  if(!email||!pw){showToast('Fill in both fields 👀');return;}
  pushAuth({action:'login',email,password:pw});
};
['loginEmail','loginPw'].forEach(id=>
  document.getElementById(id).addEventListener('keydown',e=>{if(e.key==='Enter')document.getElementById('loginBtn').click();})
);
document.getElementById('signupBtn').onclick=()=>{
  const name=document.getElementById('signupName').value.trim();
  const dob=document.getElementById('signupDob').value;
  const email=document.getElementById('signupEmail').value.trim();
  const pw=document.getElementById('signupPw').value;
  if(!name||!email||!pw){showToast('Please fill all fields 👀');return;}
  if(pw.length<6){showToast('Password must be 6+ characters');return;}
  pushAuth({action:'register',name,dob,email,password:pw});
};
document.getElementById('googleBtn').onclick=()=>{
  pushAuth({action:'register',name:'Demo User',dob:'2000-01-01',email:'demo.user@gmail.com',password:'google123'});
};
document.getElementById('logoutBtn').onclick=()=>pushAuth({action:'logout'});

function renderHistory(){
  const hl=document.getElementById('histList');
  hl.innerHTML='';
  localHistory.slice(0,6).forEach(r=>{
    const orig=r.original||r[0]||'';
    const vibe=r.vibe||r[2]||'';
    const d=document.createElement('div');
    d.className='h-item';
    d.innerHTML=`<div class="h-mood">${vibe}</div><div class="h-txt">${orig.slice(0,44)}...</div>`;
    hl.appendChild(d);
  });
}

function applyTheme(theme){
  document.body.className=theme;
  const t=THEMES[theme];
  document.getElementById('bannerIcon').textContent=t.icon;
  document.getElementById('sIcon').textContent=t.sIcon;
  document.getElementById('bannerTitle').textContent=t.title;
  document.getElementById('bannerSub').textContent=t.sub;
  selTheme=theme;
  const allowed=TONE_FILTERS[theme]||null;
  const whoStep=document.getElementById('whoStep');
  const cards=document.querySelectorAll('.tone-card');
  const needWho=!!allowed;
  whoStep.classList.toggle('step-hidden',!needWho);
  if(needWho) document.getElementById('whoTitle').textContent=theme==='pookie'?"Who's your person?":"Who are you addressing?";
  cards.forEach(c=>c.classList.toggle('card-hidden',allowed!==null&&!allowed.includes(c.dataset.tone)));
  const first=document.querySelector('.tone-card:not(.card-hidden)');
  if(first){cards.forEach(x=>x.classList.remove('active'));first.classList.add('active');selTone=first.dataset.tone;}
  document.getElementById('msgStepNum').textContent=needWho?'3':'2';
  document.getElementById('resultBox').classList.remove('show');
}

function showApp(){
  document.getElementById('loginWrap').style.display='none';
  document.getElementById('appWrap').style.display='block';
  document.getElementById('sEmail').textContent=USER_EMAIL;
  document.getElementById('sAvatar').textContent=(USER_NAME||USER_EMAIL).slice(0,2).toUpperCase();
  renderHistory();
  applyTheme('beach');
}

if(LOGGED_IN) showApp();

document.getElementById('feelRow').querySelectorAll('.feel-chip').forEach(c=>{
  c.onclick=()=>{
    document.querySelectorAll('.feel-chip').forEach(x=>x.classList.remove('active'));
    c.classList.add('active'); selFeel=c.dataset.feel; applyTheme(c.dataset.theme);
  };
});
document.getElementById('toneGrid').querySelectorAll('.tone-card').forEach(c=>{
  c.onclick=()=>{
    if(c.classList.contains('card-hidden'))return;
    document.querySelectorAll('.tone-card').forEach(x=>x.classList.remove('active'));
    c.classList.add('active'); selTone=c.dataset.tone;
  };
});

document.getElementById('goBtn').onclick=async()=>{
  const msg=document.getElementById('msgInput').value.trim();
  if(!msg){
    document.getElementById('msgInput').style.outline='2px solid #e04444';
    setTimeout(()=>document.getElementById('msgInput').style.outline='',700);
    showToast('Type something first! 👀');
    return;
  }
  const whoHidden=document.getElementById('whoStep').classList.contains('step-hidden');
  const tone=whoHidden?'':selTone;
  const btn=document.getElementById('goBtn');
  btn.disabled=true; btn.textContent='Rewriting...';
  document.getElementById('spinner').classList.add('show');
  document.getElementById('resultBox').classList.remove('show');
  try{
    const result=await callAI(msg,selFeel,tone);
    document.getElementById('resText').textContent=result;
    document.getElementById('resTag').textContent=selFeel+(tone?' · '+tone:'');
    document.getElementById('resultBox').classList.add('show');
    localHistory.unshift({original:msg,rewritten:result,vibe:selFeel,tone});
    if(localHistory.length>8) localHistory.pop();
    renderHistory();
  }catch(err){
    showToast('Error: '+err.message);
    document.getElementById('resText').textContent='Something went wrong 👻 — '+err.message;
    document.getElementById('resultBox').classList.add('show');
  }
  btn.disabled=false; btn.textContent='Rewrite my message ✦';
  document.getElementById('spinner').classList.remove('show');
};

document.getElementById('copyBtn').onclick=()=>{
  navigator.clipboard.writeText(document.getElementById('resText').textContent)
    .then(()=>showToast('Copied ✓'));
};
document.getElementById('tryAgainBtn').onclick=()=>document.getElementById('goBtn').click();
</script>
</body>
</html>"""

# inject python values — use replace so no f-string conflicts with JS braces
HTML = HTML.replace('PYLOGGED',  logged_in_js)
HTML = HTML.replace('PYEMAIL',   user_email_js)
HTML = HTML.replace('PYNAME',    user_name_js)
HTML = HTML.replace('PYAUTHERR', auth_error_js)
HTML = HTML.replace('PYHISTORY', history_json)

# 1. Grab the Gemini key from your secrets.toml
try:
    G_KEY = json.dumps(st.secrets["GEMINI_API_KEY"])
except:
    G_KEY = json.dumps("")

# 2. Use G_KEY here so the "Rewrite" button gets the correct key
HTML = HTML.replace('PYAPIKEY', G_KEY)
components.html(HTML, height=740, scrolling=True)
