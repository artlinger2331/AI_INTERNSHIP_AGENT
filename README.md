<div align="center">
  
# 🤖 AI Internship Finder Agent

**Your Ultimate AI-Powered Career Copilot**

[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask Framework](https://img.shields.io/badge/Flask-Web_App-black.svg?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![LangChain Agent](https://img.shields.io/badge/LangChain-Agentic_AI-green.svg?style=for-the-badge&logo=langchain&logoColor=white)](https://python.langchain.com/)
[![OpenAI Model](https://img.shields.io/badge/OpenAI-GPT_Powered-white.svg?style=for-the-badge&logo=openai&logoColor=black)](https://openai.com)

*An intelligent, conversational AI platform designed to help students and job seekers find their perfect internships, featuring live resume parsing, real-time global internship search, and a stunning interactive streaming avatar.*

[Explore Features](#✨-key-features) • [Installation Guide](#🚀-quick-start) • [Architecture](#🛠️-system-architecture)

</div>

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 📄 **Smart Resume Parsing** | Upload a PDF resume to instantly extract your core skills, experience, and ideal roles using AI. |
| 💬 **Agentic AI Copilot** | Chat with a highly intelligent `gpt-3.5-turbo` LangChain agent for tailored career advice. |
| 🌍 **Live Job Aggregation** | Uses the RapidAPI Internships API to fetch real, active, and global internship postings in real-time. |
| 🎙️ **Live Streaming Avatar** | Integrated with **Akool Streaming Avatar** and **Agora RTC** for a futuristic, visually speaking AI assistant. |
| 🎨 **Premium UI/UX** | Built with an ultra-modern dark-themed glassmorphism interface featuring butter-smooth animations. |
| 🎯 **AI Mock Interview Pro** | A rigorous virtual interview experience utilizing webcam proctoring right in your browser. |

---

## 🛠️ Tech Stack

<details>
<summary><b>Backend Technologies</b></summary>
<br>

- **Python & Flask**: Core web server and routing.
- **LangChain & LangGraph**: AI orchestration and agentic tool usage.
- **SQLite Database**: Lightweight, zero-config relational database for user data and chat history.
- **PyPDF2**: Intelligent document reading for resume uploads.

</details>

<details>
<summary><b>Frontend Technologies</b></summary>
<br>

- **HTML5 & CSS3**: Custom-built responsive UI with glassmorphism styling.
- **Vanilla JavaScript**: State management, real-time chat manipulation, and dynamic job card rendering.
- **Agora Web SDK**: Real-time communication for live video avatar streaming.

</details>

---

## 🚀 Quick Start

Follow these steps to run the AI Internship Finder locally on your machine.

### 1. Prerequisites
Ensure you have the following installed and ready:
- **Python 3.8+**
- Git
- Active API Keys for **OpenAI**, **RapidAPI**, and **Akool** (if you want the avatar).

### 2. Clone & Install Dependencies
Open your terminal and run:

```bash
# Clone the repository
git clone https://github.com/artlinger2331/AI_INTERNSHIP_AGENT.git
cd AI_INTERNSHIP_AGENT

# Install all required Python packages
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory (where `app.py` is located) and add your keys securely:

```env
# 🧠 Required: For the AI to generate responses and parse resumes
OPENAI_API_KEY=sk-your-openai-api-key-here

# 🔍 Required: For fetching real internships
RAPIDAPI_KEY=your-rapidapi-key-here

# 👤 Required: For the Live Avatar to initialize and speak
AKOOL_API_KEY=your-akool-api-key-here

# 👤 Optional: The ID of the specific Akool Avatar model
AKOOL_AVATAR_ID=default_avatar
```
> **Note**: Ensure your OpenAI account has active billing credits, or the chatbot will return an `insufficient_quota` error.

### 4. Boot the Server
Start the production-ready server by running:

```bash
python app.py
```

### 5. Launch the Web App
Open your favorite web browser and navigate to:
```text
http://localhost:5000
```

---

## 🏗️ System Architecture

A high-level view of how the platform operates:

```mermaid
graph TD;
    User((User))-->|Uploads Resume / Chats|Frontend[Frontend UI HTML/JS];
    Frontend-->|API Requests|Backend[Flask Server app.py];
    Backend-->|Parses Text|PyPDF2[Resume Parser];
    Backend-->|Query Processing|LangChain[LangChain Agent];
    LangChain-->|Generates Response|OpenAI[OpenAI GPT];
    LangChain-->|Executes Tool|RapidAPI[RapidAPI Internships];
    Backend-->|Stores History|SQLite[(SQLite Database)];
    Frontend-->|Initializes Video Stream|Akool[Akool Avatar Engine];
    Akool-->|WebRTC Stream|Agora[Agora Network];
    Agora-->|Video/Audio|User;
```

---

## 💡 Troubleshooting Guide

- **`insufficient_quota` Error**: The chatbot will warn you if your OpenAI API key has run out of funds. Go to [platform.openai.com](https://platform.openai.com/) to add credits.
- **Avatar Not Showing Up**: Ensure your `AKOOL_API_KEY` is correct. If the API key is missing or invalid, the app gracefully falls back to a standard text chatbot.
- **No Internships Found**: Ensure your `RAPIDAPI_KEY` is valid. Our system includes a safe fallback to a local mock database if the external API fails.

---

<div align="center">
  <p>Built with ❤️ for the next generation of professionals.</p>
</div>
