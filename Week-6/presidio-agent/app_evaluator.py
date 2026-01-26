import asyncio
import json
import time
from datetime import datetime

from agentevals.trajectory.llm import create_async_trajectory_llm_as_judge
from agentevals.trajectory.match import create_async_trajectory_match_evaluator

from agent import agent  


def compute_test_score(result):
    score = 100
    suggestions = []

    correctness = result.get("correctness_score", 0)
    latency = result.get("latency", 0)
    requires_tool = result.get("requires_tool", False)
    tool_success = result.get("tool_success", True)
    hallucination = result.get("hallucination", False)

    if correctness < 0.7:
        score -= 40
        suggestions.append("Improve factual correctness of the final answer.")

    if requires_tool and not tool_success:
        score -= 20
        suggestions.append("Ensure required tools are invoked.")

    if hallucination:
        score -= 30
        suggestions.append("Avoid hallucinations; refuse or cite sources.")

    if latency > 10:
        score -= 10
        suggestions.append("Optimize latency (slow reasoning or tools).")

    return max(score, 0), suggestions



def compute_metrics(results):
    total = len(results)

    correctness_avg = sum(r["correctness_score"] for r in results) / total
    avg_latency = sum(r["latency"] for r in results) / total

    refusal_cases = sum(1 for r in results if r["is_refusal_case"])
    hallucinations = sum(1 for r in results if r["hallucination"])

    tool_required = sum(1 for r in results if r["requires_tool"])
    tool_success = sum(1 for r in results if r["requires_tool"] and r["tool_success"])

    overall_pass = sum(1 for r in results if r["eval_score"])

    return {
        "overall_pass_rate": overall_pass / total,
        "avg_correctness": correctness_avg,
        "avg_latency": avg_latency,
        "tool_success_rate": tool_success / tool_required if tool_required else 1.0,
        "hallucination_rate": hallucinations / refusal_cases if refusal_cases else 0.0,
        "total_tests": total,
        "refusal_cases": refusal_cases,
        "hallucinations_detected": hallucinations,
        "tool_required": tool_required,
        "tool_success": tool_success,
    }

def generate_markdown_report(results, metrics):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# Presidio Agent Evaluation Report

**Generated:** {timestamp}  
**Agent:** Presidio HR AI Agent  
**Evaluation Framework:** AgentEvals + LLM-as-Judge + Tool Analysis

---

## Executive Summary

| Metric | Value |
|------|------|
| **Overall Pass Rate** | {metrics['overall_pass_rate']:.1%} |
| **Average Correctness** | {metrics['avg_correctness']:.2f} |
| **Average Latency** | {metrics['avg_latency']:.2f}s |
| **Tool Usage Success** | {metrics['tool_success_rate']:.1%} |
| **Hallucination Rate** | {metrics['hallucination_rate']:.1%} |
| **Total Test Cases** | {metrics['total_tests']} |

---

## Detailed Test Results

"""

    for i, r in enumerate(results, 1):
        report += f"""### Test Case {i}

**Query:** {r['input']}  
**Expected:** {r['expected']}  
**Response:** {r['output'][:300]}{'...' if len(r['output']) > 300 else ''}

| Metric | Value |
|------|------|
| Latency | {r['latency']:.2f}s |
| Correctness | {r['correctness_score']:.2f} |
| Relevance | {r['relevance_score']:.2f} |
| Helpfulness | {r['helpfulness_score']:.2f} |
| Tool Usage | {'✅' if r['tool_success'] else '❌'} |
| Hallucination | {'⚠️ Yes' if r['hallucination'] else '✅ No'} |
| AgentEvals Score | {r['eval_score_value']:.2f} |
| Final Score | **{r['final_score']} / 100** |

**Suggestions:**
"""
        if r["suggestions"]:
            for s in r["suggestions"]:
                report += f"- {s}\n"
        else:
            report += "- No issues detected. Good performance.\n"

        report += "\n---\n"

    report += """## Overall Recommendations

- Improve correctness on policy-related queries by strengthening retrieval grounding.
- Reduce unnecessary refusals on simple, safe questions.
- Monitor latency for tool-heavy queries.
- Maintain strong refusal behavior to prevent hallucinations.

---

*Generated automatically by Presidio Agent Evaluation Pipeline*
"""

    return report


# Serialize LC messages
def serialize_trajectory(messages):
    serialized = []
    for msg in messages:
        rec = {"type": msg.type, "content": msg.content}
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            rec["tool_calls"] = msg.tool_calls
        if hasattr(msg, "additional_kwargs") and "tool_calls" in msg.additional_kwargs:
            rec["tool_calls"] = msg.additional_kwargs["tool_calls"]
        serialized.append(rec)
    return serialized


# LLM judge evaluator
trajectory_judge = create_async_trajectory_llm_as_judge(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0"
)

# Trajectory match evaluator (strict mode)
trajectory_match = create_async_trajectory_match_evaluator(
    trajectory_match_mode="strict",  # strict expected ordering
)

TEST_DATA = [
    {
        "input": "What is 2 + 2?",
        "expected_answer": "I dont have specific tools for math, but the answer is 4.",
        "expected_tool_calls": [],
    },
    {
        "input": "Lookup company policy for PTO Carryover",
        "expected_answer": "Paid Time Off Carryover is ...",
        "expected_tool_calls": ["rag_search"],
    },
        {
        "input": "What AI tools are approved for employees to use at Presidio?",
        "expected_answer": "Microsoft Copilot, Presidio AI Assistant, Github copilot, Grammarly business ...",
        "expected_tool_calls": ["rag_search"],
    },
    {
        "input": "How does Presidio's PTO carryover policy compare to industry standards in the U.S. and globally?",
        "expected_answer": "Presidio's PTO carryover policy aligns with common U.S. industry practices by allowing limited carryover, while globally PTO policies vary by country and regulation.",
        "expected_tool_calls": ["web_search"],
    },
    {
        "input": "What is the disciplinary process if an employee repeatedly violates company policy for 3rd time?",
        "expected_answer": "Termination ...",
        "expected_tool_calls": ["rag_search"],
    },
    {
        "input": "What is Presidio's Equal Employment Opportunity (EEO) policy, and how can employees report discrimination?",
        "expected_answer": "All recruitment decisions are based solely on qualifications, skills, and cultural alignment.",
        "expected_tool_calls": ["rag_search"],
    }
]



async def run_and_evaluate(test_case):
    start_time = time.time()

    result = await agent.ainvoke(
        {"messages": [("user", test_case["input"])]}
    )

    latency = time.time() - start_time

    raw_msgs = result["messages"]
    final_ai_msgs = [m for m in raw_msgs if m.type == "ai"]
    final_answer = final_ai_msgs[-1].content if final_ai_msgs else ""

    # Judge
    judge_eval = await trajectory_judge(
        trajectory=raw_msgs,
        outputs=final_ai_msgs,
        reference_outputs=[
            {"role": "assistant", "content": test_case["expected_answer"]}
        ],
    )

    # Tool usage detection
    tool_calls = [
        m for m in raw_msgs
        if hasattr(m, "tool_calls") and m.tool_calls
    ]

    requires_tool = len(test_case["expected_tool_calls"]) > 0
    tool_success = (
        not requires_tool
        or len(tool_calls) > 0
    )

    # Simple hallucination heuristic
    hallucination = (
        "I don't have" in final_answer.lower()
        and not test_case["expected_tool_calls"]
    )

    return {
        "input": test_case["input"],
        "expected": test_case["expected_answer"],
        "output": final_answer,

        # AgentEvals
        "eval_score": judge_eval["score"],
        "eval_score_value": float(judge_eval["score"]),
        "eval_reasoning": judge_eval.get("reasoning"),

        # Derived metrics
        "correctness_score": 1.0 if judge_eval["score"] else 0.0,
        "relevance_score": 1.0 if judge_eval["score"] else 0.5,
        "helpfulness_score": 1.0 if judge_eval["score"] else 0.5,

        "latency": latency,
        "requires_tool": requires_tool,
        "tool_success": tool_success,

        "hallucination": hallucination,
        "is_refusal_case": "don't have" in final_answer.lower(),
    }





async def main():
    results = []
    for case in TEST_DATA:
        res = await run_and_evaluate(case)
        results.append(res)

    # Enrich results with scores & suggestions
    for r in results:
        final_score, suggestions = compute_test_score(r)
        r["final_score"] = final_score
        r["suggestions"] = suggestions

    metrics = compute_metrics(results)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Markdown
    md_report = generate_markdown_report(results, metrics)
    md_path = f"agent_eval_report_{timestamp}.md"
    with open(md_path, "w") as f:
        f.write(md_report)

    # JSON
    json_path = f"agent_eval_results_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(
            {
                "generated_at": timestamp,
                "metrics": metrics,
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"📄 Markdown report saved: {md_path}")
    print(f"📊 JSON results saved: {json_path}")


    return results

# run
results = asyncio.run(main())
