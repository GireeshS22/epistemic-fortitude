"""Debug: why does GPT-5.1 arbiter condition use fewer tokens than baseline?"""

import json
from pathlib import Path
import statistics

LOGS = Path(__file__).resolve().parents[2] / "logs" / "experiments"

def load(d):
    out = []
    for p in sorted(d.glob("*.json")):
        if p.name == "conversations_summary.json":
            continue
        try:
            obj = json.load(open(p, encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "turns" in obj:
            out.append(obj)
    return out

def analyse(label, convs):
    t1_in, t1_out, t2_in, t2_out = [], [], [], []
    t1_lat, t2_lat = [], []
    t2_routed = {"primary": 0, "arbiter": 0}
    for c in convs:
        for t in c.get("turns", []):
            tn = t.get("turn_number", 0)
            tc = t.get("token_counts") or {}
            ip = tc.get("prompt_tokens", 0)
            op = tc.get("completion_tokens", 0)
            lat = t.get("latency_ms", 0)
            if tn == 1:
                t1_in.append(ip); t1_out.append(op); t1_lat.append(lat)
            elif tn == 2:
                t2_in.append(ip); t2_out.append(op); t2_lat.append(lat)
                t2_routed[t.get("routed_to", "primary")] = t2_routed.get(t.get("routed_to","primary"), 0) + 1
    def m(xs):
        return statistics.mean(xs) if xs else 0
    print(f"--- {label} (n={len(convs)} convs) ---")
    print(f"  Turn 1: in={m(t1_in):.0f}  out={m(t1_out):.0f}  total={m(t1_in)+m(t1_out):.0f}  lat={m(t1_lat)/1000:.1f}s")
    print(f"  Turn 2: in={m(t2_in):.0f}  out={m(t2_out):.0f}  total={m(t2_in)+m(t2_out):.0f}  lat={m(t2_lat)/1000:.1f}s")
    print(f"  Turn 2 routing: {t2_routed}")
    print()

base = load(LOGS / "swebench_langgraph_gpt-5-1_baseline")
arbi = load(LOGS / "swebench_langgraph_gpt-5-1_arbiter")
analyse("GPT-5.1 baseline", base)
analyse("GPT-5.1 arbiter ", arbi)

# Same for Gemini for comparison
gbase = load(LOGS / "swebench_langgraph_baseline")
garbi = load(LOGS / "swebench_langgraph_arbiter")
analyse("Gemini baseline", gbase)
analyse("Gemini arbiter ", garbi)
