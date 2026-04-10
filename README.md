# 🛡️ STEP-G Intelligence Node

An enterprise-grade, high-resilience Q&A system powered by **Amazon Bedrock** and **Google Gemini**. Designed for the **ST Extruded Products Group (STEP-G)** to provide instant, summarized policy intelligence.

## 🚀 Key Features

*   **Triple-Layer Hybrid RAG**:
    1.  **Primary**: Amazon Bedrock Knowledge Base (VPC Retrieval).
    2.  **Secondary**: Google Gemini Multi-Model Fallback (2.0 Flash, 1.5 Flash).
    3.  **Tertiary**: Local Policy Intelligence Node (regex-based fuzzy matching).
*   **Premium Glassmorphism UI**: A stunning, modern dark-themed dashboard with animated transitions and high-performance layout.
*   **Absolute Resilience**: Implemented intelligent retry loops and automatic quota rotation to bypass AWS throttling and API rate limits.
*   **Typo-Resistant Search**: Natural language processing logic capable of handling common user typos (e.g., "comapny") to ensure a seamless experience.

## 🛠️ Architecture

The system utilizes a **Cloud-First** strategy. It prioritizes retrieval from the managed Amazon Bedrock Knowledge Base. If cloud resources are throttled or unreachable, it silently transitions to a local high-performance indexing engine to maintain 100% uptime.

## 📦 Setup & Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/step-g-intelligence-node.git
    cd step-g-intelligence-node
    ```

2.  **Environment Configuration**:
    Create a `.env` file in the root directory:
    ```env
    gemini_key=your_google_gemini_api_key
    AWS_REGION=us-west-2
    ```

3.  **Install Dependencies**:
    ```bash
    pip install boto3 streamlit google-genai python-dotenv PyPDF2
    ```

4.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for more information.

---
**Developed for the STEP-G Corporate Excellence Initiative.** 🏢🤖🚀🦾💎✨
