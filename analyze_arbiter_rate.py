import json
import os
from collections import Counter

DIR = r"C:\Users\ADMIN\OneDrive\Documents\SNUC\Consistency-Preserving-Architectures\epistemic_fortitude\logs\experiments\swebench_langgraph_gpt-5-1_arbiter"
SKIP = {"metadata.json", "conversations_summary.json", "errors.json"}

total = 0
routed_arbiter = 0
routed_primary = 0
routed_other = 0
routing_reasons = Counter()
contradiction_tiers = Counter()
contradiction_mechanisms = Counter()
errors = []

for fname in sorted(os.listdir(DIR)):
    if not fname.endswith(".json") or fname in SKIP:
        continue
    total += 1
    fpath = os.path.join(DIR, fname)
    try:
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        errors.append((fname, str(e)))
        continue

    turns = data.get("turns", [])
    # Find Turn 2 (the contradiction turn)
    turn2 = None
    for t in turns:
        if t.get("turn_number") == 2:
            turn2 = t
            break
    if turn2 is None:
        errors.append((fname, "No turn_number=2 found"))
        continue

    routed = turn2.get("routed_to", "unknown")
    if routed == "arbiter":
        routed_arbiter += 1
    elif routed == "primary":
        routed_primary += 1
    else:
        routed_other += 1

    reason = turn2.get("routing_reason") or turn2.get("contradiction_mechanism") or "none"
    routing_reasons[reason] += 1

    tier = turn2.get("contradiction_tier", "unknown")
    contradiction_tiers[tier] += 1

    mechanism = turn2.get("contradiction_mechanism", "unknown")
    contradiction_mechanisms[mechanism] += 1

print("=" * 65)
print("ARBITER CALL RATE ANALYSIS - GPT-5-1 Arbiter (SWE-bench)")
print("=" * 65)
print(f"Total experiment JSON files:  {total}")
print(f"  Routed to ARBITER on Turn 2: {routed_arbiter}")
print(f"  Routed to PRIMARY on Turn 2: {routed_primary}")
if routed_other:
    print(f"  Routed to OTHER on Turn 2:   {routed_other}")
print("-" * 65)
rate = (routed_arbiter / total * 100) if total else 0
print(f"  Arbiter call rate:           {rate:.1f}% ({routed_arbiter}/{total})")
print()

print("Breakdown by Contradiction Tier:")
print("-" * 40)
for tier in sorted(contradiction_tiers):
    print(f"  Tier {tier}: {contradiction_tiers[tier]}")
print()

print("Breakdown by Contradiction Mechanism:")
print("-" * 40)
for mech, cnt in contradiction_mechanisms.most_common():
    print(f"  {mech:30s} {cnt:4d}")
print()

print("Breakdown by Routing Reason / Mechanism:")
print("-" * 40)
for reason, cnt in routing_reasons.most_common():
    print(f"  {reason:30s} {cnt:4d}")

if errors:
    print(f"\nErrors ({len(errors)}):")
    for fname, err in errors[:10]:
        print(f"  {fname}: {err}")

print()
