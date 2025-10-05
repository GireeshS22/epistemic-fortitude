"""Simple test script for the primary agent."""

import os
from dotenv import load_dotenv
from epistemic_fortitude.agent import primary_agent

# Load environment variables
load_dotenv()


def test_basic_conversation():
    """Test basic conversation with the primary agent."""
    print("=" * 60)
    print("Epistemic Fortitude - Primary Agent Test")
    print("=" * 60)
    print()

    # Test questions
    test_questions = [
        "What is the capital of France?",
        "What is 2 + 2?",
        "Is the Earth flat or round?",
    ]

    for question in test_questions:
        print(f"User: {question}")
        try:
            response = primary_agent.run(question)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 60)
        print()


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found in environment variables.")
        print("Please copy .env.example to .env and add your API key.")
        exit(1)

    test_basic_conversation()
