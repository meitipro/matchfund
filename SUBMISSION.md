# Submission

One submission, under **Builder -> Intelligent Contracts**. This repository is
one standalone primitive.

---

## Before you submit, in order

1. **Measure, do not estimate.**

   ```bash
   python scripts/measure.py --write
   ```

   Runs the suite and the full mutation pass, renders the live record, and
   writes all three into README.md. It refuses to write anything if the suite
   is red, a mutation escapes, or the record is of a different contract file.

2. **Prove the address is evidence for this repository.**

   ```bash
   python scripts/verify_deployment.py <address>
   ```

   Reads the source back off chain, compares it with `contracts/match.py` and
   runs `genvm-lint check` on those bytes.

3. **Open the explorer page and check it.** It must show the deploy, the paid
   open, the four gifts with a consensus result beside each, the close, and the
   five refusals, each with its reason.

---

## On chain

The address, every transaction, every verdict and every payment are in the
[README](README.md#it-is-live-and-every-path-is-on-chain), rendered from
[`deployments/studionet.json`](deployments/studionet.json), and every
transaction with the wallet that sent it is in [EVIDENCE.md](EVIDENCE.md).

## What to say in the portal

**What it does.** Match is a matching fund that matches only the gifts its
mission covers. The matcher pays a pool in and freezes a mission, a ratio, a
cap per gift and a window. A donor gives to a recipient and says what the gift
will pay for; the gift is always passed on. Validators decide, in both option
orders and without seeing any amount or any name, whether that cause falls
within the mission, and only then does the contract add the match. What is
left goes back to the matcher when the window closes.

**Why it needs GenLayer.** Whether "a reading trolley for a children's ward in
Manchester" falls within "children's reading in Leeds" is a judgment in natural
language, and the matcher who holds the pool is the one party who cannot be
trusted to make it gift by gift. Independent validators must agree, and the
matcher cannot give, choose or close early.

**What it learned from earlier work.** The model is asked the coarsest
question that still carries the judgment, two options the contract wrote, and
is never shown money or people. Every judgment has a clock and everything an
answer cannot change is refused before the model. The uncertainty goes into
the value (an order-dependent verdict is outside), and the match is
arithmetic, not judgment.
