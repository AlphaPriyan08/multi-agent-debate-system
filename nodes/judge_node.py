# nodes/judge_node.py
import logging
import json
import re
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from rich.console import Console
from rich.panel import Panel

from graph_state import GraphState
from prompts import JUDGE_PROMPT

console = Console()

def judge_node(state: GraphState) -> GraphState:
    """
    The final node in the debate. It uses a two-step "chain of thought" process
    to summarize and then judge the debate for higher reliability.
    """
    console.print(Panel("The debate has concluded. The Judge will now review the arguments.", title="[bold]Judgment Phase[/bold]", border_style="red"))
    llm = ChatGroq(temperature=0.7, model_name="llama3-70b-8192")

    # Step 1: Create a summary of the whole debate for the judge's context
    with console.status("Judge is summarizing the debate..."):
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an impartial judge. First, summarize the entire debate transcript neutrally. Focus on the main claims and rebuttals of both the Scientist and the Philosopher."),
            MessagesPlaceholder(variable_name="messages")
        ])
        summary_chain = summary_prompt | llm
        debate_summary = summary_chain.invoke({"messages": state["messages"]}).content
        console.print(Panel(debate_summary, title="Judge's Summary of Arguments", border_style="yellow"))

    # Step 2: Use the summary to make a final, structured decision
    with console.status("Judge is deliberating on a winner..."):
        verdict_prompt_template = (
            "You are an impartial and logical Judge. You have already summarized the debate. Now, based on the full "
            "transcript and your summary, you must render a final verdict.\n\n"
            "Here is the full debate transcript for your review:\n<transcript>{messages}</transcript>\n\n"
            "Here is your summary of the arguments:\n<summary>{summary}</summary>\n\n"
            "Your final task is to declare a winner and provide a justification. You MUST respond with ONLY a "
            "valid JSON object with the keys 'winner' and 'justification'. Do not include any other text."
        )
        verdict_prompt = ChatPromptTemplate.from_template(verdict_prompt_template)
        verdict_chain = verdict_prompt | llm | JsonOutputParser()
        
        try:
            verdict = verdict_chain.invoke({
                "messages": state["messages"],
                "summary": debate_summary
            })
        except Exception as e:
            console.print(f"[bold red]Critical Error: Failed to get a structured verdict from the LLM. Error: {e}[/bold red]")
            verdict = {"winner": "Undetermined", "justification": "The judge's final response could not be parsed, preventing a final decision."}
            
    logging.info(f"JUDGE'S VERDICT: {verdict}")
    return {"winner": verdict.get("winner", "Undetermined"), "justification": verdict.get("justification", "N/A")}