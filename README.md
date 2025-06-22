# 🌟 Orbit Agent — AI-Powered Intelligent Workflow Orchestrator

## 🚀 Overview

**Orbit Agent** is an AI-driven orchestration system that makes it easy to automate and manage workflows across multiple business functions using plain language instructions.

With Orbit Agent, you don’t need to learn complex tools or write code — just **tell it what you want**, and it designs, deploys, and runs reliable automation workflows in the background.

---

## 🎯 Key Highlights

- **Natural Conversation:** Talk or type naturally — no rigid commands needed.
- **Smart Automation:** AI understands your intent and builds workflows dynamically.
- **Reusable Templates:** Uses trusted, pre-tested workflow blocks for reliability.
- **Memory:** Remembers previous tasks, preferences, and improves over time.
- **Voice-Enabled:** Interact using speech; get clear spoken responses.

---

## 🧩 How It Works

Orbit Agent is structured in three powerful layers:

### ✅ 1️⃣ Execution Layer — **n8n Workflows**

- At the core of Orbit Agent’s execution power is **n8n**, a trusted no-code automation platform.
- **What’s inside?**
  - A curated library of workflow templates for common tasks like onboarding, approvals, content publishing, CRM actions, and IT tasks.
  - Each template is modular — it does one thing well and includes placeholder fields for easy customization.
- **How it’s used:**
  - The agent selects the right template(s), fills in dynamic details (like names, emails, or dates), and runs them using n8n’s visual workflow engine.
- This ensures each workflow is secure, traceable, and easily adjustable in the visual editor if needed.

---

### ✅ 2️⃣ Intelligence Layer — **Unified AI Agent - Sun Agent**

- Orbit Agent uses **LangChain** and **Mistral AI** to process user input and plan how to turn requests into action.
- It:
  - Understands both short commands and complex multi-step requests.
  - Decides which templates or workflow blocks to use.
  - Connects multiple templates if a single workflow spans multiple departments.
  - Adapts workflows on the fly based on context and user input.

---

### ✅ 3️⃣ Learning Layer — **ChromaDB**

- Every time you use Orbit Agent, it learns a bit more.
- **ChromaDB** acts as a smart memory, storing:
  - Past workflows and their configurations.
  - How workflows were adapted or customized.
  - Relationships between tasks and departments.
- This allows the agent to:
  - Recommend relevant workflows.
  - Personalize responses.
  - Make better choices the next time you ask.

---

## 🤝 Meet Your AI Copilots

Orbit Agent comes with **two specialized assistants**, each playing a unique role to make workflow automation easy and intelligent.

### ☀️ **Sun Agent**


- It handles:
  - Quick answers about your processes.
  - Small, routine tasks that don’t need a full workflow.
  - Simple queries like *“What workflows are available for Marketing?”* or *“Show me today’s deployments.”*
- Sun Agent is always available to keep your work moving smoothly with instant responses.

### ⭐ **Star Agent**


- It takes on:
  - Designing complex workflows end-to-end.
  - Combining multiple workflow blocks to handle big tasks — like onboarding a new hire that touches HR, IT, and CRM all at once.
  - Deploying the complete workflow into your n8n system automatically.
- It doesn’t just run existing workflows — it can **generate new ones dynamically** based on your instructions and store them for future use.

Together, Sun and Star Agents work side-by-side to handle everything from simple requests to sophisticated, multi-step processes.

---

## 🔍 What Orbit Agent Can Automate

Orbit Agent comes with extensive coverage across core business areas:

### ✅ **HR Operations**
- Automate employee onboarding and offboarding.
- Manage performance reviews from scheduling to result tracking.
- Draft and deliver offer letters with candidate details.

### 📣 **Marketing**
- Schedule and publish social media or blog content.
- Monitor SEO health and generate reports.
- Run digital marketing campaigns with tracking and reporting.

### 📊 **Sales & Analytics**
- Generate revenue forecasts.
- Send monthly sales summaries to managers.
- Analyze customer behavior and buying trends.

### 💬 **CRM & Support**
- Automate customer journey touchpoints, follow-ups, and support ticket flows.
- Maintain consistent communications throughout the customer lifecycle.

### 💻 **IT Automation**
- Manage GitHub repository updates, pushes, and file monitoring.
- Provision user accounts, manage permissions, and handle access control automatically.

---

## 🧠 How Orbit Agent Thinks & Improves

Here’s how every request flows through the system:

1. **Understand:** The agent processes what you type or say.
2. **Search:** Finds the best matching workflow templates in ChromaDB.
3. **Adapt:** Fills in dynamic details you provide — no manual edits needed.
4. **Compose:** Links multiple templates if the task requires steps across domains.
5. **Deploy & Execute:** Builds the final workflow, sends it to n8n, and runs it live.
6. **Learn:** Saves successful workflows and context to make next time faster and more accurate.

---

## ⚙️ Tech Stack

| Layer | Tools | Purpose |
| ----- | ----- | ------- |
| **Reasoning & Planning** | LangChain, Mistral AI | Understand and process user instructions |
| **Execution** | n8n + n8n API | Run automations securely and visually |
| **Memory & Context** | ChromaDB | Store workflows, embeddings, and usage context |
| **Backend** | FastAPI, Python | API endpoints and orchestration logic |
| **Frontend** | Streamlit | Clean chat-based interface |



---

## 📌 Realistic Example Workflows

**Human Resources:**  
- Onboard new employees across HR, IT, and CRM.
- Manage exit checklists and asset recovery.
- Run periodic performance reviews.

**Marketing:**  
- Schedule cross-platform content with automated reminders.
- Pull SEO metrics and compile them into a report.
- Execute multi-step campaign launches with analytics.

**Sales & CRM:**  
- Create sales forecasts using historical data.
- Generate automated customer insights reports.
- Manage follow-up workflows for leads.

**IT Operations:**  
- Automate routine GitHub updates and push actions.
- Provision or revoke user accounts with correct permissions.

---

## 🚀 Get Started

1. Clone this repository.
2. Install all Python dependencies:
   ```bash
   pip install -r requirements.txt
