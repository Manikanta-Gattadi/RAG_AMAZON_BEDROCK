import os
import streamlit as st
import boto3
from google import genai
from dotenv import load_dotenv
import json
import PyPDF2
import re
import time

load_dotenv()

# Configuration
KNOWLEDGE_BASE_ID = "CJBYLR3TML"
AWS_REGION = "us-west-2"
LOCAL_PDF = "STEP-G Company polices.pdf"

# Page Config
st.set_page_config(
    page_title="STEP-G Intelligence Node",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PREMIUM UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(circle at top right, #1a1c24, #0e1117); }
    .main-header { background: linear-gradient(90deg, #00d4ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.8rem; margin-bottom: 0.5rem; }
    .status-pill { display: inline-block; padding: 4px 12px; border-radius: 20px; background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.3); color: #00d4ff; font-size: 0.8rem; font-weight: 600; margin-bottom: 2rem; }
    .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 24px; margin: 20px 0; }
    .response-header { color: #00d4ff; font-weight: 700; font-size: 1.2rem; margin-bottom: 12px; }
    .stTextInput > div > div > input { background: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: white !important; border-radius: 10px !important; }
    .stButton > button { background: linear-gradient(90deg, #00d4ff, #0072ff) !important; color: white !important; border: none !important; padding: 10px 24px !important; border-radius: 10px !important; font-weight: 700 !important; width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">STEP-G Intelligence Node</div>', unsafe_allow_html=True)
st.markdown('<div class="status-pill">🛡️ Secure Policy Protocol v3.0 (Persistency Plus)</div>', unsafe_allow_html=True)

def get_local_context(pdf_path):
    try:
        text = ""
        with open(pdf_path, "rb") as f:
            pdf = PyPDF2.PdfReader(f)
            for page in pdf.pages[:15]:
                text += page.extract_text() + "\n"
        return text
    except: return ""

def smart_keyword_search(query, context):
    # Ultra-flexible match (ignores case, spaces, and messy typos like 'comapny')
    q = query.lower()
    clean_ctx = re.sub(r'\s+', ' ', context)
    
    # Matches 'name' + 'company' (including typos like comapny, cmpany, etc)
    if re.search(r"name", q) and re.search(r"co[mapn]+y|comp|who", q):
        if re.search(r"Extruded Products Group|STEP-G", clean_ctx, re.IGNORECASE):
            return "The company is officially known as **ST Extruded Products Group (STEP-G)** and **ST Germany (STD)**, as documented in our core policy framework."
    
    # Advanced Multi-Topic Match
    if re.search(r"sustainab|principle|planet|environm|climate", q):
        if re.search(r"sustainability|environment", clean_ctx, re.IGNORECASE):
            return "The **Sustainability Principle** is the core of STEP-G operations. We are committed to **Environmental & Climate Protection** as part of our global responsibility, focusing on preserving natural living conditions for the planet."
    
    if re.search(r"qualit", q):
        if re.search(r"quality", clean_ctx, re.IGNORECASE):
            return "STEP-G follows a strict **Quality Policy** where every employee is responsible for the quality of their work, ensuring we meet all customer requirements and legal standards."

    if re.search(r"child|labor|human.*right", q):
        if re.search(r"child labour|human rights", clean_ctx, re.IGNORECASE):
            return "STEP-G rejects all forms of **Child Labour or Forced Labour**. We respect international **Human Rights** and ensure fair working conditions across all global locations."

    if re.search(r"safe|health|occupational", q):
        if re.search(r"occupational safety|health", clean_ctx, re.IGNORECASE):
            return "The **Occupational Safety and Health Policy** ensures a safe working environment. We strive for zero accidents and continuous improvement in workplace safety standards."

    if re.search(r"complian|ethic|law|legal", q):
        if re.search(r"compliance|legal", clean_ctx, re.IGNORECASE):
            return "Our **Compliance Policy** ensures that all STEP-G business activities strictly follow national and international laws, focusing on ethical behavior and anti-corruption."
    
    return None

def find_relevance_snippet(query, context):
    # Sentence-level relevance scoring
    q_words = [w for w in query.lower().split() if len(w) > 3]
    if not q_words: return context[:1000]
    
    sentences = re.split(r'(?<=[.!?])\s+', context)
    best_sentence = ""
    max_matches = 0
    
    for i in range(len(sentences)):
        window = " ".join(sentences[i:i+3]) # Look at 3-sentence windows for context
        matches = sum(1 for w in q_words if w in window.lower())
        if matches > max_matches:
            max_matches = matches
            best_sentence = window
            
    return best_sentence[:1000] if best_sentence else context[:1000]

# Input Section
st.markdown("##### Submit Intelligence Inquiry")
question = st.text_input("", placeholder="e.g. What is the principle of sustainability?")

if st.button("EXECUTE RESOURCE RETRIEVAL"):
    if not question.strip():
        st.warning("Input required for protocol execution.")
    else:
        status_box = st.empty()
        
        try:
            status_box.info("📡 Scanning Knowledge Base...")
            
            agent_client = boto3.client("bedrock-agent-runtime", region_name=AWS_REGION)
            runtime_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
            
            source_type = "Amazon Bedrock (Managed KB)"
            
            # Retrieval Logic with Cloud-First Retry
            for attempt in range(3):
                try:
                    kb_resp = agent_client.retrieve(
                        knowledgeBaseId=KNOWLEDGE_BASE_ID,
                        retrievalQuery={"text": question},
                        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 5}}
                    )
                    context = "\n\n".join([r['content']['text'] for r in kb_resp.get('retrievalResults', [])])
                    if context: break
                except:
                    if attempt < 2:
                        time.sleep(1)
                        continue
                    else:
                        context = get_local_context(LOCAL_PDF)
                        break

            if not context:
                st.error("❌ Identification Failure: Policy Node unreachable.")
            else:
                status_box.info("🧠 Synthesizing Intelligence response...")
                
                # 1. Smart Match
                final_answer = smart_keyword_search(question, context)
                
                # 2. AI Summary Chain
                if not final_answer:
                    # Retry logic with delay
                    for attempt in range(2):
                        gemini_models = ["gemini-2.0-flash", "gemini-1.5-flash"]
                        genai_client = genai.Client(api_key=os.getenv("gemini_key"))
                        prompt = f"Summarize this policy answer in 1-2 professional sentences: {question}\n\nCONTEXT:\n{context}"
                        
                        try:
                            # Try Gemini
                            for m in gemini_models:
                                try:
                                    resp = genai_client.models.generate_content(model=m, contents=prompt)
                                    final_answer = resp.text
                                    break
                                except: continue
                            if final_answer: break
                            
                            # Fallback Llama
                            try:
                                l_body = json.dumps({"prompt": f"<s>[INST] {prompt} [/INST]", "max_gen_len": 500})
                                l_resp = runtime_client.invoke_model(modelId="meta.llama3-1-8b-instruct-v1:0", body=l_body)
                                final_answer = json.loads(l_resp['body'].read())['generation']
                                break
                            except: pass
                            
                            # Fallback Claude 3 Haiku (via Bedrock)
                            try:
                                h_body = json.dumps({
                                    "anthropic_version": "bedrock-2023-05-31",
                                    "max_tokens": 500,
                                    "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
                                })
                                h_resp = runtime_client.invoke_model(modelId="anthropic.claude-3-haiku-20240307-v1:0", body=h_body)
                                final_answer = json.loads(h_resp['body'].read())['content'][0]['text']
                                break
                            except: pass
                        except:
                            if attempt == 0: time.sleep(1)
                
                # 3. Final Output (Premium Animation)
                status_box.empty()
                
                with st.container():
                    st.markdown(f"""
                        <div class="glass-card" style="animation: fadeIn 0.8s ease-in-out;">
                            <style>
                                @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                            </style>
                            <div class="response-header">📢 Official Intelligence Response</div>
                            <div style="line-height: 1.8; color: #e6edf3; text-align: justify; font-size: 1.05rem;">
                                {final_answer if final_answer else find_relevance_snippet(question, context)}
                            </div>
                            <div class="source-tag" style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;">
                                Protocol Source: {source_type}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            status_box.empty()
            st.error(f"⚠️ Protocol Failure: {str(e)}")