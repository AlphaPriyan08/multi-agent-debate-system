import logging
import json
import re
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from rich.console import Console
from rich.panel import Panel

# Local imports
from graph_state import GraphState

console = Console()

def judge_node(state: GraphState) -> GraphState:
    """
    The final node in the debate. It uses a robust, two-step "chain of thought"
    process with retry logic to ensure a reliable verdict.
    """
    console.print(Panel("The debate has concluded. The Judge will now review the arguments.", title="[bold]Judgment Phase[/bold]", border_style="red"))
    llm = ChatGroq(temperature=0.7, model_name="llama3-70b-8192")
    debate_summary = ""

    # Step 1: Create a summary with a robust retry mechanism and a better prompt
    with console.status("Judge is summarizing the debate..."):
        # This prompt is more focused and breaks down the task for the LLM.
        summary_prompt_template = (
            "You are an impartial judge. Your task is to summarize the following debate transcript. "
            "Please provide a neutral summary, covering the key arguments from each participant.\n\n"
            "Here is the debate transcript:\n"
            "--- START OF TRANSCRIPT ---\n"
            "{messages_text}\n"
            "--- END OF TRANSCRIPT ---\n\n"
            "Now, please provide your summary."
        )
        summary_prompt = ChatPromptTemplate.from_template(summary_prompt_template)
        summary_chain = summary_prompt | llm

        # Convert message objects to a simple string for the prompt
        messages_text = "\n\n".join([f"{msg.name}: {msg.content}" for msg in state["messages"]])

        # Implement retry logic for the summary generation
        for attempt in range(3):
            try:
                response = summary_chain.invoke({"messages_text": messages_text})
                if response.content and response.content.strip():
                    debate_summary = response.content
                    console.print(f"\n[green]Judge's summary generated successfully (attempt {attempt + 1}).[/green]")
                    break # Exit the loop on success
            except Exception as e:
                logging.error(f"Error during summary generation attempt {attempt + 1}: {e}")
            
            if not debate_summary:
                console.print(f"\n[yellow]Warning: Judge's summary was empty. Retrying... (attempt {attempt + 2}/3)[/yellow]")

    # Final fallback if all retry attempts fail
    if not debate_summary:
        console.print("[bold red]Critical: Failed to generate a debate summary after 3 attempts. Proceeding with a default summary.[/bold red]")
        debate_summary = "The Judge was unable to generate a summary of the debate. The verdict will be based on the raw transcript."
    
    console.print(Panel(debate_summary, title="Judge's Summary of Arguments", border_style="yellow"))

    # Step 2: Use the (now guaranteed) summary to make a final, structured decision
    with console.status("Judge is deliberating on a winner..."):
        verdict_prompt_template = (
            "You are an impartial and logical Judge. You have already summarized the debate. Now, based on the full "
            "transcript and your summary, you must render a final verdict.\n\n"
            "Here is the full debate transcript for your review:\n<transcript>{messages_text}</transcript>\n\n"
            "Here is your summary of the arguments:\n<summary>{summary}</summary>\n\n"
            "Your final task is to declare a winner and provide a justification. You MUST respond with ONLY a "
            "valid JSON object with the keys 'winner' and 'justification'. Do not include any other text."
        )
        verdict_prompt = ChatPromptTemplate.from_template(verdict_prompt_template)
        verdict_chain = verdict_prompt | llm | JsonOutputParser()
        
        try:
            verdict = verdict_chain.invoke({
                "messages_text": messages_text, # Pass the text version here too
                "summary": debate_summary
            })
        except Exception as e:
            console.print(f"[bold red]Critical Error: Failed to get a structured verdict from the LLM. Error: {e}[/bold red]")
            verdict = {"winner": "Undetermined", "justification": "The judge's final response could not be parsed, preventing a final decision."}
            
    logging.info(f"JUDGE'S VERDICT: {verdict}")
    return {"winner": verdict.get("winner", "Undetermined"), "justification": verdict.get("justification", "N/A")}