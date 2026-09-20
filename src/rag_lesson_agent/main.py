import argparse
import os

from dotenv import load_dotenv
from rich.console import Console

from .agents import GeminiModel
from .memory import MemoryStore
from .workflow import LessonWorkflow


console = Console()


def main():
    # Load environment variables from .env
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Self-evaluating RAG lesson content generator"
    )

    parser.add_argument(
        "--topic",
        default="Introduction to RAG",
        help="Topic for the lesson",
    )

    parser.add_argument(
        "--demo-error",
        action="store_true",
        help=(
            "Inject a deliberate quality error into the first draft "
            "to demonstrate evaluator rejection and retry."
        ),
    )

    args = parser.parse_args()

    # ---------------------------------------------------------
    # Validate Gemini configuration
    # ---------------------------------------------------------
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    model_name = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash",
    )

    # ---------------------------------------------------------
    # Initialize components
    # ---------------------------------------------------------
    model = GeminiModel(model_name)

    memory = MemoryStore(
        "data/memory.json"
    )

    workflow = LessonWorkflow(
        model=model,
        memory=memory,
        max_retries=2,
    )

    # ---------------------------------------------------------
    # Run workflow
    # ---------------------------------------------------------
    result = workflow.run(
        topic=args.topic,
        demo_error=args.demo_error,
    )

    # ---------------------------------------------------------
    # Display result
    # ---------------------------------------------------------
    console.print()
    console.print("[bold]RAG Lesson Agent[/bold]")
    console.print("-" * 50)

    console.print(f"Run ID: {result.run_id}")
    console.print(f"Topic: {result.topic}")
    console.print(f"Status: {result.status}")
    console.print(f"Attempts: {result.attempts}")

    console.print()

    if result.status == "PASSED":
        console.print(
            "[bold green]Lesson generation PASSED.[/bold green]"
        )
    else:
        console.print(
            "[bold red]Lesson generation FAILED "
            "after maximum attempts.[/bold red]"
        )

    console.print()
    console.print(
        "Output files:"
    )
    console.print(
        "  - outputs/final_lesson.md"
    )
    console.print(
        "  - outputs/rejection_log.md"
    )
    console.print(
        f"  - outputs/run_{result.run_id}.json"
    )
    console.print(
        "  - data/memory.json"
    )


if __name__ == "__main__":
    main()