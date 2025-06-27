import logging
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from rich.console import Console
from rich.panel import Panel

from graph_state import GraphState
from prompts import PERSONAS

console = Console()

def create_agent_node(persona: str):
    """Factory function to create a debate agent node for a specific persona."""
    def agent_node(state: GraphState) -> GraphState:
        system_prompt = PERSONAS[persona]
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Here is the debate topic: {topic}\n\nHere is a summary of the debate so far:\n{summary}\n\nPlease provide your next argument. Make it concise and impactful."),
        ])
        
        llm = ChatGroq(temperature=0.7, model_name="llama3-70b-8192")
        chain = prompt | llm
        
        display_round = (len(state['messages']) // 2) + 1
        console.print(Panel(f"Round {display_round}: It is the [bold]{persona}'s[/bold] turn to speak.", style="cyan" if persona == "Scientist" else "magenta"))
        
        with console.status(f"{persona} is thinking..."):
            response = chain.invoke({"topic": state["topic"], "summary": state["summary"]})
        
        argument = response.content
        console.print(Panel(argument, title=f"Argument from {persona}", border_style="cyan" if persona == "Scientist" else "magenta"))
        logging.info(f"ARGUMENT (Round {display_round}, {persona}): {argument}")
        
        new_message = AIMessage(content=argument, name=persona)
        
        # Increment round count only after the Philosopher (the second speaker) has finished
        if persona == "Philosopher":
            return {"messages": state["messages"] + [new_message], "round_count": state["round_count"] + 1}
        
        return {"messages": state["messages"] + [new_message]}
    
    return agent_node