import streamlit as st
import os
import tempfile

from retreival.retreiver import get_relevant_chunks, build_context
from generation.generator import generate_answer
from vectorstore.chroma_store import save_documents, count, clear
from ingestion.pdf_processor import read_pdf
from ingestion.image_processor import describe_image
from ingestion.url_processor import read_url
import config

st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="🧠",
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "upload_counter" not in st.session_state:
    st.session_state.upload_counter = 0

# Auto-ingest documents on startup if DB is empty
# This ensures the app works on cloud deployments where ChromaDB is ephemeral
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    if count() == 0:
        from ingest import ingest_all
        with st.status("📚 Auto-ingesting documents...", expanded=True) as status:
            try:
                ingest_all()
                status.update(label="✅ Ingestion complete", state="complete")
            except Exception as e:
                status.update(label=f"❌ Ingestion failed: {e}", state="error")

st.title("🧠 RAG Document Q&A")
st.markdown("Ask questions about your ingested documents. Upload files or URLs via the sidebar.")

with st.sidebar:
    st.header("📊 Database")
    chunk_count = count()
    st.metric("Total Chunks", chunk_count)

    if st.button("🗑️ Clear Database", use_container_width=True):
        clear()
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.header("📤 Ingest Data")

    tab1, tab2 = st.tabs(["📁 Files", "🔗 URL"])

    with tab1:
        uploaded_files = st.file_uploader(
            "Choose PDF or image files",
            type=["pdf", "jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"upload_{st.session_state.upload_counter}"
        )

        if uploaded_files:
            progress = st.progress(0, text="Starting...")
            for i, f in enumerate(uploaded_files):
                progress.progress(
                    (i) / len(uploaded_files),
                    text=f"Processing {f.name}..."
                )
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=os.path.splitext(f.name)[1]
                ) as tmp:
                    tmp.write(f.getbuffer())
                    tmp_path = tmp.name
                try:
                    ext = os.path.splitext(f.name)[1].lower()
                    if ext == ".pdf":
                        docs = read_pdf(tmp_path)
                        if docs:
                            save_documents(docs)
                            st.success(f"✅ {f.name}: {len(docs)} chunks")
                    elif ext in (".jpg", ".jpeg", ".png", ".webp"):
                        doc = describe_image(tmp_path)
                        if doc:
                            save_documents([doc])
                            st.success(f"✅ {f.name}: 1 chunk")
                except Exception as e:
                    st.error(f"❌ {f.name}: {e}")
                finally:
                    os.unlink(tmp_path)
            st.session_state.upload_counter += 1
            st.rerun()

    with tab2:
        url = st.text_input("Webpage URL:", placeholder="https://example.com")
        if url and st.button("Ingest", type="primary", use_container_width=True):
            with st.spinner(f"Fetching {url}..."):
                try:
                    docs = read_url(url)
                    if docs:
                        save_documents(docs)
                        st.success(f"✅ {len(docs)} chunks added from URL")
                    else:
                        st.warning("No content could be extracted")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📎 View Sources"):
                for s in msg["sources"]:
                    st.caption(f"**{s['label']}** — score: {s['score']}")

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        results = None
        response = ""
        sources_display = []

        with st.status("🤔 Processing your question...", expanded=True) as status:
            status.write("🔍 Searching knowledge base...")
            results = get_relevant_chunks(prompt)

            if not results:
                status.update(label="❌ No relevant information found", state="error")
                response = "No relevant information found. Make sure you've ingested documents first."
            else:
                status.write(f"✅ Found {len(results)} relevant chunks")
                context = build_context(results)
                status.write("🤖 Generating answer...")
                response = generate_answer(prompt, context)
                status.update(label="✅ Answer ready", state="complete")

        st.markdown(response)

        if results:
            with st.expander("📎 View Sources"):
                for r in results:
                    meta = r["metadata"]
                    stype = meta.get("source_type", "?")
                    if stype in ("pdf", "pdf_image"):
                        label = f"{meta.get('file_name','?')} - page {meta.get('page_number','?')}"
                    elif stype == "url":
                        label = meta.get("url", "?")
                    elif stype == "image":
                        label = f"Image: {meta.get('file_name', '?')}"
                    else:
                        label = stype
                    st.caption(f"**{label}** — score: {r['score']}")
                    sources_display.append({"label": label, "score": r['score']})

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sources": sources_display
        })
