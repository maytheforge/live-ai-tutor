---
stepsCompleted: [step-01-init, step-02-discovery]
inputDocuments: [brainstorming-session-20260309-200920]
workflowType: 'prd'
classification:
  projectType: 'web_app'
  domain: 'edtech'
  complexity: 'medium-high'
  projectContext: 'greenfield'
documentCounts:
  briefCount: 0
  researchCount: 0
  brainstormingCount: 1
  projectDocsCount: 0
---

# Product Requirements Document - Live Homework Tutor Agent

**Author:** Harishkanuri
**Date:** 2026-03-09T20:06:34-04:00
## 1. Product Vision
The **Live Homework Tutor Agent** aims to bridge the gap between static AI answers and genuine educational growth. By leveraging Gemini's real-time multimodal capabilities (Live Voice + Vision), we are building a "Socratic Mirror"—a tutor that doesn't just solve problems but guides students through the cognitive process of discovery. Our vision is to provide every student with a 1:1 elite tutoring experience that is interruptible, visual, and deeply responsive to their individual learning pace.

## 2. User Personas

| Persona | Grade Level | Core Needs | Tech Proficiency |
| :--- | :--- | :--- | :--- |
| **Sophie** | Early Elementary (K-2nd) | Narrative-driven learning, phonics/math basics, high emotional support, playful visuals. | Low/Guided (Touchscreens). |
| **Leo** | Upper Elementary (3rd-5th) | Visual aids, simple language, encouragement, focus on basics (Arithmetic, Reading). | Moderate (Tablets/Chromebooks). |
| **Maya** | Middle School (6th-8th) | Step-by-step logic, transition to abstract concepts (Pre-Algebra, Earth Science). | High (Mobile/Laptop). |
| **Sam** | High School (9th-12th) | Advanced reasoning, complex symbol handling (Calculus, Physics), efficiency. | Expert (Advanced tools). |

## 3. Problem Statement
Existing AI tools (LLMs) suffer from the **"Answer Engine" Trap**: they provide the final solution too quickly, bypassing the student's critical thinking phase. Furthermore, they lack **Real-Time Multimodality**; typical interactions are asynchronous (text/photo upload) rather than fluid, conversational, and visual. For a student stuck on a math problem, the jump from "question" to "solution" is often too large to be educational. We need a system that can "see" the paper, "hear" the confusion, and "draw" the path forward simultaneously.

## 4. Product Requirements (PRD)

### Functional Requirements
- **FR1: Real-Time Multimodal Stream**: Continuous or snapshot-based vision sync with low-latency voice via Gemini Live API.
- **FR2: Socratic Logic Engine**: A backend "Tutor Agent" that uses prompting strategies to avoid giving direct answers.
- **FR3: Collaborative Canvas**: Integration with Excalidraw allowing the AI to annotate student work in real-time.
- **FR4: Subject Adaptability**: Context-aware personalities for Math (Logical), Science (Exploratory), and English (Analytical).
- **FR5: Structured Diagram Generator**: Specialized agent for creating semantic visual instructions (graphs, flowcharts, grammar trees) for the canvas.


### Non-Functional Requirements
- **NFR1: Latency**: Voice response should feel "live" (<1.5s turnaround).
- **NFR2: Safety**: COPPA-ready architecture (no persistent storage of student faces/PII for the POC).
- **NFR3: Scalability**: Capable of handling concurrent Excalidraw websocket sessions via Cloud Run.

## 5. Hackathon POC Scope
For the 4-minute demo, we will focus on a **Math (Algebra)** use case:
1. **The Hook**: Student shows a handwritten equation ($3x + 5 = 20$).
2. **The Interaction**: Gemini Live greets the student and "looks" at the work.
3. **The Canvas**: The AI highlights the $+5$ on Excalidraw and asks "How do we undo this addition?".
4. **The Resolution**: Student answers "Subtract 5", the AI draws the result on the board, and the student completes the problem.
