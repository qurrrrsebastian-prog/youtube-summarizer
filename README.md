# Project #13 — YouTube Video Summarizer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=chainlink&logoColor=white" />
  <img src="https://img.shields.io/badge/YouTube-FF0000?style=flat&logo=youtube&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" />
</p>

> Extract transcript video YouTube otomatis dan ringkas jadi key insights + actionable takeaways. Hemat waktu nonton video panjang.

---

## Demo Langsung

[![Deploy to Streamlit Cloud](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://share.streamlit.io/deploy?repository=qurrrrsebastian-prog/youtube-summarizer)

**Tech Stack:** `YouTube Transcript API` · `LangChain` · `Google Gemini API` · `Streamlit`

---

## Fitur

| Fitur | Status |
|-------|--------|
| Extract transcript otomatis | ✅ |
| Summary dengan key insights | ✅ |
| Actionable takeaways | ✅ |
| Support video panjang | ✅ |
| Multi-language transcript | ✅ |
| Tema gelap AVA purple | ✅ |

---

## Cara Menjalankan

```bash
git clone https://github.com/qurrrrsebastian-prog/youtube-summarizer.git
cd youtube-summarizer
pip install -r requirements.txt
$env:GEMINI_API_KEY="your_api_key_here"
streamlit run app.py
```

## Deploy ke Streamlit Cloud (GRATIS)

1. [share.streamlit.io](https://share.streamlit.io) → Login GitHub
2. **New app** → Pilih repo ini
3. Tambahkan secret: `GEMINI_API_KEY`
4. **Deploy**

---

## Struktur Project

```
youtube-summarizer/
├── app.py              # Main Streamlit app
├── requirements.txt    # Dependencies
├── .streamlit/
│   └── config.toml    # AVA purple branding
├── .gitignore
└── LICENSE            # MIT License
```

---

**Dibuat oleh:** [Avatar Putra Sigit](https://github.com/qurrrrsebastian-prog) · Founder @AVA.Group
