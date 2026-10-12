"""Mutation pass: break every defence on purpose, confirm a test notices.

Passing tests prove nothing on their own. Each entry below is a small edit to
the contract that removes a defence. The suite must fail for every one of them,
and this script records WHICH test caught it, so the table in the README is
measured rather than claimed.

    python scripts/mutate.py            # run them all, print what caught what
    python scripts/mutate.py --md       # emit the markdown table for the README

An escaping mutation is a finding, not a nuisance: either a missing test, or a
later defence strict enough that an earlier test can no longer fail. The script
exits non-zero if anything escapes, and refuses to run on a red baseline.

Three rules keep the harness honest:

  * the unmutated suite must be green before anything is mutated;
  * a find string that is missing, or matches more than once, is a failure of
    the harness, never a skip, so refactoring cannot quietly turn a row off;
  * scripts/lift.py runs inside every mutated copy before the suite, so the lib
    parity test can never stand in for the behavioural test a mutation deserves.
"""

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).absolute().parent.parent
TARGET = "match.py"

FENCE = '    return str(raw).replace("<", "(").replace(">", ")").replace("[", "(").replace("]", ")")'
MATCH = "    want = int(gift) * int(ratio_pct) // 100\n    return max(0, min(want, int(cap), int(left)))"

MUTATIONS = [
    # -- reading the answer
    ("an option past the list is accepted", '    if k < 0 or k >= n:\n        return ""', '    if k < 0:\n        return ""'),
    ("an answer in words is read as a number",
     '    if s == "" or any(ch not in "0123456789" for ch in s) or len(s) > 2:', '    if s == "":'),

    # -- the two orders
    ("the second pass is asked in the forward order",
     "            rev, _ = ask(name, mission, text, REVERSED)", "            rev, _ = ask(name, mission, text, FORWARD)"),
    ("the reversed order is not reversed", "REVERSED = [OUTSIDE, FITS]", "REVERSED = [FITS, OUTSIDE]"),
    ("a disagreement between the orders keeps the forward verdict",
     "    return forward if forward == reverse else OUTSIDE", "    return forward"),
    ("a disagreement between the orders is fits",
     "    return forward if forward == reverse else OUTSIDE", "    return forward if forward == reverse else FITS"),
    ("an answer is not read back through its order", "    return order[int(choice)]", "    return FORWARD[int(choice)]"),

    # -- reading the model
    ("an unusable answer is not retried",
     "    for _ in range(2):\n        raw = gl.nondet.exec_prompt(", "    for _ in range(1):\n        raw = gl.nondet.exec_prompt("),
    ("an unusable answer is read as outside",
     '    raise gl.vm.UserError(f"{ERR_LLM} the model named neither option")', '    return OUTSIDE, ""'),
    ("an answer that is not an object crashes the block",
     "        if isinstance(raw, dict):\n            choice", "        if True:\n            choice"),

    # -- the validator
    ("the validator agrees with an error", "                return False\n            theirs", "                return True\n            theirs"),
    ("the validator skips the structural check",
     "            if not verdict_sound(proposed):\n                return False", "            if False:\n                return False"),
    ("the validator agrees with anything sound", '            return match_agrees(mine["verdict"], proposed)', "            return True"),
    ("the validator agrees when its own model fails",
     "            except gl.vm.UserError:\n                return False", "            except gl.vm.UserError:\n                return True"),
    ("agreement ignores soundness",
     "    return verdict_sound(mine) and verdict_sound(theirs) and str(mine) == str(theirs)", "    return str(mine) == str(theirs)"),

    # -- the deterministic half
    ("the agreed verdict is not checked again",
     "        if not verdict_sound(verdict):\n            raise", "        if False:\n            raise"),
    ("a gift outside the mission is matched", "if verdict == FITS else 0", "if verdict_sound(verdict) else 0"),
    ("the match ignores the ratio", MATCH, "    want = int(gift)\n    return max(0, min(want, int(cap), int(left)))"),
    ("the match ignores the cap", MATCH,
     "    want = int(gift) * int(ratio_pct) // 100\n    return max(0, min(want, int(left)))"),
    ("the match ignores what is left", MATCH,
     "    want = int(gift) * int(ratio_pct) // 100\n    return max(0, min(want, int(cap)))"),
    ("the pool is not drawn down", "            f.left = u256(int(f.left) - matched)", "            pass"),
    ("the matched total is not kept",
     "            f.matched_total = u256(int(f.matched_total) + matched)", "            pass"),
    ("the given total is not kept", "        f.given_total = u256(int(f.given_total) + amount)", "        pass"),
    ("the matched count is not kept", "            f.n_matched = u256(int(f.n_matched) + 1)", "            pass"),
    ("a matched recipient is not remembered", "            self.matched_to[recipient_key] = u256(gid + 1)", "            pass"),
    ("a donor's gifts are not counted",
     "        self.gifts_by[donor_key] = u256(int(self.gifts_by.get(donor_key, u256(0))) + 1)", "        pass"),
    ("the gift is kept and only the match is sent", "        self._send(to, amount + matched)", "        self._send(to, matched)"),
    ("the match is kept and only the gift is sent", "        self._send(to, amount + matched)", "        self._send(to, amount)"),
    ("the gift is not added to what is held",
     "        self.held = u256(int(self.held) + amount)\n        self._send(to", "        self._send(to"),
    ("a leader's reason is stored as sent",
     '            why=sanitise_reason(res.get("because", "")), next=u256(0),', '            why=str(res.get("because", "")), next=u256(0),'),
    ("a leader's reason is stored uncapped",
     '    return " ".join("".join(out).split())[:limit]', '    return " ".join("".join(out).split())'),
    ("gifts are not linked", "            self.gifts[int(f.last_gift)].next = u256(gid)", "            pass"),

    # -- the free refusals
    ("the matcher may give", "        if sender == f.matcher:\n            raise", "        if False:\n            raise"),
    ("a gift is taken on a closed fund",
     '        if str(f.status) != OPEN:\n            raise gl.vm.UserError(f"{ERR_EXPECTED} this fund is closed")',
     '        if False:\n            raise gl.vm.UserError(f"{ERR_EXPECTED} this fund is closed")'),
    ("gifts never close", "        if self._now() > int(f.closes_at):", "        if False:"),
    ("gifts close a second early", "        if self._now() > int(f.closes_at):", "        if self._now() >= int(f.closes_at):"),
    ("a gift may be empty", "        if amount < 1 or amount > MAX_AMOUNT:\n            raise gl.vm.UserError(f\"{ERR_EXPECTED} attach",
     "        if amount > MAX_AMOUNT:\n            raise gl.vm.UserError(f\"{ERR_EXPECTED} attach"),
    ("any recipient string is accepted", "        if not looks_like_address(recipient):\n            raise",
     "        if False:\n            raise"),
    ("a donor may give to itself", "        if to == sender:", "        if False:"),
    ("a gift to the matcher may be matched", "        if to == f.matcher:", "        if False:"),
    ("a donor gives without limit",
     "        if int(self.gifts_by.get(donor_key, u256(0))) >= MAX_PER_DONOR:", "        if False:"),
    ("a recipient is matched again", "        if int(self.matched_to.get(recipient_key, u256(0))) > 0:", "        if False:"),
    ("a spent pool still asks the model", "        if int(f.left) == 0:", "        if False:"),
    ("a fund takes any number of gifts", "        if int(f.n_gifts) >= MAX_GIFTS:", "        if False:"),
    ("a cause of any length is accepted", "        if len(text) < MIN_CAUSE or len(text) > MAX_CAUSE:", "        if False:"),

    # -- close
    ("the pool closes while gifts are open",
     "        if now <= int(f.closes_at):\n            raise", "        if False:\n            raise"),
    ("a fund closes twice",
     '        if str(f.status) != OPEN:\n            raise gl.vm.UserError(f"{ERR_EXPECTED} this fund was already closed")',
     '        if False:\n            raise gl.vm.UserError(f"{ERR_EXPECTED} this fund was already closed")'),
    ("the rest is not returned", "        self._send(f.matcher, rest)", "        pass"),
    ("what was returned is not recorded", "        f.returned = u256(rest)", "        pass"),

    # -- money
    ("the pool may be free", "        if pool < 1 or pool > MAX_AMOUNT:", "        if pool > MAX_AMOUNT:"),
    ("the held counter is not raised at open", "        self.held = u256(int(self.held) + pool)", "        pass"),
    ("a payout beyond what is held is sent", "        if amount > int(self.held):", "        if False:"),
    ("the held counter is not lowered", "        self.held = u256(int(self.held) - amount)", "        pass"),

    # -- opening
    ("the ratio is unbounded", "        if r < MIN_RATIO or r > MAX_RATIO:", "        if False:"),
    ("the cap may be zero", "        if c < 1 or c > MAX_AMOUNT:", "        if c > MAX_AMOUNT:"),
    ("the window is unbounded", "        if w < MIN_WINDOW or w > MAX_WINDOW:", "        if False:"),
    ("the window does not set the clock", "closes_at=u256(now + w)", "closes_at=u256(now + MAX_WINDOW)"),
    ("the name is unbounded", "        if len(n) < MIN_NAME or len(n) > MAX_NAME:", "        if False:"),
    ("the mission is unbounded", "        if len(m) < MIN_MISSION or len(m) > MAX_MISSION:", "        if False:"),

    # -- the prompt boundary
    ("the fence is removed", FENCE, "    return str(raw)"),
    ("the fence leaves square brackets", FENCE, '    return str(raw).replace("<", "(").replace(">", ")")'),
    ("the cause reaches the prompt unfenced", "{fence(cause)}", "{cause}"),
    ("the mission reaches the prompt unfenced", "{fence(mission)}", "{mission}"),
    ("the name reaches the prompt unfenced", "{fence(name)}", "{name}"),
    ("the prompt no longer names place and group", "including any\nplace, group or purpose the mission names", "within it"),
    ("the prompt no longer says partly is outside",
     "A cause outside it, only partly\nwithin it, or too vague to tell, does not fit.", "A cause outside it does not fit."),
    ("the prompt asks whether the cause is worthy",
     "Do not judge whether the cause\nis worthy, or whether you believe the donor; judge what the cause says.",
     "Judge whether the cause\nis worthy."),
    ("control characters are stored", '            out.append(" ")\n        else:', "            out.append(ch)\n        else:"),
]


PYTEST = [sys.executable, "-m", "pytest", "tests/", "-x", "-q", "--no-header", "-p", "no:cacheprovider"]


def copy_repo(tmp):
    dst = pathlib.Path(tmp) / "repo"
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(
        "__pycache__", ".pytest_cache", ".git", "artifacts", "*.pyc"))
    return dst


def run_one(label, find, replace):
    with tempfile.TemporaryDirectory() as tmp:
        dst = copy_repo(tmp)
        target = dst / "contracts" / TARGET
        src = target.read_text(encoding="utf-8")
        hits = src.count(find)
        if hits == 0:
            return "PATTERN NOT FOUND", None
        if hits > 1:
            return "PATTERN NOT UNIQUE", None
        target.write_text(src.replace(find, replace, 1), encoding="utf-8", newline="\n")
        subprocess.run([sys.executable, "scripts/lift.py"], cwd=dst, capture_output=True)
        proc = subprocess.run(PYTEST, cwd=dst, capture_output=True, text=True)
        if proc.returncode == 0:
            return "ESCAPED", None
        text = proc.stdout + proc.stderr
        m = re.search(r"^(?:FAILED|ERROR) (\S+?)::(\S+?)(?:\[|\s|$)", text, re.M)
        if m:
            return "caught", m.group(2).split("::")[-1]
        m = re.search(r"^E\s+(\w*(?:Error|Exception))", text, re.M)
        if m:
            return "caught", m.group(1) + " at import"
        return "caught", "unnamed failure"


def baseline_is_green():
    with tempfile.TemporaryDirectory() as tmp:
        dst = copy_repo(tmp)
        proc = subprocess.run(PYTEST, cwd=dst, capture_output=True, text=True)
        return proc.returncode == 0, (proc.stdout + proc.stderr)[-2000:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="emit the README table")
    args = ap.parse_args()

    green, tail = baseline_is_green()
    if not green:
        print("the unmutated suite is not green; every mutation would look caught:\n" + tail, file=sys.stderr)
        return 2

    rows, escaped = [], []
    for label, find, replace in MUTATIONS:
        status, test = run_one(label, find, replace)
        if status == "caught":
            rows.append((label, test))
            if not args.md:
                print("  caught   %-70s %s" % (label, test), flush=True)
        else:
            escaped.append((label, status))
            print("  %-8s %s" % (status, label), file=sys.stderr, flush=True)

    if args.md:
        print("| Mutation | Caught by |")
        print("|---|---|")
        for label, test in rows:
            print("| %s | `%s` |" % (label, test))
    else:
        print()
        print("  %d mutations, %d caught, %d escaped" % (len(MUTATIONS), len(rows), len(escaped)))
    return 1 if escaped else 0


if __name__ == "__main__":
    sys.exit(main())
