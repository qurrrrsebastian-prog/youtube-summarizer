"""YouTube Summarizer with Groq (Llama 3.3 70B). Author: Avatar Putra Sigit"""
import os
import sys
import re
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_groq import ChatGroq

def get_llm() -> ChatGroq:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        st.error("GROQ_API_KEY not found.")
        sys.exit(1)
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=key, temperature=0.3)

def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from URL."""
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_transcript(video_id: str) -> str:
    """Fetch transcript from YouTube (youtube-transcript-api >= 1.0)."""
    api = YouTubeTranscriptApi()
    # 1) Coba bahasa yang diinginkan dulu
    try:
        fetched = api.fetch(video_id, languages=["id", "en"])
        return " ".join(snippet.text for snippet in fetched)
    except Exception:
        pass
    # 2) Fallback: pakai transcript apa pun yang tersedia
    try:
        transcript = next(iter(api.list(video_id)))
        fetched = transcript.fetch()
        return " ".join(snippet.text for snippet in fetched)
    except Exception as e:
        return f"Error: {e}"

def summarize(text: str, llm: ChatGroq) -> str:
    """Summarize transcript with Groq."""
    prompt = f"""Summarize this YouTube video transcript in Indonesian. Provide:
1) Ringkasan singkat (3 kalimat),
2) 5 Key Points (bullet),
3) Actionable takeaway.

Transcript: {text[:15000]}"""
    response = llm.invoke(prompt)
    return response.content

def main() -> None:
    st.set_page_config(page_title="YouTube Summarizer", layout="wide")
    st.title("📺 YouTube Summarizer — Groq Powered")
    st.markdown("Paste link video → AI rangkum jadi key insights")

    url = st.text_input("🔗 URL YouTube:", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    if st.button("✨ Summarize", type="primary") and url:
        vid = extract_video_id(url)
        if not vid:
            st.error("Invalid YouTube URL")
            return
        with st.spinner("Fetching transcript..."):
            transcript = get_transcript(vid)
            if transcript.startswith("Error"):
                st.error(transcript)
                return
            st.success(f"Transcript fetched: {len(transcript.split())} words")
        with st.spinner("Summarizing with Groq..."):
            llm = get_llm()
            summary = summarize(transcript, llm)
            st.subheader("📝 Summary")
            st.markdown(summary)

if __name__ == "__main__":
    main()
