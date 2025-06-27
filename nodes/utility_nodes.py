import logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from graph_state import GraphState
from prompts import SUMMARIZER_PROMPT

# We can pass the console object or initialize it here
console = Console()

def user_input_node(state: GraphState) -> GraphState:
    """Node to get the initial debate topic and initialize the full state."""
    topic = Prompt.ask("[bold yellow]Please enter the topic for the debate[/bold yellow]")
    console.print(Panel(f"Debate Topic: [bold]{topic}[/bold]", title="Topic Set", border_style="green"))
    logging.info(f"Debate topic set to: {topic}")
    return {
        "topic": topic, "messages": [], "summary": "The debate has not yet begun.",
        "round_count": 0, "winner": "", "justification": ""
    }

def summarize_debate_node(state: GraphState) -> GraphState:
    """
    Node to create a rolling, updated summary of the debate after each turn.
    """
    # On the very first pass, there's nothing to summarize yet.
    if not state["messages"]:
        return {}

    llm = ChatGroq(temperature=0.7, model_name="llama3-8b-8192")
    
    # Get the existing summary and the last message (the new argument)
    current_summary = state["summary"]
    new_argument = state["messages"][-1].content
    
    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT)
    chain = prompt | llm
    
    summary = ""
    # Implement retry logic for reliability
    for attempt in range(3):
        with console.status("Moderator is updating summary..."):
            try:
                response = chain.invoke({
                    "summary": current_summary,
                    "new_argument": new_argument,
                })
                if response.content and response.content.strip():
                    summary = response.content
                    break # Success
            except Exception as e:
                logging.error(f"Error during summary update attempt {attempt + 1}: {e}")
    
    if not summary:
        logging.warning("Failed to update summary after 3 attempts. Appending raw argument instead.")
        summary = current_summary + "\n\n" + f"The last speaker added: {new_argument}"

    logging.info(f"UPDATED DEBATE SUMMARY: {summary}")
    return {"summary": summary}