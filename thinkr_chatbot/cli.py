"""
Command-line interface for the ThinkR chatbot.
"""

import click
import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from .core.chatbot import ThinkRChatbot

# Load environment variables
load_dotenv()

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ThinkR Chatbot - A friendly R tutor for students learning R programming."""
    pass


@cli.command()
@click.option("--pdf-dir", default="./data/pdfs", help="Directory containing PDF files")
@click.option("--force", is_flag=True, help="Force re-indexing of all PDFs")
def index_pdfs(pdf_dir, force):
    """Index PDF documents for retrieval."""
    try:
        console.print(f"[bold blue]Indexing PDFs from: {pdf_dir}[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing chatbot...", total=None)
            
            chatbot = ThinkRChatbot()
            progress.update(task, description="Processing PDFs...")
            
            if force:
                result = chatbot.update_index(pdf_dir)
            else:
                result = chatbot.index_pdfs(pdf_dir)
            
            progress.update(task, description="Indexing complete!")
        
        if result["status"] == "success":
            console.print(f"[bold green]✓ {result['message']}[/bold green]")
            if "stats" in result:
                stats = result["stats"]
                table = Table(title="Indexing Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="magenta")
                table.add_row("Total Documents", str(stats["total_documents"]))
                table.add_row("Index Size", str(stats["index_size"]))
                table.add_row("Dimension", str(stats["dimension"]))
                table.add_row("Model", stats["model_name"])
                console.print(table)
        else:
            console.print(f"[bold yellow]⚠ {result['message']}[/bold yellow]")
            
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)


@cli.command()
@click.option("--model", default="gpt-4", help="OpenAI model to use")
@click.option("--temperature", default=0.7, help="Model temperature")
@click.option("--max-tokens", default=1000, help="Maximum tokens for response")
def chat(model, temperature, max_tokens):
    """Start an interactive chat session with the R tutor."""
    try:
        console.print(Panel.fit(
            "[bold blue]ThinkR Chatbot[/bold blue]\n"
            "[italic]Your friendly R programming tutor[/italic]\n\n"
            "Type your questions about R programming and I'll help you learn!\n"
            "Type 'quit' or 'exit' to end the session.\n"
            "Type 'clear' to clear conversation history.\n"
            "Type 'help' for more commands.",
            border_style="blue"
        ))
        
        chatbot = ThinkRChatbot(
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Check if PDFs are indexed
        stats = chatbot.get_system_info()
        if stats["vector_store_stats"]["total_documents"] == 0:
            console.print("[yellow]⚠ No course materials indexed. Run 'thinkr-chatbot index-pdfs' first.[/yellow]")
        
        while True:
            try:
                # Get user input
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("[bold blue]Goodbye! Happy learning![/bold blue]")
                    break
                
                if user_input.lower() == 'clear':
                    chatbot.clear_conversation_history()
                    console.print("[green]Conversation history cleared.[/green]")
                    continue
                
                if user_input.lower() == 'help':
                    console.print(Panel(
                        "[bold]Available Commands:[/bold]\n"
                        "• Type your R programming questions\n"
                        "• 'clear' - Clear conversation history\n"
                        "• 'stats' - Show system statistics\n"
                        "• 'quit' or 'exit' - End session\n"
                        "• 'help' - Show this help",
                        title="Help"
                    ))
                    continue
                
                if user_input.lower() == 'stats':
                    info = chatbot.get_system_info()
                    table = Table(title="System Information")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="magenta")
                    table.add_row("Model", info["model_name"])
                    table.add_row("Temperature", str(info["temperature"]))
                    table.add_row("Max Tokens", str(info["max_tokens"]))
                    table.add_row("Indexed Documents", str(info["vector_store_stats"]["total_documents"]))
                    table.add_row("Conversation History", str(info["conversation_history_length"]))
                    console.print(table)
                    continue
                
                if not user_input.strip():
                    continue
                
                # Get response
                with console.status("[bold green]Thinking...[/bold green]"):
                    result = chatbot.chat(user_input)
                
                # Display response
                if "error" in result:
                    console.print(f"[bold red]Error: {result['error']}[/bold red]")
                else:
                    # Format and display the response
                    response_md = Markdown(result["response"])
                    console.print(Panel(
                        response_md,
                        title="[bold green]ThinkR Tutor[/bold green]",
                        border_style="green"
                    ))
                    
                    # Show references if any
                    if result["references"]:
                        ref_table = Table(title="Course References")
                        ref_table.add_column("Module", style="cyan")
                        ref_table.add_column("Page", style="yellow")
                        ref_table.add_column("Relevance", style="green")
                        
                        for ref in result["references"]:
                            ref_table.add_row(
                                ref.get("module", "Unknown"),
                                ref.get("page", "N/A"),
                                f"{ref.get('score', 0):.3f}"
                            )
                        console.print(ref_table)
                
            except KeyboardInterrupt:
                console.print("\n[bold blue]Goodbye! Happy learning![/bold blue]")
                break
            except Exception as e:
                console.print(f"[bold red]Error: {str(e)}[/bold red]")
                
    except Exception as e:
        console.print(f"[bold red]Failed to initialize chatbot: {str(e)}[/bold red]")
        console.print("[yellow]Make sure you have set your OPENAI_API_KEY environment variable.[/yellow]")
        sys.exit(1)


@cli.command()
@click.argument("message")
@click.option("--output", "-o", help="Output file for response")
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "json"]))
def ask(message, output, output_format):
    """Ask a single question and get a response."""
    try:
        chatbot = ThinkRChatbot()
        result = chatbot.chat(message)
        
        if output_format == "json":
            response_data = {
                "question": message,
                "response": result["response"],
                "raw_response": result["raw_response"],
                "references": result["references"],
                "model": result["model"],
                "timestamp": result["timestamp"]
            }
            response_text = json.dumps(response_data, indent=2)
        else:
            response_text = result["response"]
        
        if output:
            with open(output, 'w') as f:
                f.write(response_text)
            console.print(f"[green]Response saved to {output}[/green]")
        else:
            console.print(Panel(
                Markdown(result["response"]),
                title="[bold green]ThinkR Tutor Response[/bold green]",
                border_style="green"
            ))
            
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)


@cli.command()
@click.argument("topic")
@click.option("--count", "-c", default=3, help="Number of recommendations")
def recommend(topic, count):
    """Get learning recommendations for a topic."""
    try:
        chatbot = ThinkRChatbot()
        recommendations = chatbot.get_recommendations(topic, count)
        
        if not recommendations:
            console.print(f"[yellow]No recommendations found for '{topic}'[/yellow]")
            return
        
        table = Table(title=f"Learning Recommendations for '{topic}'")
        table.add_column("Module", style="cyan")
        table.add_column("Page", style="yellow")
        table.add_column("Relevance", style="green")
        table.add_column("Suggestion", style="blue")
        
        for rec in recommendations:
            table.add_row(
                rec["module"],
                rec["page"],
                f"{rec['relevance_score']:.3f}",
                rec["suggestion"]
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)


@cli.command()
def info():
    """Show system information and statistics."""
    try:
        chatbot = ThinkRChatbot()
        info = chatbot.get_system_info()
        
        table = Table(title="ThinkR Chatbot System Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Model", info["model_name"])
        table.add_row("Temperature", str(info["temperature"]))
        table.add_row("Max Tokens", str(info["max_tokens"]))
        table.add_row("PDF Directory", info["pdf_directory"])
        table.add_row("Vector DB Path", info["vector_db_path"])
        table.add_row("Indexed Documents", str(info["vector_store_stats"]["total_documents"]))
        table.add_row("Index Size", str(info["vector_store_stats"]["index_size"]))
        table.add_row("Vector Dimension", str(info["vector_store_stats"]["dimension"]))
        table.add_row("Embedding Model", info["vector_store_stats"]["model_name"])
        table.add_row("Conversation History", str(info["conversation_history_length"]))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)


@cli.command()
@click.option("--format", default="json", type=click.Choice(["json", "text"]))
@click.option("--output", "-o", help="Output file")
def export(format, output):
    """Export conversation history."""
    try:
        chatbot = ThinkRChatbot()
        export_data = chatbot.export_conversation(format)
        
        if format == "json":
            content = json.dumps(export_data, indent=2)
        else:
            content = export_data["conversation_text"]
        
        if output:
            with open(output, 'w') as f:
                f.write(content)
            console.print(f"[green]Conversation exported to {output}[/green]")
        else:
            console.print(content)
            
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main() 