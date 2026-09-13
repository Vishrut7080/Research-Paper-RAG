# Logs Markdown File
## RAG system for Research Papers

This file is to maintain a track of progress, objectives, tech stack and completion percentage of the whole project.

---

## 1. Quick Overview
- **Project Name:** MyRAG
- **Date Created:** 9 September 2026
- **Status:** In Progress
- **Author:** Vishrut

---

## 2. Key Objectives & Checklist
- [x] Initial setup and project scaffolding for RAG
- [x] Local System without Web Search
- [ ] Initial setup and project scaffolding for Web Dev
- [ ] Define system architecture and technical requirements
- [ ] Implement core features
- [ ] Conduct user testing and quality assurance
- [ ] Deploy to production

---

## 3. Architecture & Components

| Component | Responsibility | Tech Stack | Status |
| :--- | :--- | :--- | :--- |
| **RAG System** | | Sentence Transformer | In Progress
| **Frontend** | User Interface & Client Logic | React / TypeScript | Planned |
| **Backend API** | Business Logic & Auth | Python / FastAPI | In Progress |
| **Database** | Persistent Storage | PostgreSQL | Active |
| **Cache** | Session & Fast Lookups | Redis | Planned |

---

---

## 4. Issues faced and their status
| **Issue** | Resolved? | How? | Reason behind issue |
| :--- | :--- | :--- | :--- |
| **Chunking** | Yes | Had to decrease Chunking size from 150 to 50 | The chunk size for too big to run local system and I was also using print statement to print chunks.

---

## 5. Code Snippet Example

```python
def greet(name: str) -> str:
    \"\"\"Return a personalized greeting.\"\"\"
    return f"Hello, {name}! Ready to build something great?"

if __name__ == "__main__":
    print(greet("Developer"))