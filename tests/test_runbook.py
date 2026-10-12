"""
The demo, replayed offline.

scripts/demo.py puts the demo on StudioNet from scripts/demo_data.py (STEPS).
This file replays the same steps against the real contract in the simulator,
so a demo that could not succeed is caught before a single transaction is
spent on it.

When deployments/studionet.json exists, the replay goes further: it feeds the
simulator the verdicts the validators actually agreed on, and checks that the
contract in this repository matches and pays exactly what the deployed one
did, and refuses exactly where it refused.

    pytest tests/test_runbook.py -v
"""

import collections
import hashlib
import importlib.util
import json
import pathlib

import pytest

import glsim as S

CONTRACT_PATH = "contracts/match.py"
M = S.load_contract(CONTRACT_PATH)
RECORD = pathlib.Path("deployments/studionet.json")

_spec = importlib.util.spec_from_file_location("demo_data", "scripts/demo_data.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

WHO = {"matcher": "0x" + "a1" * 20, "ann": "0x" + "b2" * 20, "ben": "0x" + "c3" * 20, "cal": "0x" + "d4" * 20,
       "dev": "0x" + "e5" * 20, "stranger": "0x" + "f6" * 20, "club": "0x" + "01" * 20,
       "library": "0x" + "02" * 20, "pitch": "0x" + "03" * 20, "ward": "0x" + "04" * 20}
T0 = 1_790_000_000


def args_for(method, spec, who):
    if method == "give":
        fid, to, cause = spec
        return [fid, who[to], cause]
    return list(spec)


def replay(verdicts, who=WHO):
    """Run STEPS. `verdicts` are what the ok gifts come back with, in order."""
    S.reset_transfers()
    c = S.deploy(CONTRACT_PATH)
    queue = list(verdicts)
    outcomes = []
    clock = T0
    for step in D.STEPS:
        actor, method, spec, value, expect, label = step[:6]
        clock += 30
        if "after_close" in step[6:]:
            clock = max(clock, M.seconds(c.fund(0)["closes_at"]) + 20)
        S.set_time(M.iso(clock))
        S.set_mocks()
        if method == "give" and expect == "ok":
            want = queue.pop(0)
            S.set_mocks(leader_prompts={"[0] fits:": {"option": str(M.FORWARD.index(want)), "because": "replayed"},
                                        "[0] outside:": {"option": str(M.REVERSED.index(want)), "because": "replayed"}})
        S.set_sender(who[actor])
        try:
            S.call(c, method, *args_for(method, spec, who), value=value)
            outcomes.append(("ok", ""))
        except S.UserError as e:
            outcomes.append(("refused", e.message))
    return c, outcomes


def received():
    out = collections.Counter()
    for to, v in S.transfers():
        out[str(to).lower()] += v
    return out


class TestDemoData:
    def test_every_value_the_demo_sends_passes_the_bounds(self):
        assert M.MIN_NAME <= len(D.NAME) <= M.MAX_NAME and M.MIN_MISSION <= len(D.MISSION) <= M.MAX_MISSION
        assert M.MIN_RATIO <= D.RATIO <= M.MAX_RATIO and M.MIN_WINDOW <= D.WINDOW <= M.MAX_WINDOW
        for text in (D.BOOKS, D.SUMMER, D.FLOODLIGHT, D.WARD, D.AGAIN, D.LATE):
            assert M.MIN_CAUSE <= len(M.clean_text(text)) <= M.MAX_CAUSE

    def test_each_gift_changes_one_thing(self):
        assert "Leeds" in D.BOOKS and "Leeds" in D.SUMMER and "Leeds" in D.FLOODLIGHT
        assert "Leeds" not in D.WARD and "Manchester" in D.WARD          # Dev is outside on place
        assert "adult" in D.FLOODLIGHT and "read" not in D.FLOODLIGHT    # Cal is outside on purpose
        gifts = [s for s in D.STEPS if s[1] == "give" and s[4] == "ok"]
        assert gifts[1][3] * D.RATIO // 100 > D.CAP                      # Ben's match is capped

    def test_the_window_outlasts_the_steps_meant_to_land_inside_it(self):
        """Four gifts (each a judging, up to 90 s) and five other transactions
        (up to 60 s) are meant to land before the window closes."""
        assert D.WINDOW >= 4 * 90 + 5 * 60 + 120


class TestReplay:
    def test_the_demo_succeeds_and_refuses_exactly_where_it_says(self):
        _, outcomes = replay(D.EXPECTED_VERDICTS)
        assert [o for o, _ in outcomes] == [s[4] for s in D.STEPS]

    def test_the_refusals_say_why(self):
        _, outcomes = replay(D.EXPECTED_VERDICTS)
        msgs = [m for o, m in outcomes if o == "refused"]
        wants = ["the matcher cannot give", "cannot give to itself", "already matched a gift to this recipient",
                 "gifts are open until", "gifts closed at"]
        assert len(msgs) == len(wants)
        for msg, want in zip(msgs, wants):
            assert want in msg, (want, msg)

    def test_the_expected_verdicts_pay_what_the_readme_says(self):
        c, _ = replay(D.EXPECTED_VERDICTS)
        g = c.gifts_of(0)["gifts"]
        assert [(x["verdict"], int(x["matched"])) for x in g] == [
            ("fits", D.GEN // 10), ("fits", D.CAP), ("outside", 0), ("outside", 0)]
        got = received()
        assert got[WHO["club"].lower()] == 2 * D.GEN // 10
        assert got[WHO["library"].lower()] == 25 * D.GEN // 100 + D.CAP
        assert got[WHO["pitch"].lower()] == D.GEN // 10 and got[WHO["ward"].lower()] == 5 * D.GEN // 100
        assert got[WHO["matcher"].lower()] == D.POOL - D.GEN // 10 - D.CAP
        f = c.fund(0)
        assert (f["status"], f["returned"], f["left"]) == ("closed", str(D.POOL - D.GEN // 10 - D.CAP), "0")
        assert c.held_total() == 0


@pytest.mark.skipif(not RECORD.exists(), reason="no deployment recorded yet: python scripts/demo.py")
class TestTheRecord:
    """The live run, checked against this repository."""

    def _record(self):
        return json.loads(RECORD.read_text(encoding="utf-8"))

    def test_the_record_is_of_this_source(self):
        here = hashlib.sha256(pathlib.Path(CONTRACT_PATH).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert self._record()["source_sha256"] == here, "the deployed contract is not this file; redeploy"

    def test_every_step_on_chain_did_what_the_demo_expected(self):
        steps = [s for s in self._record()["steps"] if s["step"] != "deploy"]
        assert [("ok" if s["ok"] else "refused") for s in steps] == [s[4] for s in D.STEPS]

    def test_this_contract_pays_what_the_deployed_one_paid(self):
        rec = self._record()
        who = {k: v for k, v in rec["accounts"].items()}
        c, outcomes = replay([g["verdict"] for g in rec["funds"][0]["gifts"]], who=who)
        assert [o for o, _ in outcomes] == [s[4] for s in D.STEPS]
        assert [(g["verdict"], g["matched"]) for g in c.gifts_of(0)["gifts"]] == \
            [(g["verdict"], g["matched"]) for g in rec["funds"][0]["gifts"]]
        mine, theirs = c.fund(0), rec["funds"][0]["fund"]
        for field in ("status", "matched_total", "given_total", "returned", "left"):
            assert str(mine[field]) == str(theirs[field]), field

    def test_every_wallet_received_on_chain_exactly_what_the_contract_sent(self):
        rec = self._record()
        who = {k: v for k, v in rec["accounts"].items()}
        replay([g["verdict"] for g in rec["funds"][0]["gifts"]], who=who)
        got = received()
        b = rec["balances"]
        for name in ("club", "library", "pitch", "ward", "matcher"):
            gained = int(b[f"{name}_after"]) - int(b[f"{name}_before"])
            assert gained == got[who[name].lower()], name
        assert rec["held_after"] == "0"
