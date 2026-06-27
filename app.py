"""YouTube Summarizer — Groq (Llama 3.3 70B) | v2.0 production upgrade.

Rose Media theme, centered card with a history gallery below. v2.0 adds SQLite
persistence (summaries, audit_log), video metadata extraction via YouTube oEmbed,
four summary modes (Brief/Detailed/Bullet Points/Executive), an ID/EN language
selector, word-count statistics, a 3-column history grid, copy/share (markdown)
and export. Lazy Groq client keeps the UI usable without an API key.

Author: Avatar Putra Sigit | GitHub: qurrrrsebastian-prog
"""
import json
import os
import re
import urllib.parse
import urllib.request

import streamlit as st

import database as db
from security import sanitize_input
from ui_components import (PRIMARY, render_footer, render_header,
                           render_video_card)

st.set_page_config(page_title="YouTube Summarizer", layout="wide", page_icon="📺")

db.init_db()

MODES = {
    "Brief": "a concise 3-sentence summary",
    "Detailed": "a detailed multi-paragraph summary with clear sections",
    "Bullet Points": "a clean bulleted list of the main points only",
    "Executive": "an executive summary aimed at busy decision-makers, with a "
                 "one-line TL;DR followed by key implications",
}
LANGS = {"Indonesian": "Indonesian", "English": "English"}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False)
def get_llm():
    """Return a cached Groq chat model, or None if no API key."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    try:
        from langchain_groq import ChatGroq
        return ChatGroq(model="llama-3.3-70b-versatile", api_key=key, temperature=0.3)
    except Exception:  # noqa: BLE001
        return None


def extract_video_id(url: str):
    """Extract a YouTube video ID from a URL."""
    for p in (r"v=([a-zA-Z0-9_-]{11})", r"youtu\.be/([a-zA-Z0-9_-]{11})",
              r"embed/([a-zA-Z0-9_-]{11})"):
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def fetch_metadata(url: str):
    """Return (title, channel) via YouTube oEmbed; graceful fallback on error."""
    try:
        q = urllib.parse.quote(url, safe="")
        endpoint = f"https://www.youtube.com/oembed?url={q}&format=json"
        with urllib.request.urlopen(endpoint, timeout=8) as resp:
            data = json.load(resp)
        return data.get("title", "Unknown title"), data.get("author_name", "Unknown")
    except Exception:  # noqa: BLE001
        return "Unknown title", "Unknown channel"


def fmt_duration(seconds: float) -> str:
    """Format seconds as H:MM:SS or M:SS."""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def get_transcript(video_id: str, language: str):
    """Fetch transcript text and approximate duration. Returns (text, duration_str)."""
    from youtube_transcript_api import YouTubeTranscriptApi
    api = YouTubeTranscriptApi()
    lang_pref = ["id", "en"] if language == "Indonesian" else ["en", "id"]
    fetched = None
    try:
        fetched = api.fetch(video_id, languages=lang_pref)
    except Exception:  # noqa: BLE001
        try:
            fetched = next(iter(api.list(video_id))).fetch()
        except Exception as exc:  # noqa: BLE001
            return f"Error: {exc}", "N/A"
    snippets = list(fetched)
    text = " ".join(s.text for s in snippets)
    duration = "N/A"
    try:
        last = snippets[-1]
        duration = fmt_duration(getattr(last, "start", 0) + getattr(last, "duration", 0))
    except Exception:  # noqa: BLE001
        pass
    return text, duration


def summarize(text: str, llm, mode: str, language: str) -> str:
    """Summarize a transcript with Groq in the requested mode and language."""
    prompt = (
        f"Summarize this YouTube video transcript in {language}. Produce {MODES[mode]}. "
        "Then add a section 'KEY POINTS' with up to 5 bullets and a section "
        "'ACTIONABLE TAKEAWAY' with one concrete action.\n\n"
        f"Transcript: {text[:15000]}")
    return llm.invoke(prompt).content


def split_sections(summary: str):
    """Split the model output into (key_insights, actionable) best-effort."""
    key, action = "", ""
    km = re.search(r"KEY POINTS[:\s]*(.+?)(ACTIONABLE|$)", summary,
                   re.IGNORECASE | re.DOTALL)
    if km:
        key = km.group(1).strip()
    am = re.search(r"ACTIONABLE TAKEAWAY[:\s]*(.+)", summary, re.IGNORECASE | re.DOTALL)
    if am:
        action = am.group(1).strip()
    return key, action


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
llm = get_llm()
render_header("📺 YouTube Summarizer",
              "Turn any video into key insights · v2.0 Rose Media")
if llm is None:
    st.info("ℹ️ GROQ_API_KEY not set — summarization is disabled. History and "
            "export remain available.")

if "active_summary" not in st.session_state:
    st.session_state.active_summary = None

# Centered input card.
_, mid, _ = st.columns([1, 2, 1])
with mid:
    url = st.text_input("🔗 YouTube URL",
                        "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    c1, c2 = st.columns(2)
    mode = c1.selectbox("Summary mode", list(MODES.keys()))
    language = c2.selectbox("Language", list(LANGS.keys()))
    go = st.button("✨ Summarize", type="primary", use_container_width=True,
                   disabled=llm is None)

if go and url:
    vid = extract_video_id(url)
    if not vid:
        st.error("Invalid YouTube URL.")
    else:
        with st.spinner("Fetching transcript & metadata..."):
            title, channel = fetch_metadata(url)
            transcript, duration = get_transcript(vid, language)
        if transcript.startswith("Error"):
            st.error(transcript)
        else:
            words = len(transcript.split())
            with st.spinner("Summarizing with Groq..."):
                try:
                    summary = summarize(transcript, llm, mode, language)
                except Exception as exc:  # noqa: BLE001
                    summary = f"Error: {exc}"
            key_ins, action = split_sections(summary)
            db.add_summary(url, title, channel, duration, summary, key_ins, action, mode)
            db.add_log("summarize", f"{title} [{mode}]")
            st.session_state.active_summary = {
                "title": title, "channel": channel, "duration": duration,
                "summary": summary, "words": words, "mode": mode}

# Active summary display.
active = st.session_state.active_summary
if active:
    st.divider()
    st.subheader(f"📝 {active['title']}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Channel", active["channel"][:18])
    m2.metric("Duration", active["duration"])
    m3.metric("Transcript words", f"{active['words']:,}")
    m4.metric("Summary words", f"{len(active['summary'].split()):,}")
    st.markdown(active["summary"])
    st.caption("📋 Copy the markdown below to share:")
    st.code(active["summary"], language="markdown")
    st.download_button("⬇️ Download summary (.md)",
                       active["summary"].encode("utf-8"),
                       file_name="summary.md", mime="text/markdown")

# --------------------------------------------------------------------------- #
# History gallery (3-column grid)
# --------------------------------------------------------------------------- #
st.divider()
hg1, hg2 = st.columns([3, 1])
hg1.subheader("🖼️ History Gallery")
if hg2.button("🗑️ Clear history", use_container_width=True):
    db.clear_summaries()
    st.session_state.active_summary = None
    st.rerun()

history = db.get_summaries()
if history.empty:
    st.caption("No summaries yet — summarize a video to populate the gallery.")
else:
    rows = history.to_dict("records")
    for i in range(0, len(rows), 3):
        cols = st.columns(3)
        for col, rec in zip(cols, rows[i:i + 3]):
            with col:
                render_video_card(rec["video_title"] or "Untitled",
                                  rec["channel_name"] or "Unknown",
                                  rec["duration"] or "N/A", rec["mode"] or "—",
                                  rec["timestamp"])
                if st.button("👁️ View", key=f"view_{rec['id']}",
                             use_container_width=True):
                    st.session_state.active_summary = {
                        "title": rec["video_title"], "channel": rec["channel_name"],
                        "duration": rec["duration"], "summary": rec["summary"],
                        "words": len((rec["summary"] or "").split()),
                        "mode": rec["mode"]}
                    st.rerun()
    st.download_button("⬇️ Export all summaries (CSV)",
                       history.to_csv(index=False).encode("utf-8"),
                       file_name="summaries.csv", mime="text/csv")

render_footer()
