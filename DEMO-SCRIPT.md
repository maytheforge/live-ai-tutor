# Live AI Tutor — Demo Video Script (Under 4 Minutes)

**Category:** Live Agents
**Total Runtime:** 3:50

---

## PRE-RECORDING SETUP

- [ ] Have a handwritten math problem ready on paper: `3x + 5 = 20`
- [ ] Open the app in Chrome (Cloud Run URL or localhost:5173)
- [ ] Webcam and microphone enabled
- [ ] Screen recorder running (full screen capture + audio)
- [ ] Close all other tabs/notifications

---

## ACT 1 — THE PROBLEM (0:00 – 0:40)

**[SCREEN: Title slide or speak to camera]**

> "Every day, millions of students ask AI for homework help — and every day, AI gives them the answer instantly. The problem? They never actually learn."
>
> "ChatGPT, Gemini, every AI tool today is an answer engine. A student types in '3x + 5 = 20' and gets back 'x = 5.' Problem solved. Learning? Zero."
>
> "What if AI could tutor like the best teachers do — by asking questions, not giving answers?"

**[SCREEN: Open the Live AI Tutor landing page]**

> "This is Live AI Tutor — a real-time, multimodal Socratic tutor powered by Gemini Live and Google ADK."

---

## ACT 2 — THE LIVE DEMO (0:40 – 2:50)

### Starting a Session (0:40 – 0:55)

**[SCREEN: Click "Start Tutoring Session" on the landing page]**

> "The student clicks to start a session. They get a live voice connection to Coach Leo — our Socratic AI tutor — plus a dual-panel workspace featuring a high-quality Mermaid Diagram tab and an Excalidraw whiteboard for annotations."

**[SCREEN: Session page loads — webcam feed, Diagram panel, and mic indicator visible]**

> "This is fully multimodal. Voice in and out via Gemini Live, camera vision, and an intelligent Diagram tab — all in real time."

### Showing the Homework (0:55 – 1:25)

**[ACTION: Hold up the handwritten paper with `3x + 5 = 20` to the webcam, or upload a photo]**

> "The student shows their homework — or uploads a photo. Our Vision Agent, running Gemini 1.5 Flash, instantly analyzes the image."

**[ACTION: Say out loud — "Hey Coach Leo, I'm stuck on this equation. Can you help me?"]**

**[WAIT for Gemini Live to respond via voice — it should ask a Socratic question like "What do you notice about this equation?" rather than solving it]**

> *(Let the AI response play naturally — don't talk over it)*

### The Socratic Interaction (1:25 – 2:10)

**[ACTION: Respond to Coach Leo's question — e.g., "There's a 3x and a plus 5"]**

**[WAIT for the AI to guide — it should ask something like "What could you do to get the x by itself?"]**

**[ACTION: Say "Subtract 5 from both sides?"]**

**[WAIT for AI to affirm and possibly trigger a canvas drawing]**

> *(If the AI generates a diagram, point it out):*
> "Notice how Coach Leo just generated a Mermaid flowchart in the Diagram tab — it's showing the logic visually without revealing the final answer. The student still has to do the thinking."

### Canvas in Action (2:10 – 2:50)

**[SCREEN: Point to the Excalidraw canvas showing diagrams/highlights]**

> "The backend orchestrator built with Google ADK routes between specialized sub-agents. The Diagram Agent generates high-quality Mermaid DSL for conceptual flows and solution summaries, while the Canvas Agent handles dynamic highlights on the whiteboard."

**[ACTION: Say "Can you draw a number line for this?"]**

**[WAIT for diagram to appear on canvas]**

> "Every visual is a discovery aid — not a spoiler. For science concepts, diagrams appear upfront to build a framework. For math homework, Coach Leo holds them back until the final 'Aha!' moment — where he provides a complete visual wrap-up of the steps we walked through together."

---

## ACT 3 — THE ARCHITECTURE (2:50 – 3:25)

**[SCREEN: Show the architecture diagram (architecture-diagram.png)]**

> "Under the hood, this is a multi-agent system:"
>
> "The React frontend connects to Gemini Live via WebSocket for real-time voice. When the student shows their work, a snapshot goes to our FastAPI backend on Cloud Run."
>
> "The Vision Agent analyzes the image with Gemini 1.5 Flash. Then the Google ADK Orchestrator routes between the Tutor Agent — which handles Socratic logic — and sub-agents for Mermaid Diagram and Excalidraw Canvas generation."
>
> "Tool calls flow back to the frontend, updating the Diagram panel and Whiteboard in real time. The student sees the logic take shape as Coach Leo speaks."

---

## ACT 4 — THE CLOSE (3:25 – 3:50)

**[SCREEN: Back to the app or title slide]**

> "Live AI Tutor proves that AI doesn't have to be an answer engine. With Gemini Live for real-time voice, Gemini Vision for understanding homework, and Google ADK for multi-agent orchestration — we built the tutor every student deserves."
>
> "One that asks questions. One that draws the path. And one that lets the student walk it themselves."
>
> "Built with Gemini Live and Google Cloud. Thank you."

---

## KEY MOMENTS TO CAPTURE

| Timestamp | What to Show | Judging Criteria Hit |
|-----------|-------------|---------------------|
| 0:00-0:40 | Problem statement — answer engines don't teach | Demo & Presentation (30%) |
| 0:40-1:25 | Multimodal input: voice + camera/upload | Innovation & Multimodal UX (40%) |
| 1:25-2:50 | Live Socratic dialogue + canvas drawings | Innovation & Multimodal UX (40%) |
| 2:50-3:25 | Architecture diagram + tech explanation | Technical Implementation (30%) |
| 3:25-3:50 | Impact statement + closing | Demo & Presentation (30%) |

## TIPS FOR RECORDING

1. **Don't script the AI responses** — let them happen naturally. Authentic interaction is more impressive than a rehearsed demo.
2. **If the AI gives a direct answer** (breaks Socratic rules), say "Usually Coach Leo guides with questions — let me try again." Honesty builds credibility.
3. **Keep your voice energy high** — you're pitching, not presenting a lecture.
4. **Show the URL** briefly so judges see it's deployed on Cloud Run.
5. **Have a backup uploaded image** ready in case the webcam has issues.
6. **Record 2-3 takes** — pick the one where the AI interaction is most natural.
