import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.agent import critique, decide
from fixtures import FIXTURES, WRONG_DECISION


def run():
    metrics = [{k: v for k, v in row.items() if k != "label"} for row in FIXTURES]
    labels = {(r["platform"], r["campaign"], r["ad_set"]): r["label"] for r in FIXTURES}

    decisions = decide(metrics)
    correct = 0
    print("Decision accuracy check")
    print("-" * 48)
    for decision in decisions:
        key = (decision["platform"], decision["campaign"], decision["ad_set"])
        expected = labels.get(key)
        got = decision["decision"]
        hit = expected == got
        correct += int(hit)
        mark = "ok " if hit else "MISS"
        print(f"[{mark}] {key[2]:<22} expected={expected:<6} got={got}")

    accuracy = round(100 * correct / len(FIXTURES), 1)
    print("-" * 48)
    print(f"Decision accuracy: {accuracy}%  ({correct}/{len(FIXTURES)})")

    wrong_metric = next(m for m in metrics if m["ad_set"] == "Discount Angle")
    checked = critique([wrong_metric], [dict(WRONG_DECISION)])[0]
    caught = checked["decision"] != "scale" or not checked.get("verified", True)
    print()
    print("Self-critique check (planted a false 'scale' on a losing ad set)")
    print("-" * 48)
    print(f"decision after critique: {checked['decision']}")
    print(f"verified flag: {checked.get('verified')}")
    print(f"note: {checked.get('critique_note')}")
    print(f"caught the bad call: {caught}")


if __name__ == "__main__":
    run()
