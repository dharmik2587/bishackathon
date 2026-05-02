# 🛡️ BIS Standards RAG Engine

[![Groq Powered](https://img.shields.io/badge/LLM-Groq-orange?style=for-the-badge&logo=ai)](https://groq.com)
[![Vite](https://img.shields.io/badge/Frontend-Vite%20%2B%20React-646CFF?style=for-the-badge&logo=vite)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com)

A high-performance **Retrieval-Augmented Generation (RAG)** engine prototype designed to simplify the discovery and recommendation of **Bureau of Indian Standards (BIS)** across various industries. This tool helps manufacturers and engineers identify applicable standards with zero hallucination and lightning-fast latency.

---

## 🚀 Key Features

- **Interactive RAG Query Engine**: Describe your product in plain natural language, and retrieve the exact IS codes you need.
- **Groq-Powered Reasoning**: Leverages `Llama-3` via Groq's high-speed inference for instant rationale generation.
- **Evaluation Dashboard**: Real-time metrics including Hit Rate @3, MRR @5, and average latency tracking.
- **Verified Grounding**: Every recommendation is linked to a specific context chunk from the BIS knowledge base to ensure technical accuracy.
- **Premium UI**: A sleek, dark-mode/glassmorphism inspired interface built for modern engineering workflows.

---

## 🛠️ Tech Stack

- **Frontend**: React 19 + Vite + TypeScript
- **Styling**: Tailwind CSS 4.0
- **Icons**: Lucide React
- **LLM Inference**: Groq Cloud API (Llama-3-8B)
- **State Management**: React Hooks

---

## 📦 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/dharmik2587/bishackathon.git
cd bishackathon
```

### 2. Install dependencies
```bash
npm install
```

### 3. Set up environment variables
Create a `.env` file in the root directory:
```env
VITE_GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the development server
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🏗️ Architecture Overview

The system follows a classic RAG pipeline:
1. **Query**: User inputs a product description.
2. **Retrieval**: System performs keyword and semantic similarity matching against the BIS Standards knowledge base.
3. **Augmentation**: Top relevant standards and context chunks are injected into the LLM prompt.
4. **Generation**: Groq LLM generates a grounded rationale explaining the applicability of each standard.

---

## 📊 Performance Targets

- **Latency**: < 2.0s average
- **Hit Rate @3**: > 85%
- **Hallucination Rate**: 0% (Strict Grounding)

---

## 🤝 Contributing

Contributions are welcome! This project was built for the **BIS Hackathon**.

---

Developed with ❤️ for the BIS Hackathon.
