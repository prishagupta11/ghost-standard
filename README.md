# 👻 Ghost-Standard Pro

An AI-powered text rewriting assistant built with **Streamlit, JavaScript, SQLite, and Google Gemini API**.

Ghost-Standard Pro helps users rewrite their messages according to different moods, tones, and situations — making everyday texting easier and more natural.

---

## ✨ Features

| Feature                | Description                                       |
| ---------------------- | ------------------------------------------------- |
| 🔐 User Authentication | Register and login system with password hashing   |
| 🤖 AI Rewriting        | Uses Gemini API to rewrite messages intelligently |
| 🎭 Mood Selection      | Choose different writing styles and vibes         |
| 💬 Tone Selection      | Adjust message style based on the recipient       |
| 🕒 History Tracking    | Saves previous rewritten messages                 |
| 🎨 Custom UI Themes    | Dynamic themes based on selected vibe             |
| 📱 Responsive Design   | Works across desktop and mobile layouts           |

---

## 🧠 How It Works

1. User creates an account or logs in
2. Selects the desired writing vibe
3. Chooses who the message is for
4. Enters a rough message
5. Gemini AI rewrites it into a cleaner version

---

## 🎭 Available Writing Styles

### 🌊 Chill & Unbothered

Relaxed, casual, and easy-going tone.

### ⚡ Firm but Polite

Clear and confident communication.

### 🍞 Sweet & Caring

Warm and thoughtful messages.

### 🩷 Lovey Dovey

Soft and affectionate style.

### 😄 Funny & Playful

Light humour and playful wording.

### ⚡ Confident & Direct

Straightforward and bold communication.

---

## 🛠️ Tech Stack

```
Frontend
│
├── HTML / CSS
├── JavaScript
└── Streamlit Components

Backend
│
├── Python
├── SQLite
└── Gemini API

Security
│
└── SHA-256 Password Hashing
```

---

## 📂 Project Structure

```
Ghost-Standard-Pro/
│
├── app.py
├── ghost_data.db
├── .streamlit/
│   └── secrets.toml
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/prishagupta11/ghost-standard/tree/main
```

Move into the project folder:

```bash
cd Ghost-Standard-Pro
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔑 API Setup

Create a file:

```
.streamlit/secrets.toml
```

Add your Gemini API key:

```toml
GEMINI_API_KEY = "your_api_key_here"
```

---

## ▶️ Run The Application

Start Streamlit:

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🗃️ Database

The project uses SQLite to store:

### Users Table

Stores:

* Email
* Name
* Password hash
* Date of birth
* Account creation time

### History Table

Stores:

* Original message
* Rewritten message
* Selected vibe
* Selected tone
* Timestamp

---

## 🚀 Future Improvements

* Add Google OAuth authentication
* Add user profile customization
* Add multiple AI models
* Add downloadable chat history
* Add voice input support
* Deploy with cloud database

---

## 👩‍💻 Author

**Your Name**

GitHub:
https://github.com/prishagupta11

---

⭐ If you found this project interesting, feel free to star the repository.
