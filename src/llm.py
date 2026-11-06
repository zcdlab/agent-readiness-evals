import json
import os
import urllib.request
from src.models import ReadinessReport


def is_demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")


def get_api_key() -> tuple[str | None, str]:
    if is_demo_mode():
        return None, "demo"
    for provider, key_name in (("openai", "OPENAI_API_KEY"), ("gemini", "GEMINI_API_KEY"), ("anthropic", "ANTHROPIC_API_KEY")):
        val = os.getenv(key_name)
        if val:
            return val, provider
    return None, "none"


def call_llm(prompt: str, system: str = "") -> str | None:
    api_key, _ = get_api_key()
    if not api_key:
        return None
    url = os.getenv("LLM_API_BASE", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system or "You are an enterprise AI agent governance architect."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def synthesize_contracts(report: ReadinessReport, force_llm: bool = False) -> tuple[str, str, str]:
    if force_llm or (not is_demo_mode() and get_api_key()[0]):
        prompt = (
            f"Repo: {report.repo_name}\nStack: {report.detected_stack}\n"
            f"Sensitive: {report.discovered_sensitive_paths}\n"
            f"Generate YAML policy and AGENTS.md separated by ===SPLIT==="
        )
        out = call_llm(prompt)
        if out and "===SPLIT===" in out:
            parts = out.split("===SPLIT===")
            return parts[0].strip(), parts[1].strip(), "llm_synthesized"
    return report.generated_policy_yaml, report.generated_agents_md, "precalculated_deterministic"
