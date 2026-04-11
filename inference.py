import os
from openai import OpenAI
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = """You are a professional fact-checker and misinformation analyst.
Your job is to analyze news claims and articles carefully.
Always reply concisely and directly as instructed."""


def call_llm(user_message: str) -> str:
    """Call the LLM and return its text response."""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM call failed: {e}")
        return ""


def run_task(task_id: str) -> float:
    """Run one full episode for a given task. Returns score 0.0-1.0."""
    print(f"\n{'='*50}")
    print(f"Running: {task_id}")
    print('='*50)

    # Reset environment
    reset_resp = requests.post(
        f"{ENV_URL}/reset",
        json={"task_id": task_id}
    )
    obs = reset_resp.json()

    print(f"Instruction: {obs['instruction']}")
    print(f"Text: {obs['text'][:150]}...")

    # Build prompt for LLM
    prompt = f"""INSTRUCTION: {obs['instruction']}

TEXT TO ANALYZE:
{obs['text']}

Your response:"""

    # Get LLM answer
    llm_answer = call_llm(prompt)
    print(f"LLM Answer: {llm_answer[:200]}")

    # Determine action type from task
    if "classify" in task_id:
        action_type = "classify"
    elif "locate" in task_id:
        action_type = "locate"
    else:
        action_type = "correct"

    # Send action to environment
    step_resp = requests.post(
        f"{ENV_URL}/step",
        json={
            "action_type": action_type,
            "content": llm_answer
        }
    )
    result = step_resp.json()

    score = result["reward"]["score"]
    feedback = result["reward"]["feedback"]

    print(f"Score: {score}")
    print(f"Feedback: {feedback}")

    return score


def main():
    print("Misinformation Detector — Baseline Inference")
    print("Running all 3 tasks...\n")

    task_ids = ["task_1_classify", "task_2_locate", "task_3_correct"]
    scores = {}

    for task_id in task_ids:
        score = run_task(task_id)
        scores[task_id] = score

    print(f"\n{'='*50}")
    print("FINAL RESULTS")
    print('='*50)
    for task_id, score in scores.items():
        difficulty = {"task_1_classify": "Easy",
                      "task_2_locate": "Medium",
                      "task_3_correct": "Hard"}[task_id]
        print(f"{difficulty:8} | {task_id:25} | Score: {score:.2f}")

    avg = sum(scores.values()) / len(scores)
    print(f"\nAverage Score: {avg:.2f} / 1.00")
    print("Baseline run complete.")


if __name__ == "__main__":
    main()
