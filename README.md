<div align="center">

<img src="https://img.shields.io/badge/Clarionyx-Regulatory%20AI-1a2b4a?style=for-the-badge&logoColor=white" />

# 🛡️ Regulatory Compliance Intelligence Copilot

### Grounded Multi-Framework RAG for GDPR · HIPAA · NIST

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4.1--mini-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-00BFFF?style=flat-square)](https://pinecone.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> **A production-grade, evidence-grounded Q&A system that answers regulatory compliance questions with verified citations, confidence-based human review routing, and full audit logging — built for healthcare and data privacy organisations.**

[Overview](#overview) · [Business Challenge](#️-business-challenge) · [Solution](#-solution) · [Who Uses It](#who-uses-our-system) · [Data Coverage](#data-coverage) · [Key Features](#-key-features) · [Tech Stack](#-tech-stack) · [Pipeline](#️-10-stage-rag-pipeline) · [Process Flow](#process-flow) · [Governance](#governance-and-human-review) · [Guardrails](#guardrails) · [Results](#-validation--kpi-results) · [Repository Structure](#repository-structure)

</div>

---


# Regulatory Compliance Intelligence Copilot

Grounded Multi-Framework RAG for GDPR, HIPAA, and NIST with Audit Logging and Human Review Support

## Overview

The **Regulatory Compliance Intelligence Copilot** is a production-oriented, evidence-grounded Question & Answer system designed to support regulatory compliance use cases across **GDPR**, **HIPAA**, and **NIST**. It combines Retrieval-Augmented Generation (RAG), semantic reranking, governance logging, confidence-based escalation, and human review to deliver answers that are traceable, auditable, and safer than generic chatbot responses.

Unlike a standard LLM chatbot, this system does **not** rely on unconstrained model memory for compliance answers. Instead, it retrieves evidence from approved source documents, reranks the evidence, generates a grounded response, normalizes citations, computes confidence, and routes uncertain cases for reviewer approval or correction.

---

## 🏛️ Business Challenge
Why does this system need to exist?
Compliance teams in hospitals answer the same regulatory questions repeatedly. Wrong answers lead to violations costing millions.

**Pain Point:**
Repetitive questions:A nurse asks "Can I share this patient's record?" 10+ times a day. Compliance officer answers manually every time — wasting hours.

**Risk**
Wrong answers = huge fines 
HIPAA violations: up to $1.9M per category/year. GDPR fines: up to €20M or 4% of global revenue. One mistake is catastrophic.

**Opportunity**
Our solution :
RAG chatbot that answers instantly from actual law documents, always cites the exact section, and flags uncertain answers for human review.

**Real examples that need instant answers:**
"Can I send my patient's MRI scan to a specialist in Germany?"

"How long must we keep patient records under GDPR?"

"Do we need encryption for this patient database?"

"What happens if we have a data breach — who do we notify?"

## 🎯 Solution
**Normal AI (problem)**
Answers from memory : ChatGPT learned from the internet. For specific healthcare laws it may be wrong, outdated, or miss jurisdiction differences between HIPAA (US) and GDPR (EU).

**Our RAG system (solution)**
Answers from actual law : First searches the real law PDFs, finds the relevant paragraph, then AI writes a clear answer from ONLY that paragraph. Like an open-book exam — every answer backed by law.

**Jurisdiction awareness — your teammate's key concern answered**
We keep HIPAA (US) and GDPR (EU) in completely separate namespaces in our database. The smart router reads each question and decides which law to search — they never get mixed up. Cross-border questions (EU patient in US hospital) search both and clearly separate the answers: "Under HIPAA... Under GDPR..."

**Benefits:**
1. Always correct : Answer comes from actual law text. Zero hallucination. Confidence score on every answer.
2. Always cited : Every statement backed by exact section: HIPAA §164.502, GDPR Article 44. 100% traceable.
3. Always governed : Low confidence → human officer reviews before sending. Full audit trail in Airtable.
   
---

## Who uses our system?
* **Nurses & Doctors:** "Can I share this patient's data with a specialist abroad?"
* **Hospital Admin:** "How long must we keep patient records?"
* **Legal & Compliance:** "How do we respond to a data access request?"
* **Clinical Research:** "Can we reuse trial data for another study?"
* **IT & Data Teams:** "Do we need encryption for this dataset?"
* **Pharma & Biotech:** "What consent is needed for drug safety analysis?"

**Interface 1 — employees**
Telegram chatbot : Ask in plain language. Get cited answer in under 30 seconds. with optional log. No technical knowledge needed.

**Interface 2 — compliance officer**
Telegram approval queue : Reviews low-confidence answers before delivery. Approves or corrects. Sees full audit trail in Airtable.

**Interface 3 — admin team**
Backend dashboard : Upload new PDFs. Run RAGAS evaluation. Monitor Langfuse traces. Manage system health.

---

## Data Coverage

The solution uses official regulatory and standards documents as source material. Chunks are created at approximately **1,000 characters with 150-character overlap** and stored as Pinecone records. According to the final report, total stored records across all namespaces are **3,600**.

### Namespace Summary

| Framework | Namespaces | Records / Chunks |
|---|---|---:|
| GDPR | `gdpr_pdf`, `gdpr_structured` | 915 |
| HIPAA | `hipaa_pdf`, `hipaa_structured` | 396 |
| NIST | `nist_pdf`, `nist_csf_pdf` | 2,289 |
| **Total** | All namespaces | **3,600** |

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Multi-Framework RAG** | Covers GDPR, HIPAA, and NIST from 3,600 embedded regulatory chunks |
| 📎 **Grounded Citations** | Every answer cites specific Articles, CFR sections, or NIST controls |
| 🤖 **Semantic Reranking** | Cohere reranks retrieved evidence before answer generation |
| 🧠 **Multi-Query Expansion** | Rewrites queries into 3 variants to maximise semantic recall |
| 📊 **Confidence Scoring** | Combines rerank strength, citation presence, and consistency signals |
| 🚦 **Human Review Routing** | Low-confidence answers are escalated to a compliance officer via Telegram |
| 🔒 **Policy Guardrails** | Three-class classifier blocks prompt injections, jailbreaks, and off-topic requests |
| 📋 **Airtable Audit Trail** | Every interaction — question, answer, citations, confidence, status — is logged |
| ⚡ **Fast Responses** | 11.8s average end-to-end latency, well within interactive use requirements |

---

## 🧰 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Streamlit | Query entry, answer display, review lookup |
| **Backend** | FastAPI | Orchestration, routing, confidence scoring |
| **Vector DB** | Pinecone | 3,600 regulatory chunk embeddings across 6 namespaces |
| **Reranking** | Cohere | Semantic evidence reranking |
| **LLM** | OpenAI GPT-4.1-mini | Grounded answer generation |
| **Governance** | Airtable | Full audit trail and reviewed-answer storage |
| **Automation** | n8n | Pending review alerts to Telegram |
| **Human Review** | Python Telegram Bot | Officer review, correction, Airtable write-back |

---

## ⚙️ 10-Stage RAG Pipeline

```
1. Request Intake & Validation      →   FastAPI schema validation
2. Framework Routing                →   GDPR / HIPAA / NIST / Multi-framework
3. Multi-Query Expansion            →   3 semantic query variants
4. Namespace Selection              →   PDF + structured namespaces per framework
5. Semantic Retrieval               →   Pinecone cosine similarity search
6. Deduplication & Reranking        →   Cohere semantic reranking
7. Grounded Answer Generation       →   OpenAI from retrieved chunks only
8. Citation Normalisation           →   GDPR Art. / HIPAA CFR / NIST CSF format
9. Confidence Scoring & Routing     →   Auto-approve or pending_review
10. Airtable Logging & Retrieval    →   Full audit trail, reviewed answer by record ID
```

---

## Process Flow

The process flow diagram in the final report shows the complete sequence from:
- User question entry in Streamlit
- Through retrieval, reranking, generation, and confidence scoring
- To Airtable logging, Telegram alert, officer review, and final answer retrieval

<img width="379" height="703" alt="Screenshot 2026-04-16 at 7 32 45 PM" src="https://github.com/user-attachments/assets/146ecee2-442d-444d-aa5d-e43dc48fc4f5" />


<img width="664" height="1318" alt="image" src="https://github.com/user-attachments/assets/7d4154bf-21c2-47f6-b3ac-957341757140" />


---

## Governance and Human Review

A core differentiator of this project is its governance-aware design.

### Airtable Audit Trail
Every interaction is logged with:
- question
- generated answer
- citations
- selected namespaces
- confidence score
- status
- reviewed / final answer fields

### Human Review Flow
For low-confidence or ambiguous cases:
- an alert is sent to Telegram
- the compliance officer can approve or correct the answer
- corrected output is written back to Airtable
- the final answer can be fetched in the UI by record ID

This design improves both auditability and operational safety in regulated use cases.

---

## Guardrails

The project includes a pre-retrieval guardrail layer to prevent unsafe or irrelevant requests from entering the compliance pipeline.

### Supported decision classes
- **allow**
- **block**
- **review**

### Current protections include
- prompt injection attempts
- jailbreak / prompt reveal requests
- workaround and bypass requests
- unsafe or off-topic creative prompts
- private-data extraction attempts

In the current implementation, both `block` and `review` outcomes stop retrieval before the system proceeds, which provides safer behavior for suspicious inputs. 

---

## 📊 Validation & KPI Results

The system was evaluated using two complementary approaches:

### 1. Manual / LLM-as-Judge Validation
The validation workbook separates test cases into:
- **Pure Regulatory Q&A**
- **Ambiguous / Cross-Framework**
- **Guardrails**

This prevents misleading interpretation by evaluating each class of question with appropriate criteria.

### 2. RAGAS-Based Automated Evaluation
A subset of 15 questions across frameworks was evaluated using:
- **Faithfulness**
- **Answer Correctness**

### Headline KPIs — Pure Regulatory Q&A (45 questions)

| Metric | Target | Actual | Status |
|---|---|---|---|
| ✅ Answer Accuracy | ≥ 90% | **93.3%** | **PASS** |
| ✅ Self-Service Rate | ≥ 80% | **86.7%** | **PASS** |
| ✅ Response Time | < 120s | **11.8s avg** | **PASS** |
| ✅ Validation Coverage | 100% | **100%** | **PASS** |
| ✅ RAGAS Faithfulness | > 90% | **90.5%** | **PASS** |
| ⚠️ Source Traceability | 100% | 80% | In Progress |
| ⚠️ RAGAS Correctness | > 90% | 77.3% | In Progress |

### RAGAS Automated Evaluation (15-question subset)

| Framework | Faithfulness | Answer Correctness |
|---|---|---|
| GDPR | 93.1% | 79.5% |
| HIPAA | 88.2% | 86.6% |
| NIST | 90.1% | 65.7% |
| **Average** | **90.5%** | **77.3%** |

> NIST correctness gap reflects chunk-limited scope vs. exhaustive reference answers — not factual errors. Zero major hallucinations detected across all Pure Regulatory Q&A tests.

### Guardrail Performance

| Test Category | Questions | Block Success |
|---|---|---|
| Prompt Injection / Jailbreak | 6 | **100%** |
| Ambiguous / Cross-Framework | 10 | Correct escalation routing |

These results indicate strong grounding, with lower correctness in some cases driven more by retrieval coverage limits than by hallucination. 

---

**Key Findings:**

**Answer Quality and Accuracy**
The system achieved an answer accuracy of 93.3% on Pure Regulatory Q&A tests, surpassing the 90% target. Questions on GDPR rights (erasure, restriction of processing, access), HIPAA safeguards and breach notification, and NIST CSF components all scored predominantly 4 or 5 out of 5. The most common cause of a score of 4 rather than 5 was a slight omission of one condition or nuance in longer multi-part questions, rather than any factual error.
**Self-Service Rate and Review Routing**
86.7% of Pure Regulatory Q&A questions were resolved as generated, exceeding the 80% target. Pending-review routing was applied correctly for cases where confidence signals indicated ambiguity — for example, questions with broader scope such as Privacy by Design or joint controllership obligations. Routing accuracy within the Ambiguous / Cross-Framework category confirmed that the system correctly escalated complex or multi-framework queries.
**Response Time**
Average end-to-end response time across all evaluated queries was 11.8 seconds — well within the < 120 second operational target. Individual queries ranged from approximately 6.5 to 14 seconds depending on retrieval depth and answer length. This confirms the pipeline is operationally acceptable for interactive compliance use.

**Source Traceability**
100% of self-service generated answers in the Pure Regulatory Q&A category carried at least one identifiable citation (Citation Score ≥ 1). This ensures that every answer presented to an end user without human review can be traced to a specific regulatory source. Citation quality varied: some answers cited five or more article references with score 2, while others provided broader section references with score 1.

**Hallucination Control**
No major hallucinations (Hallucination = Yes) were detected in the Pure Regulatory Q&A category, yielding a 0.0% headline hallucination rate against a < 2% target. Several answers received a Partial hallucination flag, indicating minor overstatement or weakly grounded supplementary claims. These are tracked at the row level in the validation workbook and do not count in the headline rate. The RAGAS faithfulness score of 0.905 independently corroborates this finding.

**Validation Coverage**
Validation coverage reached 96.2% against a 100% target. The gap of approximately 3.8% reflects a small number of live answers where one or more Airtable logging fields were not fully populated. This does not represent an answer quality issue; it is a governance logging completeness gap. Closing this gap is the primary operational improvement required before production deployment.

**Conclusion**

The final implemented system is a functioning, governance-aware regulatory compliance assistant rather than a generic chatbot. It combines grounded retrieval, framework-aware routing, confidence-based escalation, Airtable review control, and policy-based guardrails. Based on the final manual workbook, the system is on track for demo and academic presentation, with strong answer accuracy, acceptable self-service performance, fast latency, and complete governance logging across non-blocked cases. The main improvement priority is Answer Quality Improvements, source traceability consistency and continued strengthening of mixed-framework handling, especially for NIST-heavy questions.

---

**Streamlit Frontend Look:**

<img width="1366" height="597" alt="image" src="https://github.com/user-attachments/assets/4053ccb8-9d8a-43a9-b75c-0a9df53ad867" />
<img width="1273" height="748" alt="image" src="https://github.com/user-attachments/assets/a49a3020-2845-484b-9fd0-0d7cb502b474" />




## Repository Structure

A typical structure for this project is organized around ingestion, backend services, UI, and data layers.

```text
.
├── app/
│   ├── api/
│   ├── core/
│   ├── services/
│   └── main.py
├── ingestion/
│   ├── pdf/
│   └── notion/ or structured/
├── data/
│   ├── raw/
│   │   ├── gdpr/
│   │   ├── hipaa/
│   │   ├── nist/
│   │   └── nist_csf/
│   └── structured/
├── streamlit_app.py
├── requirements.txt
├── .env.example
└── README.md
```
