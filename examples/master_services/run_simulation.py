#!/usr/bin/env python3
"""Interactive Master Services Company Simulation.

This script provides an interactive interface to the Master Services
multi-agent company simulation system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.company_simulation import app


def print_header():
    """Print the welcome header."""
    print("\n" + "=" * 80)
    print("MASTER SERVICES PANAMA S.A. - COMPANY SIMULATION")
    print("=" * 80)
    print("\nWelcome to the Master Services multi-agent simulation!")
    print("\nThis AI-powered system simulates different departments of your company:")
    print("  🏦 Finance Agent - Financial analysis and cost calculations")
    print("  🔧 Operations Manager - Project management and resource allocation")
    print("  👥 HR Agent - Employee information and skills management")
    print("  📊 Strategy Agent - Competitive analysis and strategic planning")
    print("  💼 Sales/Bidding Agent - Quotes, pricing, and proposals")
    print("\n" + "=" * 80)


def print_examples():
    """Print example queries."""
    print("\n💡 Example Questions You Can Ask:")
    print("\n  COMPANY INFORMATION:")
    print('    - "Give me a company overview"')
    print('    - "What are our recent major projects?"')
    print('    - "What is our strategic focus?"')
    print("\n  EMPLOYEE & HR:")
    print('    - "Show me all employees in the Maintenance department"')
    print('    - "Who can do tank installation?"')
    print('    - "List employees with electrical work skills"')
    print("\n  FINANCIAL & PRICING:")
    print('    - "What are our hourly rates for different services?"')
    print('    - "Calculate a quote for 100 hours of station maintenance"')
    print('    - "Quote a station construction project: 2000 hours, $50,000 materials"')
    print("\n  STRATEGIC DECISIONS:")
    print('    - "Should we bid on a $15,000 local maintenance project?"')
    print('    - "Analyze: Tank installation, 80 hours, $10,000 materials, Colon, Delta Petroleum"')
    print('    - "How do we compare to our competitors?"')
    print("\n  PROJECT MANAGEMENT:")
    print('    - "What employees should work on a major electrical project?"')
    print('    - "How many technicians do we have in each department?"')
    print("\n" + "=" * 80)


def run_interactive():
    """Run the interactive simulation."""
    print_header()
    print_examples()

    # Create a unique thread for this session
    import time
    thread_id = f"session_{int(time.time())}"
    config = {"configurable": {"thread_id": thread_id}}

    print("\n🤖 System ready! Type your questions below.")
    print("   (Type 'help' for examples, 'quit' or 'exit' to stop)\n")

    while True:
        try:
            # Get user input
            user_input = input("\n📝 You: ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye! Thank you for using Master Services simulation.\n")
                break

            if user_input.lower() in ["help", "examples", "?"]:
                print_examples()
                continue

            # Process the query
            print("\n🤔 Processing...\n")

            response = app.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config,
            )

            # Get the last message (the agent's response)
            last_message = response["messages"][-1]

            # Print the response
            print(f"🤖 {last_message.content}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Please try again or type 'help' for examples.\n")


def run_examples():
    """Run a set of example queries to demonstrate the system."""
    print_header()
    print("\n🎯 Running example scenarios...\n")

    config = {"configurable": {"thread_id": "examples"}}

    examples = [
        {
            "title": "Company Overview",
            "query": "Give me a comprehensive company overview",
        },
        {
            "title": "Employee Skills Search",
            "query": "Who are our employees with Tank Installation skills?",
        },
        {
            "title": "Project Quote",
            "query": "Calculate a quote for a Tank Installation project with 80 hours of labor and $10,000 in materials",
        },
        {
            "title": "Strategic Analysis",
            "query": "Should we bid on a Station Construction project in Colon (interior) for Delta Petroleum, estimated 500 hours and $30,000 in materials?",
        },
    ]

    for i, example in enumerate(examples, 1):
        print("\n" + "=" * 80)
        print(f"Example {i}: {example['title']}")
        print("=" * 80)
        print(f"\n📝 Query: {example['query']}\n")

        response = app.invoke(
            {"messages": [{"role": "user", "content": example["query"]}]},
            config,
        )

        last_message = response["messages"][-1]
        print(f"🤖 Response:\n{last_message.content}\n")

        if i < len(examples):
            input("\nPress Enter to continue to next example...")

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    import os

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  WARNING: OPENAI_API_KEY environment variable not set!")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'\n")
        sys.exit(1)

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--examples", "-e"]:
            run_examples()
        elif sys.argv[1] in ["--help", "-h"]:
            print("\nMaster Services Simulation - Usage:")
            print("\n  python run_simulation.py          - Run interactive mode")
            print("  python run_simulation.py -e       - Run example scenarios")
            print("  python run_simulation.py -h       - Show this help\n")
        else:
            print(f"\nUnknown option: {sys.argv[1]}")
            print("Use --help for usage information\n")
    else:
        # Run interactive mode by default
        run_interactive()
