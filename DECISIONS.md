# DECISIONS

Why Match is built the way it is. Each section names the alternative that was
rejected and what it would have cost.

## The model decides fit, never money

The obvious design asks a model "should this gift be matched, and by how
much?". It does two jobs at once: reading the cause against the mission, and
deciding what the pool can afford. The second is the matcher's discretion
wearing a model's clothes, and a large gift from a familiar donor wins it.

So the model answers one question: does what this gift pays for fall within
the mission. It never sees the amount, the donor, the recipient or what is
left in the pool. How much is matched is `match_amount()`: the gift times the
frozen ratio, rounded down, capped per gift and by what is left.
`tests/test_e2e.py::TestStorageShape::test_the_block_never_touches_storage_and_never_sees_money_or_people`
fails if any of them is passed into the block, and
`test_the_model_is_never_shown_an_amount_a_donor_or_a_recipient` checks every
prompt of a real gift.

## The gift is always passed on

A donor who gives through the fund wants the recipient to get the money
whatever the fund decides. So the gift is forwarded in full in the same
transaction; the verdict only decides whether the pool adds to it. A cause
outside the mission costs the donor nothing but the match. Nothing a donor
gives is ever held by the contract past the call that brought it.

## Two options the contract wrote

The answer is `fits` or `outside`, labelled `[0]` and `[1]` by the contract
inside an `<options>` block, after every caller string has been fenced. A
cause cannot forge a third option or close its block.

## Order-dependence is outside

The options are asked in the order fits, outside and then reversed and
renumbered; each answer is read back through the order it was asked in. The
same option both ways stands; anything else is `outside`. A cause that only
fits when "fits" is listed first does not clearly fit, and the pool is not
spent on it. A model that always answers "0" matches nothing, and the tests
check it.

## Partly, vague, or the wrong place is outside

The prompt says a cause fits only if what it pays for falls squarely within
the mission, including any place, group or purpose the mission names; a cause
only partly within it, or too vague to tell, does not. The model is told not
to judge whether the cause is worthy or whether it believes the donor. The
demo's fourth gift is books for children, in Manchester, against a mission
that names Leeds.

## Every judgment has a clock

The window is frozen at `open()`. After `closes_at`, `give()` refuses before
any model is asked, and `close()` returns what is left to the matcher. A
matcher cannot keep a pool open to wait for a cause it likes, and nobody can
spend inference on a fund that can no longer match.

## Settled before the model

Everything an answer could not change is refused for free, before a prompt:
the matcher giving to its own fund, a donor giving to itself or to the
matcher, a donor's third gift, a recipient this fund already matched, a spent
pool, more than forty gifts, and anything after the window.

## One match per recipient, two gifts per donor

A recipient is keyed `"fund:recipient"` once its gift is matched, so one
cause cannot drain the pool through many donors; a recipient whose gift was
outside may still be matched by a later gift that fits. A donor is keyed
`"fund:donor"` and gives at most twice. Neither is proof against one person
using many wallets; the cap per gift and the one match per recipient bound
what that can take, and that is a known limit.

## The matcher has no say once the fund is open

The matcher cannot give, cannot be given to with a match, cannot change the
mission, ratio, cap or window, and has no method that decides anything.
`close()` is open to anyone once the window has closed, so a matcher who has
vanished cannot strand the pool, and one who is present cannot close early.

## Money

The pool is paid in at `open()` and counted in `held`. A gift is added to
`held` for the length of its own call and sent on at once with its match, so
`held` is always exactly what is left in open pools. Every payout goes through
one guarded path, after the state that justifies it is written, and a payout
larger than `held` is refused.

## Tagging untrusted text is not a fence

The name, the mission and every cause are written by someone with a stake.
`fence()` replaces `< > [ ]` at the prompt boundary, length preserved. Stored
text is kept verbatim; only the prompt is fenced.

## The reason string is leader-supplied

`because` is stored next to each gift, sanitised and capped at 140
characters, and is not part of consensus. Nothing in the contract acts on it,
and the view says so.

## Known limits

- The model judges what the donor says the gift will pay for, not what the
  recipient does with it. Match makes the stated cause public and permanent
  next to the gift; it does not audit spending.
- One person with many wallets can give many times; see above.
- On StudioNet a payment can land a little after the transaction that sent it,
  so `scripts/demo.py` reads each wallet until what the contract sent has
  arrived.
- The value of a refused payable call stays at the contract's address on
  StudioNet. `held` counts only accepted pools, so that value is never paid
  out; the demo's refused gifts carry 0.01 GEN each for that reason.

## Why the tests are built the way they are

- **Each node gets its own answers**, so a contract that assumes both nodes read the same thing is caught offline.
- **A leader can lie**, so the validator's checks are reachable, and the free layer is measured: a verdict that is neither option must cost the validator zero prompts, and the free refusals before the block must cost everyone zero prompts.
- **Every transfer is recorded**, so a gift that is kept, or a match sent to the wrong wallet, fails a test.
- **The runbook is a test.** The demo is replayed offline from `scripts/demo_data.py` before a transaction is spent, and once `deployments/studionet.json` exists the validators' real verdicts are replayed through this file, and every wallet's gain on chain is compared with what the contract sent.
- **Mutation testing.** `scripts/mutate.py` removes each defence and names the test that caught it.

## GenVM constraints this contract obeys

- the runner is pinned (`py-genlayer:1jb45aa8...`), never `test` or `latest`
- the class is named after the product, because `genvm-lint validate` does not see a class named `Contract`; the storage rows are `Fund` and `Gift`, so no dataclass shares its name
- no `int`, `list`, `dict` or `tuple` as a storage type, and no collection inside a storage dataclass; TreeMap keys are strings
- every persistent field is declared in the class body, and every stored field is read somewhere
- the block returns a flat dict of strings
- `gl.nondet` is reached only from `ask`, called only from inside the block
- payouts use `@gl.evm.contract_interface` and `emit_transfer(value=...)`
- the file is pure ASCII
- `genvm-lint` validates against GenVM `v0.3.0-rc7`, the release that ships the pinned runner; `scripts/verify_deployment.py` sets `GENVM_VERSION` accordingly
- `scripts/schema_check.py` validates the file against the live studionet runtime with `gen_getContractSchemaForCode` before a deploy is spent

## Not upgradable

There is no owner and no admin method. A fund's mission, ratio, cap and window
are frozen at `open()`, and a verdict on record stays the verdict.
