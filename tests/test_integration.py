"""Integration tests, run against StudioNet.

    pip install genlayer-py==0.18.0
    GENLAYER_STUDIO=1 pytest tests/test_integration.py -v

They are opt in. Without GENLAYER_STUDIO set they skip, so `pytest tests/ -q`
stays clean and offline on a reviewer's machine whatever is installed there,
and an unreachable network can never be mistaken for a broken contract.

They exercise the deterministic half on a real runtime, where the simulator is
weakest: the sender is derived from a signature rather than set by a test, the
pool is real value attached to a real transaction, a TreeMap is keyed on a real
address, and the free refusals before any model are shown to cost no
inference. The gifts themselves cost inference on every validator and are on
the record from scripts/demo.py.
"""

import os
import pathlib
import sys

import pytest

if not os.environ.get("GENLAYER_STUDIO"):
    pytest.skip("integration tests run against StudioNet and are opt in: set GENLAYER_STUDIO=1. "
                "Everything else runs offline with pytest tests/ -q", allow_module_level=True)

pytest.importorskip("genlayer_py", reason="pip install genlayer-py==0.18.0")

sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent / "scripts"))
from studio import Studio                                     # noqa: E402

CODE = (pathlib.Path(__file__).absolute().parent.parent / "contracts" / "match.py").read_text(encoding="utf-8")
NAME = "Match, integration run"
MISSION = "Children's reading in Leeds: books and reading clubs for children in Leeds."
CAUSE = "Picture books for a reading club at a primary school in Leeds."
POOL = 10 ** 15
GIFT = 10 ** 13


@pytest.fixture(scope="module")
def world():
    s = Studio()
    matcher = s.account("matcher", gen=1)
    donor = s.account("donor", gen=1)
    address = s.deploy(matcher, CODE, [])
    s.write(matcher, address, "open", [NAME, MISSION, 100, POOL, 3600], value=POOL, step="open a fund")
    return s, address, matcher, donor


def test_a_fund_opens_with_the_signer_as_matcher_and_the_pool_held(world):
    s, address, matcher, _ = world
    f = s.read(address, "fund", [0])
    assert f["status"] == "open" and f["matcher"].lower() == matcher.address.lower()
    assert f["pool"] == str(POOL) and int(s.read(address, "held_total")) == POOL


def test_the_matcher_cannot_give(world):
    s, address, matcher, donor = world
    row = s.write(matcher, address, "give", [0, donor.address, CAUSE], value=GIFT, step="the matcher gives",
                  expect="refused")
    assert "the matcher cannot give" in row["refusal"]


def test_a_donor_cannot_give_to_itself_keyed_on_its_real_address(world):
    s, address, _, donor = world
    row = s.write(donor, address, "give", [0, donor.address.lower(), CAUSE], value=GIFT,
                  step="a donor gives to itself", expect="refused")
    assert "cannot give to itself" in row["refusal"]
    assert s.read(address, "gifts_of", [0])["gifts"] == []


def test_a_close_while_gifts_are_open_is_refused(world):
    s, address, _, donor = world
    row = s.write(donor, address, "close", [0], step="close too early", expect="refused")
    assert "gifts are open until" in row["refusal"]


def test_an_unknown_fund_is_a_refusal_not_the_newest_row(world):
    s, address, _, donor = world
    row = s.write(donor, address, "close", [99], step="close a fund that does not exist", expect="refused")
    assert "no such fund" in row["refusal"]
