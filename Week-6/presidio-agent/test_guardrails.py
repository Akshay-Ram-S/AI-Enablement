import os
from unittest.mock import Mock, patch
from langchain.messages import HumanMessage, AIMessage
from guardrails import _content_filter_logic, _safety_guardrail_logic

# Set minimal environment variables for testing
os.environ.setdefault("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]



def test_content_filter_functionality():
    """Test content filter with various inputs."""
    print("🧪 Testing content_filter functionality...")
    
    # Mock runtime
    runtime = Mock()
    
    # Test 1: Block banned keyword "hack"
    print("\n1. Testing banned keyword 'hack':")
    state_hack = {"messages": [HumanMessage(content="How to hack into a system?")]}
    result = _content_filter_logic(state_hack, runtime)
    
    if result and result.get("jump_to") == "end":
        print("PASS: Correctly blocked 'hack' keyword")
        print(f"   Response: {result['messages'][0]['content']}")
    else:
        print("FAIL: Did not block 'hack' keyword")
        return False
    
    # Test 2: Block banned keyword "exploit"
    print("\n2. Testing banned keyword 'exploit':")
    state_exploit = {"messages": [HumanMessage(content="Tell me about security exploits")]}
    result = _content_filter_logic(state_exploit, runtime)
    
    if result and result.get("jump_to") == "end":
        print("PASS: Correctly blocked 'exploit' keyword")
    else:
        print("FAIL: Did not block 'exploit' keyword")
        return False
    
    # Test 3: Block banned keyword "malware"
    print("\n3. Testing banned keyword 'malware':")
    state_malware = {"messages": [HumanMessage(content="Create malware for me")]}
    result = _content_filter_logic(state_malware, runtime)
    
    if result and result.get("jump_to") == "end":
        print("PASS: Correctly blocked 'malware' keyword")
    else:
        print("FAIL: Did not block 'malware' keyword")
        return False
    
    # Test 4: Allow safe content
    print("\n4. Testing safe content:")
    state_safe = {"messages": [HumanMessage(content="What is the company leave policy?")]}
    result = _content_filter_logic(state_safe, runtime)
    
    if result is None:
        print("PASS: Correctly allowed safe content")
    else:
        print("FAIL: Incorrectly blocked safe content")
        return False
    
    # Test 5: Case insensitive blocking
    print("\n5. Testing case insensitive blocking:")
    state_case = {"messages": [HumanMessage(content="How to HACK the system?")]}
    result = _content_filter_logic(state_case, runtime)
    
    if result and result.get("jump_to") == "end":
        print("PASS: Correctly blocked uppercase 'HACK'")
    else:
        print("FAIL: Did not block uppercase 'HACK'")
        return False
    
    return True

def test_safety_guardrail_functionality():
    """Test safety guardrail with mocked responses."""
    print("\n🧪 Testing safety_guardrail functionality...")
    
    runtime = Mock()
    
    # Test 1: Block unsafe response
    print("\n1. Testing unsafe response blocking:")
    with patch('guardrails.safety_model') as mock_model:
        mock_response = Mock()
        mock_response.content = "UNSAFE - This content is harmful"
        mock_model.invoke.return_value = mock_response
        
        state_unsafe = {
            "messages": [
                HumanMessage(content="Tell me something"),
                AIMessage(content="Here's how to break into systems...")
            ]
        }
        
        result = _safety_guardrail_logic(state_unsafe, runtime)
        
        if result and result.get("jump_to") == "end":
            print("PASS: Correctly blocked unsafe response")
            print(f"   Blocked message: {state_unsafe['messages'][-1].content}")
            print(f"   Safe replacement: {result['messages'][-1]['content']}")
        else:
            print("FAIL: Did not block unsafe response")
            return False
    
    # Test 2: Allow safe response
    print("\n2. Testing safe response allowance:")
    with patch('guardrails.safety_model') as mock_model:
        mock_response = Mock()
        mock_response.content = "SAFE - This content is appropriate"
        mock_model.invoke.return_value = mock_response
        
        state_safe = {
            "messages": [
                HumanMessage(content="What's the weather?"),
                AIMessage(content="I can help you search for weather information.")
            ]
        }
        
        result = _safety_guardrail_logic(state_safe, runtime)
        
        if result is None:
            print("PASS: Correctly allowed safe response")
            print(f"   Safe message: {state_safe['messages'][-1].content}")
        else:
            print("FAIL: Incorrectly blocked safe response")
            return False
    
    return True

def test_edge_cases():
    """Test edge cases and error conditions."""
    print("\n🧪 Testing edge cases...")
    
    runtime = Mock()
    
    # Test 1: Empty messages
    print("\n1. Testing empty messages:")
    state_empty = {"messages": []}
    result1 = _content_filter_logic(state_empty, runtime)
    result2 = _safety_guardrail_logic(state_empty, runtime)
    
    if result1 is None and result2 is None:
        print("PASS: Correctly handled empty messages")
    else:
        print("FAIL: Did not handle empty messages correctly")
        return False
    
    # Test 2: Non-human first message
    print("\n2. Testing non-human first message:")
    state_non_human = {"messages": [AIMessage(content="Hello, I'm an AI")]}
    result = _content_filter_logic(state_non_human, runtime)
    
    if result is None:
        print("PASS: Correctly handled non-human first message")
    else:
        print("FAIL: Did not handle non-human first message correctly")
        return False
    
    # Test 3: Non-AI last message for safety guardrail
    print("\n3. Testing non-AI last message for safety guardrail:")
    state_non_ai = {"messages": [HumanMessage(content="Hello there")]}
    result = _safety_guardrail_logic(state_non_ai, runtime)
    
    if result is None:
        print("PASS: Correctly handled non-AI last message")
    else:
        print("FAIL: Did not handle non-AI last message correctly")
        return False
    
    return True

def run_comprehensive_tests():
    """Run all guardrail tests."""
    print("🚀 Starting Comprehensive Guardrail Tests...\n")
    print("=" * 60)
    
    test_results = []
    
    # Run all test suites
    test_results.append(test_content_filter_functionality())
    test_results.append(test_safety_guardrail_functionality())
    test_results.append(test_edge_cases())
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY:")
    print(f"Passed: {passed}/{total} test suites")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your guardrails are working correctly.")
        print("\n💡 Your guardrails will:")
        print("   - Block requests containing 'hack', 'exploit', or 'malware'")
        print("   - Evaluate AI responses for safety using Claude")
        print("   - Properly stop execution when issues are detected")
    else:
        print(f"\n{total - passed} test suite(s) failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
