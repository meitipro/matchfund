"""Deploy Match to StudioNet and put every path on the explorer.

    pip install genlayer-py==0.18.0
    python scripts/demo.py

The run deploys contracts/match.py exactly as it is in this repository, then
sends the steps in scripts/demo_data.py (STEPS), including the ones that end in
a refusal, and writes what happened to deployments/studionet.json: every
transaction hash, its sender and status, the refusal sentence where there was
one, the fund and every gift as the chain holds them, and the balance of every
wallet that was paid, read before and again once every payment had landed.
Nothing in that file is typed by hand.

Ten accounts, each in one role: the matcher, four donors, a stranger, and four
recipients that only ever receive. They are made in memory for this run and
never written to disk; the payers are funded from the StudioNet faucet.
"""

import datetime
import hashlib
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent))
import demo_data as D                                       # noqa: E402
from studio import EXPLORER, Studio                         # noqa: E402

ROOT = pathlib.Path(__file__).absolute().parent.parent
SOURCE = ROOT / "contracts" / "match.py"
OUT = ROOT / "deployments" / "studionet.json"

PAYERS = {"matcher": 2, "ann": 1, "ben": 1, "cal": 1, "dev": 1, "stranger": 1}
RECIPIENTS = ("club", "library", "pitch", "ward")


def utc_seconds(iso):
    t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return int(t.timestamp())


def wait_past(iso, label):
    """Sleep until the chain clock has passed `iso`, with a margin, because
    the contract compares against the time of the transaction that arrives."""
    target = utc_seconds(iso) + 20
    left = target - int(time.time())
    if left > 0:
        print(f"  waiting {left}s for {label} ({iso})")
        time.sleep(left)


def wait_for_balance(s, address, at_least, label, tries=24):
    """A payment can land a little after the transaction that sent it, so the
    balance is read until it has arrived rather than once."""
    for _ in range(tries):
        b = s.balance(address)
        if b >= at_least:
            return b
        time.sleep(5)
    print(f"  {label}: the payment had not landed after {tries * 5}s")
    return s.balance(address)


def args_for(method, spec, who):
    if method == "give":
        fid, to, cause = spec
        return [fid, who[to].address, cause]
    return list(spec)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    code = SOURCE.read_text(encoding="utf-8")
    s = Studio()

    print("\naccounts (in memory, StudioNet test GEN only)")
    who = {name: s.account(name, gen=gen) for name, gen in PAYERS.items()}
    who.update({name: s.account(name) for name in RECIPIENTS})
    before = {name: s.balance(who[name].address) for name in RECIPIENTS}

    print("\ndeploy")
    address = s.deploy(who["matcher"], code, [])

    print("\nthe demo")
    for step in D.STEPS:
        actor, method, spec, value, expect, label = step[:6]
        if "after_close" in step[6:]:
            wait_past(s.read(address, "fund", [0])["closes_at"], "the window to close")
        if method == "close" and expect == "ok":
            before["matcher"] = s.balance(who["matcher"].address)
        s.write(who[actor], address, method, args_for(method, spec, who), value=value, step=label, expect=expect)

    n = int(s.read(address, "count"))
    funds = [{
        "fund": s.read(address, "fund", [k]),
        "gifts": s.read(address, "gifts_of", [k])["gifts"],
    } for k in range(n)]

    # what the contract says each wallet is owed, then wait until it has landed
    owed = {name: 0 for name in before}
    by_address = {who[name].address.lower(): name for name in before}
    for g in funds[0]["gifts"]:
        owed[by_address[g["recipient"].lower()]] += int(g["amount"]) + int(g["matched"])
    owed["matcher"] = int(funds[0]["fund"]["returned"])
    after = {name: wait_for_balance(s, who[name].address, before[name] + owed[name], name) for name in before}

    record = {
        "network": "studionet",
        "chain_id": 61999,
        "contract": address,
        "explorer": f"{EXPLORER}/address/{address}",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "constructor": {},
        "accounts": {name: a.address for name, a in who.items()},
        "balances": {f"{name}_{when}": str(v[name]) for when, v in (("before", before), ("after", after))
                     for name in before},
        "owed": {name: str(v) for name, v in owed.items()},
        "held_after": str(s.read(address, "held_total")),
        "steps": s.log,
        "funds": funds,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")

    print(f"\n  contract   {address}")
    print(f"  explorer   {EXPLORER}/address/{address}")
    f = funds[0]["fund"]
    print(f"  fund 0     {f['status']}  matched {f['matched_total']}  given {f['given_total']}  "
          f"returned {f['returned']}")
    print(f"  verdicts   {[(g['id'], g['verdict'], g['matched']) for g in funds[0]['gifts']]}")
    for name in before:
        print(f"  {name:<9} gained {after[name] - before[name]}  owed {owed[name]}")
    print(f"  written    {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
