# Deploying Match

Everything here runs on StudioNet. It is gasless; the only GEN needed is the
pool and the gifts, and the payers get it from the StudioNet faucet. Nothing
needs a private key in a file.

## 1 - Check the contract

```bash
pip install -r requirements-dev.txt
pytest tests/ -q
python scripts/schema_check.py contracts/match.py
GENVM_VERSION=v0.3.0-rc7 genvm-lint check contracts/match.py
```

`schema_check.py` runs the file through the live studionet runtime with
`gen_getContractSchemaForCode`, without deploying it. On Windows, set
`PYTHONIOENCODING=utf-8` first, or the linter dies printing its own tick.

## 2 - Run the demo

```bash
python scripts/demo.py
```

It makes ten accounts in memory: the `matcher`, four donors (`ann`, `ben`,
`cal`, `dev`), a `stranger`, and four recipients that only ever receive
(`club`, `library`, `pitch`, `ward`). The matcher is funded with 2 GEN and each
donor and the stranger with 1 GEN from the faucet. It deploys
`contracts/match.py` exactly as it is in this repository. The data and the
steps are in [`scripts/demo_data.py`](scripts/demo_data.py); the same list
drives the demo and `tests/test_runbook.py`.

The fund: *Children's reading in Leeds: books, libraries and reading clubs for
children under twelve living in Leeds.* A 0.6 GEN pool, matched one to one, at
most 0.2 GEN per gift, open for fifteen minutes.

The writes, in order:

| # | From | Call | Value | Expected |
|---|---|---|---|---|
| 1 | matcher | `open(name, mission, 100, 0.2 GEN, 900)` | 0.6 GEN | ok: fund 0 |
| 2 | matcher | `give(0, club, <books>)` | 0.01 | refused: the matcher cannot give |
| 3 | ann | `give(0, club, <books for a Leeds reading club>)` | 0.1 | ok: **fits**, matched 0.1 |
| 4 | ben | `give(0, library, <a Leeds library's summer reading challenge>)` | 0.25 | ok: **fits**, matched 0.2 (the cap) |
| 5 | cal | `give(0, pitch, <a floodlight for an adult football club in Leeds>)` | 0.1 | ok: **outside**, passed on alone |
| 6 | dev | `give(0, ward, <books for a children's ward in Manchester>)` | 0.05 | ok: **outside**, passed on alone |
| 7 | ann | `give(0, ann, ...)` | 0.01 | refused: a donor cannot give to itself |
| 8 | ben | `give(0, club, ...)` | 0.01 | refused: the club was already matched |
| 9 | stranger | `close(0)` | - | refused: gifts are open |
| 10 | stranger | `give(0, ward, ...)` after the window | 0.01 | refused: gifts closed |
| 11 | stranger | `close(0)` after the window | - | ok: 0.3 GEN back to the matcher |

The script waits for the window to close before step 10, and stops at the
first step that does not do what the table says, because the demo claims
whatever it records. The verdicts are whatever the validators agree on; the
live ones are in the README.

It writes [`deployments/studionet.json`](deployments/studionet.json): every
transaction hash, its sender and status, each refusal's sentence, the fund and
every gift as the chain holds them, what the contract sent each wallet, and
each wallet's balance before and after. Then:

```bash
pytest tests/test_runbook.py -v
```

`TestTheRecord` replays the verdicts the validators agreed on through this
repository's contract and fails unless it matches and pays exactly what the
deployed one did, and unless every wallet gained on chain exactly what the
contract sent it.

## 3 - Reads - free, no transaction

```bash
genlayer network set studionet
genlayer call <address> count
genlayer call <address> fund --args 0
genlayer call <address> gifts_of --args 0
genlayer call <address> held_total
```

## 4 - Before the portal

```bash
python scripts/verify_deployment.py <address>
python scripts/measure.py --write
```

The first reads the deployed source back off chain, compares it with
`contracts/match.py` and lints the deployed bytes. The second runs the suite
and the mutation pass and writes the measured numbers and the live record into
README.md. Neither writes anything unless every check passes.
