import os
import json
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any

import requests
from dotenv import load_dotenv

from openai import OpenAI

import boto3


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AWS_REGION = os.getenv("AWS_REGION_NAME")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/chat")


if not all([OPENAI_API_KEY, AWS_REGION]):
    missing = [k for k, v in {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "AWS_REGION_NAME": AWS_REGION
    }.items() if not v]
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")


# ──────────────────────────────────────────────── Clients ───
openai_client = OpenAI(api_key=OPENAI_API_KEY)
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)


# ──────────────────────────────────────────────── Query functions ───
def query_openai(model_id: str, prompt: str) -> Tuple[str, Optional[float]]:
    try:
        start = datetime.now()
        resp = openai_client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        latency_ms = (datetime.now() - start).total_seconds() * 1000
        return resp.choices[0].message.content, round(latency_ms, 2)
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {str(e)}", None



def query_bedrock(model_id: str, prompt: str) -> Tuple[str, Optional[float]]:
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    }

    try:
        start = datetime.now()
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        result = json.loads(response["body"].read())
        latency_ms = (datetime.now() - start).total_seconds() * 1000
        return result["content"][0]["text"], round(latency_ms, 2)
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {str(e)}", None


def query_ollama(model_id: str, prompt: str) -> Tuple[str, Optional[float]]:
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.0}
    }

    try:
        start = datetime.now()
        r = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        latency_ms = (datetime.now() - start).total_seconds() * 1000

        content = data.get("message", {}).get("content")
        if content is not None:
            return content, round(latency_ms, 2)

        return f"ERROR: Unexpected Ollama response format", round(latency_ms, 2)

    except Exception as e:
        return f"ERROR: {type(e).__name__}: {str(e)}", None



MODELS = [
    {"name": "GPT-4o",               "provider": "openai",    "id": "gpt-4o"},
    {"name": "Claude 3 Sonnet",      "provider": "bedrock",   "id": "anthropic.claude-3-sonnet-20240229-v1:0"},
    {"name": "DeepSeek R1 7B",       "provider": "ollama",    "id": "deepseek-r1:7b"},
]



EVALUATION_TASKS = [
    {
        "category": "AppDev (Code Generation)",
        "id": "factorial",
        "title": "Python Factorial",
        "prompt": "Write a python program to find factorial of given number."
    },
    {
        "category": "Data (SQL Generation & Analysis)",
        "id": "sql_orders_jan2026",
        "title": "Orders in January 2026",
        "prompt": "Write a SQL query to show all orders placed in January 2026. Table: orders (order_id, customer_id, order_date)"
    },
    {
        "category": "DevOps (Infrastructure Automation)",
        "id": "devops_k8s_restart",
        "title": "K8s Pod Restart",
        "prompt": "How do you restart / recreate a single pod in Kubernetes using kubectl?"
    },
]


QUERY_FUNCTIONS = {
    "openai":  query_openai,
    "bedrock": query_bedrock,
    "ollama":  query_ollama,
}


def run_evaluation() -> List[Dict[str, Any]]:
    results = []

    for model in MODELS:
        print(f"Evaluating: {model['name']}")

        query_fn = QUERY_FUNCTIONS.get(model["provider"])
        if not query_fn:
            print(f"  → Skipping: unknown provider {model['provider']}")
            continue

        for task in EVALUATION_TASKS:
            print(f"  • {task['title']}")

            response, latency_ms = query_fn(model["id"], task["prompt"])

            results.append({
                "model": model["name"],
                "provider": model["provider"],
                "category": task["category"],
                "task_id": task["id"],
                "task_title": task["title"],
                "prompt": task["prompt"],
                "response": response,
                "latency_ms": latency_ms,
            })

    return results


def main():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    raw_file = f"ai_evaluation_raw_{timestamp}.json"

    results = run_evaluation()

    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved → {raw_file}")

    with open(raw_file, encoding="utf-8") as f:
        annotated = json.load(f)


if __name__ == "__main__":
    main()