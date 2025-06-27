# Multi-Agent Debate System using LangGraph

**ATG Technical Assignment - Round 2**

This project implements a sophisticated multi-agent debate system where two AI personas, a **Scientist** and a **Philosopher**, engage in a structured, multi-round debate on a user-provided topic. The system is built with a modular architecture using LangGraph to manage the complex, looping control flow.

It features scoped memory for each agent, a robust two-step "chain of thought" judging process for a reliable verdict, and a professional command-line interface.

## Key Architectural Features

*   **Modular, Scalable Codebase:** The project is organized into distinct modules for prompts, graph state, and node logic, following professional software engineering best practices.
*   **Persona-Driven Agents:** The Scientist and Philosopher have distinct, carefully crafted system prompts that guide their reasoning and rhetorical style, leading to a high-quality, nuanced debate.
*   **Scoped Memory via Summarization:** To prevent prompt bloat and ensure agents respond to the evolving context, a `summarize_debate_node` acts as a central hub, creating a rolling summary that is the *only* context the debaters receive for their next turn.
*   **Robust, Two-Step Judgment:** To ensure a reliable final verdict, the `JudgeNode` first performs a "chain of thought" by summarizing the entire debate, then uses that summary as context to make its final, structured JSON decision. This significantly improves the reliability of the structured output.
*   **Programmatic DAG Visualization:** The application automatically generates a `debate_dag.png` file that is a 100% accurate visual representation of the compiled graph's true structure.

## System Architecture

The core of the system is a "hub and spoke" `StateGraph` that manages the turn-based flow of the debate. The `summarize` node acts as the central hub for the main debate loop.

```
+--------------+
|  User Input  |
+------+-------+
       |
       v
+------+---------+     (After any turn)
|    Summarize   |<--------------------------------------------+
+------+---------+                                             |
       |                                                       |
       | (Conditional: debate_router)                          |
       |                                                       |
       +---------------------------------------+               |
       | (Rounds <= 4)             (Rounds > 4)|               |
       v                                       v               |
+------------------+                     +-----------+         |
|  Decide Speaker  |                     |   Judge   |         |
+--------+---------+                     +-----+-----+         |
         |                                     |               |
         | (Conditional: speaker_router)       |               |
         |                                     v               |
+--------+---------+                     +-------------+       |
| (Phil. last)     | (Sci. last)         |   __end__   |       |
v                  v                     +-------------+       |
+-----------+      +-------------+                             |
| Scientist |      | Philosopher |                             |
+-----------+      +-------------+                             |
      |                  |                                     |
      +------------------+-------------------------------------+

```

## Project Structure

The codebase is organized for clarity, scalability, and maintainability.

```
debate-multi-agent/
├── main.py                # Main entry point, CLI loop, and graph assembly.
├── graph_state.py         # Defines the central GraphState TypedDict.
├── prompts.py             # Centralizes all system prompts for agents and judge.
├── nodes/
│   ├── __init__.py        # Makes 'nodes' a Python package.
│   ├── agent_nodes.py     # Logic for the Scientist and Philosopher debaters.
│   ├── judge_node.py      # Contains the robust, two-step judging logic.
│   └── utility_nodes.py   # Contains helper nodes like user input and summarizer.
├── requirements.txt       # All Python dependencies.
├── .env                   # For storing API keys securely.
└── debate_dag.png         # Auto-generated diagram of the graph.
```

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/AlphaPriyan08/multi-agent-debate-system
    cd multi-agent-debate-system
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Key:**
    *   Create a free API key at [Groq Console](https://console.groq.com/keys).
    *   Create a file named `.env` in the project's root directory.
    *   Add your API key to the `.env` file like this:
        `GROQ_API_KEY="gsk_YourActualGroqApiKeyHere"`

## How to Run

1.  **Ensure all dependencies and the `.env` file are set up.**
2.  **Run the application from your terminal:**
    ```bash
    python main.py
    ```
3.  The program will first generate the `debate_dag.png` file.
4.  You will then be prompted to enter a topic for the debate.
5.  The debate will run automatically for 4 full rounds (8 total arguments), culminating in a final verdict from the Judge. A full `chat_log.log` file will be generated.

## Sample CLI Interaction

Here is a sample of a full interaction with the application.

```
DAG diagram saved to debate_dag.png
Please enter the topic for the debate: What is important for life? Money or Friends.
╭─────────────────────────────────── Topic Set ─────────────────────────────────────╮
│ Debate Topic: What is important for life? Money or Friends.                       │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────────────────────────────╮
│ Round 1: It is the Scientist's turn to speak.                                     │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────── Argument from Scientist ────────────────────────────╮
│ Let's start with empirical evidence. Studies have consistently shown that once    │
│ basic needs are met, additional wealth does not necessarily lead to greater       │
│ happiness. This is known as the "Easterlin paradox."...                           │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────────────────────────────╮
│ Round 1: It is the Philosopher's turn to speak.                                   │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭───────────────────────────── Argument from Philosopher ───────────────────────────╮
│ A most intriguing debate! As a philosopher, I'd like to challenge the very        │
│ foundation of this question by asking: What does it mean to say something is      │
│ "important" in life? ...                                                          │
╰───────────────────────────────────────────────────────────────────────────────────╯

... (Debate continues for 4 full rounds) ...

╭────────────────────────────────── Judgment Phase ─────────────────────────────────╮
│ The debate has concluded. The Judge will now review the arguments.                │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────── Judge's Summary of Arguments ─────────────────────────╮
│ The Scientist consistently argued from a basis of empirical evidence, citing      │
│ studies like the "Easterlin paradox" and research on social epidemiology to show  │
│ that strong social connections are a greater predictor of well-being and longevity│
│ than wealth beyond a certain threshold.                                           │
│                                                                                   │
│ The Philosopher consistently challenged the premise of the question itself,       │
│ arguing that framing it as a binary choice is a philosophical error. They         │
│ posited that friends provide intrinsic value and contribute to a life of meaning  │
│ and purpose, which cannot be measured by the same instrumental scale as money.    │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────── FINAL VERDICT ──────────────────────────────────╮
│ Winner: Philosopher                                                               │
│                                                                                   │
│ Justification:                                                                    │
│ While the Scientist provided strong, consistent empirical evidence, the           │
│ Philosopher won the debate by successfully deconstructing the core question. They │
│ effectively argued that the debate was not a matter of conflicting evidence but   │
│ of different value systems, and that a meaningful life (eudaimonia) transcends a  │
│ simple comparison between a means (money) and an end (meaningful relationships).  │
│ This meta-level analysis was more persuasive.                                     │
╰───────────────────────────────────────────────────────────────────────────────────╯
```

## Demo Video