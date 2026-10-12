"""The demo's data, in one place.

scripts/demo.py sends exactly these values to StudioNet, and
tests/test_runbook.py replays them offline, so the demo on the explorer and the
demo the tests check cannot drift apart.

One matching fund for children's reading in Leeds: a 0.6 GEN pool, matched one
to one, at most 0.2 GEN per gift. Four donors give to four recipients. Each
gift changes one thing, so each rule of the contract shows once, on chain:

  ANN   0.1 GEN, books for a Leeds reading club: fits, matched 0.1
  BEN   0.25 GEN, a Leeds library's summer reading challenge: fits, matched
        0.2, the cap
  CAL   0.1 GEN, a floodlight for a Leeds football pitch: outside, passed on
        alone
  DEV   0.05 GEN, books for a children's ward in Manchester: outside, the
        mission names Leeds

What is left of the pool, 0.3 GEN, goes back to the matcher when the window
closes.
"""

GEN = 10 ** 18

NAME = "Leeds Reads matching fund"
MISSION = ("Children's reading in Leeds: books, libraries and reading clubs for children under twelve "
           "living in Leeds.")
RATIO = 100
CAP = 20 * GEN // 100
POOL = 60 * GEN // 100
WINDOW = 900

BOOKS = ("Forty picture books and two bean bags for the after-school reading club at a primary school "
         "in Harehills, Leeds, which meets twice a week for children aged five to eleven.")
SUMMER = ("The summer reading challenge at Leeds Central Library for primary school children: extra "
          "copies of the most borrowed books, stickers and certificates for every child who finishes.")
FLOODLIGHT = ("A new floodlight for the training pitch of an amateur adult football club in Leeds, so "
              "the team can train on winter evenings.")
WARD = ("Picture books and a reading trolley for the children's ward of a hospital in Manchester, for "
        "children staying more than a week.")
AGAIN = ("More picture books for the after-school reading club at a primary school in Harehills, "
         "Leeds, for the new reception class.")
LATE = ("Story sacks for a toddler group at a community centre in Chapeltown, Leeds, so parents can "
        "borrow books to read at home.")

# Gifts that are refused still carry a small value, as a real donor's would.
SMALL = GEN // 100

# The demo, step by step, exactly as scripts/demo.py sends it and
# tests/test_runbook.py replays it: (who, method, arguments, value, expected,
# label). Recipients are named by role and turned into addresses by the run.
# A step marked "after_close" waits until the window has closed.
STEPS = [
    ("matcher", "open", (NAME, MISSION, RATIO, CAP, WINDOW), POOL, "ok", "fund 0 opened: 0.6 GEN pool, 1:1, cap 0.2"),
    ("matcher", "give", (0, "club", BOOKS), SMALL, "refused", "the matcher gives to its own fund"),
    ("ann", "give", (0, "club", BOOKS), 10 * GEN // 100, "ok", "gift 0: Ann, 0.1 GEN to the reading club"),
    ("ben", "give", (0, "library", SUMMER), 25 * GEN // 100, "ok", "gift 1: Ben, 0.25 GEN to the library"),
    ("cal", "give", (0, "pitch", FLOODLIGHT), 10 * GEN // 100, "ok", "gift 2: Cal, 0.1 GEN to a football club"),
    ("dev", "give", (0, "ward", WARD), 5 * GEN // 100, "ok", "gift 3: Dev, 0.05 GEN to a ward in Manchester"),
    ("ann", "give", (0, "ann", BOOKS), SMALL, "refused", "Ann gives to herself"),
    ("ben", "give", (0, "club", AGAIN), SMALL, "refused", "Ben gives to the reading club, already matched"),
    ("stranger", "close", (0,), 0, "refused", "a close while gifts are open"),
    ("stranger", "give", (0, "ward", LATE), SMALL, "refused", "a gift after the window closed", "after_close"),
    ("stranger", "close", (0,), 0, "ok", "fund 0 closed: the rest back to the matcher", "after_close"),
]

# What each ok gift is expected to come back with, in order.
EXPECTED_VERDICTS = ["fits", "fits", "outside", "outside"]
