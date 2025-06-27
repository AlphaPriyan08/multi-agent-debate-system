# nodes/utility_nodes.py
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
    """Node to create a rolling summary of the debate."""
    if not state["messages"]:
        return {}
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUMMARIZER_PROMPT), 
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # Using a smaller, faster model for summarization is efficient
    llm = ChatGroq(temperature=0.7, model_name="llama3-8b-8192")
    chain = prompt | llm

    with console.status("Moderator is summarizing..."):
        response = chain.invoke({"messages": state["messages"]})
    
    summary = response.content
    logging.info(f"DEBATE SUMMARY: {summary}")
    return {"summary": summary}