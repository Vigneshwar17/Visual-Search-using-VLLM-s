# 🔍 Visual Search using VLLM(s)

This project implements a **Visual Search system** powered by **Vision-Language Large Models (VLLMs)** like CLIP. Users can input natural language queries and the system first performs a local search using **pgvector** and CLIP embeddings stored in a PostgreSQL database. If no relevant match is found locally, it falls back to an **external API call** to fetch semantically matching images, ensuring optimal retrieval from both internal and external sources.

Demo Video Link - https://drive.google.com/file/d/10QXP-tAAf4WTF66EnV3CdLTr4lhobyGy/view?usp=sharing

---

## 📌 Features

- 🔎 Text-to-image search with natural language queries
- 🌐 External API integration for dynamic search
- 🧠 Local fallback using CLIP + pgvector + PostgreSQL
- ⚡ Fast inference powered by Flask and Python backend
- 🖼️ Visual embedding with OpenCV and CLIP
- 🧪 REST API with Flask, served to a React frontend

---

## 🧰 Tech Stack

**Frontend**
- React
- Vite.js
- Tailwind CSS

**Backend**
- Python
- Flask
- Node.js (optional bridge/API service)

**AI & Processing**
- CLIP Model (OpenAI)
- OpenCV
- External Image Search API

**Database**
- PostgreSQL with pgvector extension

---
## 🙋‍♂️ Author

- **Name**: Vigneshwar S
- **Email**: vigneshwar.codes@gmail.com  
- **GitHub**: https://github.com/Vigneshwar17

## 🤝 Collaborators

- **Name**: Gokulnath V  
  - **GitHub**: https://github.com/demon0211

- **Name**: Marishwaran A  
  - **GitHub**: https://github.com/Ultimatemarish
---

## 📄 License

This project is licensed under the **MIT License**.  
You're free to use, modify, and distribute this software with proper attribution.  
See the [LICENSE](./LICENSE) file for more details.


## ⚙️ Setup and Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/visual-search-vllm.git
cd visual-search-vllm

# Install frontend dependencies
cd client
npm install

# Install backend dependencies
cd ../server
pip install -r requirements.txt
