#!/usr/bin/env python3
"""
Test script to demonstrate and compare the dynamic routing agent
with the original supervisor-based routing approach.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph.workflow import app as original_app
from graph.dynamic_workflow import app as dynamic_app


def test_query(query: str, description: str = ""):
    """Test a query with both original and dynamic routing approaches."""
    print(f"\n{'='*80}")
    print(f"TEST: {description if description else query}")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    # Test with original supervisor-based approach
    print("\n🔹 ORIGINAL SUPERVISOR APPROACH:")
    print("-" * 50)
    try:
        original_result = original_app.invoke({"query": query})
        print(f"Route: {original_result.get('route', 'Unknown')}")
        print(f"Response: {original_result.get('response', 'No response')}")
    except Exception as e:
        print(f"Error with original approach: {str(e)}")
    
    # Test with dynamic routing approach
    print("\n🔸 DYNAMIC ROUTING APPROACH:")
    print("-" * 50)
    try:
        dynamic_result = dynamic_app.invoke({"query": query})
        print(f"Route: {dynamic_result.get('route', 'Unknown')}")
        print(f"Response: {dynamic_result.get('response', 'No response')}")
    except Exception as e:
        print(f"Error with dynamic approach: {str(e)}")


def main():
    """Run comprehensive tests to compare routing approaches."""
    
    print("🚀 DYNAMIC ROUTING AGENT TEST SUITE")
    print("Comparing original supervisor routing vs. dynamic tool selection")
    
    # Test cases covering different scenarios
    test_cases = [
        {
            "query": "How do I install VPN software on my laptop?",
            "description": "Clear IT Query"
        },
        {
            "query": "What is the reimbursement policy for travel expenses?", 
            "description": "Clear Finance Query"
        },
        {
            "query": "I need help with my payroll and also setting up SSH access to the server",
            "description": "Mixed IT + Finance Query"
        },
        {
            "query": "What are the latest cybersecurity trends in 2024?",
            "description": "External IT Knowledge Query"
        },
        {
            "query": "How do I submit an expense report and what are the approval procedures?",
            "description": "Finance Process Query"
        },
        {
            "query": "What is the weather like today?",
            "description": "Unrelated Query"
        }
    ]
    
    # Run all test cases
    for test_case in test_cases:
        test_query(test_case["query"], test_case["description"])


if __name__ == "__main__":
    main()
