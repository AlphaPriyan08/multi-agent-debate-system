# main.py (Modular Version)
import logging
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from langgraph.graph import END, StateGraph

# Local module imports
from graph_state import GraphState
from nodes.utility_nodes import user_input_node, summarize_debate_node
from nodes.agent_nodes import create_agent_node
from nodes.judge_node import judge_node

# --- Setup ---
load_dotenv()
console = Console()

# --- Conditional Routing Logic ---
def debate_router(state: GraphState) -> str:
    """Router to control the flow of the debate."""
    if state["round_count"] >= 4: # Limit to 4 rounds (2 per agent)
        return "route_to_judge"
    return "continue_debate"

def speaker_router(state: GraphState) -> str:
    """Determines which agent speaks next."""
    if not state["messages"] or state["messages"][-1].name == "Philosopher":
        return "scientist"
    return "philosopher"

# --- Graph Assembly (Final Refined Version) ---
def build_graph() -> StateGraph:
    """Builds and compiles the multi-agent debate graph."""
    workflow = StateGraph(GraphState)
    
    # Add nodes to the graph
    workflow.add_node("user_input", user_input_node)
    workflow.add_node("summarize", summarize_debate_node)
    workflow.add_node("scientist", create_agent_node("Scientist"))
    workflow.add_node("philosopher", create_agent_node("Philosopher"))
    workflow.add_node("judge", judge_node)
    workflow.add_node("decide_speaker", lambda state: {}) # Passthrough node

    # Define the graph's edges and control flow
    workflow.set_entry_point("user_input")
    workflow.add_edge("user_input", "summarize")
    workflow.add_edge("scientist", "summarize")
    workflow.add_edge("philosopher", "summarize")
    workflow.add_edge("judge", END)
    
    # The main routing logic
    workflow.add_conditional_edges(
        "summarize", debate_router,
        {"route_to_judge": "judge", "continue_debate": "decide_speaker"}
    )
    
    # The speaker selection logic
    workflow.add_conditional_edges("decide_speaker", speaker_router, {
        "scientist": "scientist", "philosopher": "philosopher"
    })
    
    return workflow.compile()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler("chat_log.log", mode='w')])

    app = build_graph()
    
    # Generate the diagram of the final graph
    try:
        app.get_graph().draw_mermaid_png(output_file_path="debate_dag.png")
        console.print("[bold green]DAG diagram saved to debate_dag.png[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Could not create diagram: {e}[/bold red]")
    
    # Invoke the graph and run the debate
    final_state = app.invoke({}, {"recursion_limit": 100})
    
    # Print the final verdict
    console.print(Panel(f"[bold]Winner: {final_state['winner']}[/bold]\n\n"
                        f"[bold]Justification:[/bold]\n{final_state['justification']}",
                        title="[bold red]FINAL VERDICT[/bold red]",
                        border_style="red"))