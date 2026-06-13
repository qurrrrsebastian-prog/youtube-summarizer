# YouTube Summarizer — Groq Powered

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange)

## 📌 Deskripsi
AI-powered YouTube video summarizer. Extract transcript otomatis → Groq (Llama 3.3 70B) rangkum jadi ringkasan + key points + actionable takeaway.

## 🎯 Fitur
- Extract transcript dari URL YouTube
- Support bahasa Indonesia & English
- AI summary dengan 3 format (ringkasan, key points, takeaway)
- Streamlit UI minimal

## 🛠️ Tech Stack
- Python, Streamlit, YouTube Transcript API, Groq (Llama 3.3 70B)

## 🚀 Cara Menjalankan

```bash
# Ambil API key gratis di https://console.groq.com/keys
$env:GROQ_API_KEY="gsk_....YOUR_KEY_HERE...."
pip install -r requirements.txt
streamlit run app.py
```

## 📊 Key Insight
- 80% video edukasi 30+ menit bisa dirangkum dalam 10 bullet points
- Transcript API gratis, nggak perlu download video
- Groq inference super cepat (ratusan token/detik) untuk transcript 6000+ kata

## 👤 Author
[Avatar Putra Sigit](https://linkedin.com/in/avatarputrasigit) — Founder & CEO @AVA.Group
[GitHub](https://github.com/qurrrrsebastian-prog)
