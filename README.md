# 🧪 LLM Benchmark Studio — Multi-Model Landing Page Generator

<p align="center">
  <img src="https://img.shields.io/badge/LLM-OpenAI%20|%20Claude%20|%20Gemini-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Streamlit-Interactive%20App-red?style=for-the-badge">
  <img src="https://img.shields.io/badge/Benchmark-Multi%20Model-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/GenAI-Content%20Generation-yellow?style=for-the-badge">
</p>

<p align="center">
  A Streamlit application for generating landing pages with multiple LLMs and comparing outputs side-by-side with live previews.
</p>

---

## 📌 Overview

LLM Benchmark Studio enables structured comparison of landing page generation across multiple large language models.

The system:

- Generates HTML landing pages from a single prompt  
- Benchmarks outputs across models  
- Displays live rendered previews  
- Tracks performance metrics per model  

---

## ✨ Features

- 🤖 Multi-LLM support (GPT-4o-mini, Claude 3.5 Sonnet, Gemini 2.0 Flash)  
- 🖥 Live HTML preview (iframe rendering)  
- 📊 Side-by-side model comparison  
- ⏱ Generation time & output size tracking  
- 🎚 Adjustable max token control (500–4000)  
- 📥 Download generated HTML  
- 🔍 Expandable source code viewer  
- 🎨 Clean, modern Streamlit UI  

---

## ⚙️ Tech Stack

| Technology | Usage |
|------------|--------|
| Python | Core development |
| Streamlit | Web interface |
| OpenAI API | GPT models |
| OpenRouter API | Claude & Gemini access |
| HTML/CSS | Generated landing pages |

---

## 🚀 Getting Started

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Configure Environment

Create a `.env` file:

```env
OPENAI_API_KEY=your-key
OPENROUTER_API_KEY=your-key
```

At least one key is required.

### 3️⃣ Run Application

```bash
streamlit run app.py
```

App runs at:

```
http://localhost:8501
```

---

## 🧠 How It Works

1. User enters product/service description  
2. Selected LLMs generate landing page HTML  
3. Outputs are rendered in embedded previews  
4. Performance metrics are logged  
5. User can inspect or download any version  

---

## 📂 Project Structure

```
├── app.py
├── sample_outputs/
├── requirements.txt
├── .env.example
└── notebook/
```
## 👨‍💻 Author 
**Vashishtha Verma** 
* 🤖 Machine Learning & Generative AI
* 🧠 Agentic AI Systems
* 💻 Software Engineering & DSA

## 📄 License

MIT License.
