# Agentic RAG App: Multi-Agent Research & Writing Pipeline


[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Workflows-24292e?style=for-the-badge)](https://github.com/langchain-ai/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Empowering autonomous research through a collaborative multi-agent architecture built on LangGraph.**

This project implements an advanced **Agentic RAG (Retrieval-Augmented Generation)** pipeline. Unlike traditional RAG systems that follow a linear path, this application utilizes a choreography of specialized agents—Planner, Researcher, Writer, and Critic—to iteratively research, draft, and refine high-quality content.

---

##  Architecture & Flow

The system operates as a stateful graph where each node represents an agent. The flow is cyclical, allowing the system to learn from its own drafts through a feedback loop.

```mermaid
graph TD
    subgraph Input_Layer ["User Interface"]
        UserQuery["User Question"]
    end

    subgraph Core_Engine ["LangGraph Multi-Agent Workflow"]
        Planner{{"Planner Node<br/>(Structured Strategy)"}}
        Researcher[["Researcher Node<br/>(Knowledge Synthesis)"]]
        Writer[["Writer Node<br/>(Draft Generation)"]]
        Critic{{"Critic Node<br/>(Feedback & Scoring)"}}
        Finalizer[["Finalizer Node<br/>(Polished Delivery)"]]
    end

    UserQuery --> Planner
    Planner --> Researcher
    Researcher --> Writer
    Writer --> Critic
    
    Critic -->|"Score < 80"| Writer
    Critic -->|"Score >= 80"| Finalizer
    
    Finalizer --> Output["Final Answer"]

    %% Styling for clarity
    style Planner fill:#1a237e,stroke:#0d47a1,stroke-width:2px,color:#fff
    style Critic fill:#311b92,stroke:#4527a0,stroke-width:2px,color:#fff
    style Researcher fill:#004d40,stroke:#00695c,stroke-width:2px,color:#fff
    style Writer fill:#01579b,stroke:#0277bd,stroke-width:2px,color:#fff
    style Finalizer fill:#bf360c,stroke:#d84315,stroke-width:2px,color:#fff
    style UserQuery fill:#f5f5f5,stroke:#333,stroke-width:2px
    style Output fill:#f5f5f5,stroke:#333,stroke-width:2px
    
    linkStyle 4,5 stroke:#ffab00,stroke-width:3px;
```

