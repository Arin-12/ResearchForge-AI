# ResearchForge AI 🔬

### Multi-Agent AI Research Assistant for Automated Research Discovery, Analysis, and Report Generation

ResearchForge AI is an intelligent multi-agent research assistant built using **Google Agent Development Kit (ADK)** and **Groq Cloud**. It automates the research workflow by discovering relevant research papers and datasets, analyzing existing literature, identifying research gaps, generating structured research reports, and reviewing the final output.

The system uses specialized AI agents working together through a coordinated workflow to simplify and accelerate academic and technical research.

---

## 🚀 Key Features

- **Automated Research Discovery:** Searches for relevant research papers and datasets from platforms such as arXiv, Kaggle, Hugging Face, UCI, and OpenML.
- **Multi-Agent Architecture:** Uses specialized agents for research, analysis, report generation, and review.
- **Literature Analysis:** Extracts important findings, methodologies, and insights from discovered research.
- **Research Gap Identification:** Helps identify potential research gaps and future research directions.
- **Dataset Discovery:** Finds relevant datasets for proposed research topics.
- **Citation Validation:** Validates references and improves the reliability of generated research reports.
- **Structured Report Generation:** Produces organized Markdown research reports.
- **LLM Integration:** Uses Groq Cloud models through LiteLLM for efficient inference.
- **Error Handling:** Includes retry mechanisms and recovery handling for temporary API failures and rate limits.

---

## 🏗️ System Architecture

ResearchForge AI follows a sequential multi-agent research workflow.

```text
             User Research Query
                     |
                     ▼
             Research Agent
                     |
          Paper & Dataset Discovery
                     |
                     ▼
              Analysis Agent
                     |
          Literature Analysis
          Research Gap Detection
                     |
                     ▼
               Report Agent
                     |
           Structured Report
              Generation
                     |
                     ▼
              Reviewer Agent
                     |
          Quality & Citation Review
                     |
                     ▼
             Final Research Report
                     |
                     ▼
               outputs/
```

### Specialized AI Agents

| Agent | Responsibility |
|---|---|
| Research Agent | Discovers relevant papers and datasets. |
| Analysis Agent | Analyzes literature, methodologies, and research gaps. |
| Report Agent | Generates structured research reports. |
| Reviewer Agent | Reviews report quality and validates citations. |

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Agent Framework | Google Agent Development Kit (ADK) |
| LLM Provider | Groq Cloud |
| LLM Integration | LiteLLM |
| AI Models | Groq-hosted OpenAI GPT-OSS models |
| Research Sources | arXiv, Kaggle, Hugging Face, UCI, OpenML |
| Data Processing | Python |
| Output Format | Markdown |
| Version Control | Git and GitHub |

---

## 📂 Project Structure

```text
ResearchForge-AI/
│
├── researchforge/
│   ├── agents/
│   │   ├── research_agent.py
│   │   ├── analysis_agent.py
│   │   ├── report_agent.py
│   │   └── reviewer_agent.py
│   │
│   ├── tools/
│   │   ├── paper_search.py
│   │   ├── dataset_discovery.py
│   │   └── citation_validation.py
│   │
│   ├── utils/
│   │   └── output.py
│   │
│   ├── agent.py
│   ├── workflow.py
│   ├── config.py
│   ├── models.py
│   └── logging_config.py
│
├── outputs/
│   ├── .gitkeep
│   ├── sample_research_report_1.md
│   └── sample_research_report_2.md
│
├── main.py
├── requirements.txt
├── check_groq_models.py
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Arin-12/ResearchForge-AI.git
cd ResearchForge-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```powershell
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

---

## 📑 Sample Research Reports

ResearchForge AI generates detailed, well-structured research reports in Markdown format, bringing together relevant research papers, key findings, methodologies, and potential research directions.

The `outputs/` directory includes two sample reports generated using the system:

1. **[AI-Generated and Manipulated Academic Content Detection](outputs/Detecting_AI-Generated_and_Manipulated_Academic_Content_Usin_20261115_125436.md)**
2. **[Explainable AI for Early Detection of Cardiovascular Disease](outputs/Explainable_AI_for_Early_Detection_of_Cardiovascular_Disease_20261114_123807.md)**

These reports showcase how ResearchForge AI takes a research topic and turns it into an organized report, helping explore existing work, understand key research findings, and identify possible directions for further study.

## 🔄 Workflow

1. **Research:** Discover relevant research papers and datasets based on the user's topic.
2. **Analysis:** Examine existing literature, methodologies, findings, and research gaps.
3. **Report:** Generate a structured research report with relevant references.
4. **Review:** Review the generated report and validate citations.

---

## 🔮 Future Enhancements

- Integration with additional academic research databases.
- Advanced semantic search and vector-based retrieval.
- Improved citation verification and source-grounded generation.
- Interactive research dashboard.
- Export reports to PDF and DOCX.
- Research history and report management.
- Advanced multi-agent collaboration and evaluation.
