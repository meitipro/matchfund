# Match - a matching fund that matches only the gifts its mission covers

A GenLayer Intelligent Contract for a matching campaign with its rules written
in before the first gift. The matcher pays a pool in and opens a fund with a
mission, a match ratio, a cap per gift and a window. A donor gives to a
recipient and says, in words, what the gift will pay for. **The gift is always
passed on.** Validators decide one thing: **does that cause fall within the
mission, or not**. If it does, the contract adds the match from the pool; if
not, the gift goes on alone. When the window closes, what is left goes back to
the matcher. The model is never shown an amount, a donor or a recipient, and
the matcher cannot give, choose or close early.

- **Contract:** [`contracts/match.py`](contracts/match.py)
- **Tests:** `pip install pytest && pytest tests/ -q` - nothing else to install
- **Deployed:** see [It is live](#it-is-live-and-every-path-is-on-chain) below, and [`deployments/studionet.json`](deployments/studionet.json)
- **Every transaction and the wallet that sent it:** [EVIDENCE.md](EVIDENCE.md), read back from the chain
- **Run the demo yourself:** [DEPLOY.md](DEPLOY.md)
- **Verify a deployment:** `python scripts/verify_deployment.py 0x...` - compares the on-chain source with this file and lints it
- **Decisions:** [DECISIONS.md](DECISIONS.md)
- **License:** MIT

---

## It is live, and every path is on chain

<!-- measured:deployment:start -->
Deployed on studionet at [`0xcc9d9D05CB053d06d8736E312bA8D61E79534235`](https://explorer-studio.genlayer.com/address/0xcc9d9D05CB053d06d8736E312bA8D61E79534235) (deploy [`0xf9a4ddcb...`](https://explorer-studio.genlayer.com/tx/0xf9a4ddcb42260ce369fb01278a618b24d5284780a19b7f3e29bf49a4aea4661b)). Every value below was read back from the chain by `scripts/demo.py` and written to [`deployments/studionet.json`](deployments/studionet.json); none of it is typed by hand.

| Fund | Pool | Ratio | Cap per gift | Given | Matched | Returned to the matcher | Status |
|---|---|---|---|---|---|---|---|
| 0: Leeds Reads matching fund | 0.6 GEN | 100% | 0.2 GEN | 0.5 GEN | 0.3 GEN | 0.3 GEN | closed |

The mission, frozen at open: *Children's reading in Leeds: books, libraries and reading clubs for children under twelve living in Leeds.*

Every gift, and what the validators decided:

| Gift | Cause | Given | Verdict | Matched | Reason the leader gave (not consensus) |
|---|---|---|---|---|---|
| 0 | Forty picture books and two bean bags for the after-school reading club at a ... | 0.1 GEN | **fits** | 0.1 GEN | Books and bean bags support a reading club for children aged five to eleven in Harehills, Leeds, squarely matching the mission. |
| 1 | The summer reading challenge at Leeds Central Library for primary school chil... | 0.25 GEN | **fits** | 0.2 GEN | The cause supports children's reading in a Leeds library for primary school children, fitting the mission exactly. |
| 2 | A new floodlight for the training pitch of an amateur adult football club in ... | 0.1 GEN | **outside** | 0 GEN | Floodlights for adult football training have no connection to children's reading, books, libraries, or reading clubs. |
| 3 | Picture books and a reading trolley for the children's ward of a hospital in ... | 0.05 GEN | **outside** | 0 GEN | Hospital children’s reading support is in Manchester, not Leeds, so it does not meet the mission’s required location. |

Every wallet that was paid, its balance read from the chain before and again once every payment had landed, against what the contract says it sent:

| Wallet | Gained | The contract sent |
|---|---|---|
| club | 0.2 GEN | 0.2 GEN |
| library | 0.45 GEN | 0.45 GEN |
| pitch | 0.1 GEN | 0.1 GEN |
| ward | 0.05 GEN | 0.05 GEN |
| matcher | 0.3 GEN | 0.3 GEN |

Held by the contract afterwards: 0 wei.

Every transaction, in order, refusals included, with the wallet that sent it:

| Step | From | Outcome | Transaction |
|---|---|---|---|
| fund 0 opened: 0.6 GEN pool, 1:1, cap 0.2 | matcher | ok | [`0x8bae89b8...`](https://explorer-studio.genlayer.com/tx/0x8bae89b855e8b4a608e95d1eadb2d38349e8fe2692658b3e71610e2558b82814) |
| the matcher gives to its own fund | matcher | refused: the matcher cannot give to its own fund | [`0x32a3ef05...`](https://explorer-studio.genlayer.com/tx/0x32a3ef0550b17e0b73d4061c51db9a8375bc81169ed423728812f8a203e17c0a) |
| gift 0: Ann, 0.1 GEN to the reading club | ann | ok | [`0xddd3587a...`](https://explorer-studio.genlayer.com/tx/0xddd3587ab7f823de8e9da93d92317be8a90df442922e790669e62f4b11ac8ffe) |
| gift 1: Ben, 0.25 GEN to the library | ben | ok | [`0x6d833360...`](https://explorer-studio.genlayer.com/tx/0x6d83336083376965d4c8d8297f3c0c07c93948b9a97b22ea3be6ccaf4dd800be) |
| gift 2: Cal, 0.1 GEN to a football club | cal | ok | [`0x93dd1e91...`](https://explorer-studio.genlayer.com/tx/0x93dd1e91777c7dca170a37a832597dc231c998e20fcfd76c49fa75f4191eb419) |
| gift 3: Dev, 0.05 GEN to a ward in Manchester | dev | ok | [`0x550131ea...`](https://explorer-studio.genlayer.com/tx/0x550131ea47a4ea4ae83053252d5ba440c0d4d4ff8fd4eb4f3967c82797de55f1) |
| Ann gives to herself | ann | refused: a donor cannot give to itself | [`0x4eb9cadb...`](https://explorer-studio.genlayer.com/tx/0x4eb9cadb24b045f754b3172f7760badba64e4886a74156075f784584ece822e8) |
| Ben gives to the reading club, already matched | ben | refused: this fund already matched a gift to this recipient; give to it directly | [`0xf20a965b...`](https://explorer-studio.genlayer.com/tx/0xf20a965b28bf0a1cc56eef498a779a32f6b8efcedf83f9e8c159a3e6d9cedefe) |
| a close while gifts are open | stranger | refused: gifts are open until 2026-10-09T23:04:12Z | [`0x21418617...`](https://explorer-studio.genlayer.com/tx/0x214186171d154977db0b33647cb8ef3289d5205a8592f276013fc6ba6f7400d0) |
| a gift after the window closed | stranger | refused: gifts closed at 2026-10-09T23:04:12Z; a gift after the window is never judged | [`0x181ed215...`](https://explorer-studio.genlayer.com/tx/0x181ed2155d3eea2783d70fbbc092b4e10e907bc42fff0c5ae207fa93b4dcc830) |
| fund 0 closed: the rest back to the matcher | stranger | ok | [`0xbfb4d1b6...`](https://explorer-studio.genlayer.com/tx/0xbfb4d1b63991373e70e2d67f7634a9a5904070a7be268b723fa2a738630776e9) |

`tests/test_runbook.py::TestTheRecord` replays these verdicts through this repository's contract and fails unless it matches and pays exactly what the deployed one did, and unless every wallet gained on chain exactly what the contract sent it.
<!-- measured:deployment:end -->

## The problem

Matching campaigns are run by whoever holds the pool, and "does this gift
count?" is decided case by case, after the money has arrived. The matcher's
favourite causes count; a stranger's gift to a cause "outside our focus" does
not, and the donor finds out afterwards.

Asking a model "should this gift be matched?" does not fix it. It hands the
model the amount, the donor and the pool, and gets back whatever seems
generous. Match splits it: the mission, ratio and cap are frozen before any
gift; the model answers only *does what this gift pays for fall within the
mission*, without any amount or name; and how much is matched is arithmetic.

## How consensus is used

### Before any model: could any answer change the outcome?

The contract refuses for free, before a single prompt: a gift after the window
closed, a gift from the matcher, a gift to oneself or to the matcher, a
donor's third gift, a gift to a recipient this fund already matched, and a gift
when the pool is spent.

### The verdict

Otherwise the block sees the fund's name, its mission and the stated cause,
and picks one of two options the contract wrote itself:

```
<mission>
Children's reading in Leeds: books, libraries and reading clubs for children under twelve living in Leeds.
</mission>

<cause>
Picture books and a reading trolley for the children's ward of a hospital in Manchester ...
</cause>

<options>
[0] fits: what the gift will pay for falls squarely within the mission
[1] outside: it falls outside the mission, or only partly within it, or the cause is too vague to tell
</options>

answer: {"option": "1", "because": "..."}
```

The cause fits only if what it pays for falls squarely within the mission,
including any place, group or purpose the mission names. The model is told not
to judge whether the cause is worthy or whether it believes the donor.

### Both orders

The leader asks **twice**, with the options in the order fits, outside and
then reversed and renumbered, and reads each answer back through the order it
was asked in. The same option in both orders stands; anything else is
`outside`. A cause that only fits when "fits" is listed first does not clearly
fit, and a model that always answers "0" matches nothing. The uncertainty goes
into the **value** (outside), never into the comparison.

### The validator, in two layers

1. **Structural, and free.** The verdict is `fits` or `outside`. Anything else
   is refused before the validator spends a single prompt.
2. **Exact agreement.** The validator asks both orders itself and compares.

An unusable answer is retried once inside the block and then raised as
`[LLM_ERROR]`, which a validator never agrees with, so a broken model can never
spend the pool. There is no equivalence principle and no tolerance anywhere.

## What the contract decides, not the model

| The verdict | The recipient gets | The pool |
|---|---|---|
| `fits` | the gift **plus** min(gift x ratio, cap per gift, what is left) | drawn down by the match; the recipient is never matched again by this fund |
| `outside` | the gift, alone | untouched; a later gift that fits may still be matched |
| at `close()` | - | what is left goes back to the matcher |

## The state machine and its clock

```
open     gifts until closes_at
closed   what was left went back to the matcher
```

| Clock | What happens after it |
|---|---|
| `closes_at` = open + window | `give()` refuses for free, before any model; `close()` is open to anyone and returns the rest |

## Who may write

| Method | Caller | Why |
|---|---|---|
| `open(name, mission, ratio_pct, cap, window)` payable | anyone, paying the pool in | the caller becomes the matcher |
| `give(id, recipient, cause)` payable | anyone but the matcher, at most twice per fund, until the window closes | the gift is the donor's own money; the verdict only decides the match |
| `close(id)` | anyone, deliberately, after the window | it reads no model and only returns what is left; a matcher who has vanished cannot strand the pool |

`tests/test_e2e.py::TestStorageShape::test_every_gated_write_checks_the_sender`
fails if `give()` stops checking the sender, and
`test_only_a_fit_is_matched_in_code` fails if anything but `fits` can draw on
the pool.

## The API

| View | Returns |
|---|---|
| `count()` | number of funds |
| `status(id)` | `open` or `closed`: one word for another contract |
| `fund(id)` | matcher, mission, ratio, cap, pool, what is left, totals given, matched and returned, the clock |
| `gifts_of(id)` | every gift: donor, recipient, cause, amount, verdict, match, and the leader's reason |
| `matched_gift(id, recipient)` | the gift this fund matched for a recipient, or -1 |
| `held_total()` | wei still in open pools |

## Running the tests

```bash
pip install pytest
pytest tests/ -q
```

<!-- measured:tests:start -->
Measured: **131 passed**, 1 skipped. The skipped tests are the opt-in StudioNet integration tests, which run with `GENLAYER_STUDIO=1`.
<!-- measured:tests:end -->

The suite runs on [`tests/glsim.py`](tests/glsim.py), a small GenVM stand-in
that executes the real contract file, gives the leader and the validator their
own mock answers, can make a leader lie, rolls back storage and transfers on a
refusal, records every transfer, and refuses what GenVM refuses.

- [`tests/test_logic.py`](tests/test_logic.py) - the pure rules: the match arithmetic, the answer read back through its order, the fold, the agreement, the fence and the prompt, and that `lib/match_consensus.py` is the contract's own code
- [`tests/test_e2e.py`](tests/test_e2e.py) - the contract executed: the paid open, every free refusal (zero prompts), the amounts and names the model never sees, the options in both orders, order-dependence, a leader that claims a fit, `[LLM_ERROR]` never agreed with, the clock on its last second, every wei that moves, and static checks over the parsed source
- [`tests/test_runbook.py`](tests/test_runbook.py) - the demo replayed offline before a transaction is spent, and the live record replayed through this code, wallet by wallet
- [`tests/test_integration.py`](tests/test_integration.py) - opt in, `GENLAYER_STUDIO=1`: senders, real value, a TreeMap on a real address, and the free refusals on a real runtime

### The tests have teeth

[`scripts/mutate.py`](scripts/mutate.py) removes every defence one at a time
and names the test that caught each mutant. It refuses to run on a red
baseline and exits non-zero if anything escapes.

<!-- measured:mutations:start -->
Measured: **68 mutations, 68 caught, 0 escaped.**

| Mutation | Caught by |
|---|---|
| an option past the list is accepted | `test_an_unusable_answer_is_an_error_and_never_a_verdict` |
| an answer in words is read as a number | `test_an_unusable_answer_is_an_error_and_never_a_verdict` |
| the second pass is asked in the forward order | `test_the_options_are_asked_in_both_orders` |
| the reversed order is not reversed | `test_the_options_are_asked_in_both_orders` |
| a disagreement between the orders keeps the forward verdict | `test_a_model_that_always_answers_0_matches_nothing` |
| a disagreement between the orders is fits | `test_a_model_that_always_answers_0_matches_nothing` |
| an answer is not read back through its order | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| an unusable answer is not retried | `test_an_unusable_answer_is_an_error_and_never_a_verdict` |
| an unusable answer is read as outside | `test_an_unusable_answer_is_an_error_and_never_a_verdict` |
| an answer that is not an object crashes the block | `test_an_unusable_answer_is_an_error_and_never_a_verdict` |
| the validator agrees with an error | `test_an_unusable_answer_is_an_error_and_never_a_verdict` |
| the validator skips the structural check | `test_a_verdict_that_is_neither_option_is_refused_for_free` |
| the validator agrees with anything sound | `test_nodes_that_decide_differently_do_not_agree` |
| the validator agrees when its own model fails | `test_a_validator_whose_model_fails_does_not_agree` |
| agreement ignores soundness | `test_agreement_is_exact_symmetric_and_over_sound_verdicts` |
| the agreed verdict is not checked again | `test_the_agreed_verdict_is_checked_again_before_it_is_stored` |
| a gift outside the mission is matched | `test_a_gift_outside_the_mission_is_passed_on_alone` |
| the match ignores the ratio | `test_the_match_follows_the_frozen_ratio_and_cap` |
| the match ignores the cap | `test_the_match_follows_the_frozen_ratio_and_cap` |
| the match ignores what is left | `test_the_last_match_takes_only_what_is_left_and_then_the_pool_is_spent` |
| the pool is not drawn down | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| the matched total is not kept | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| the given total is not kept | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| the matched count is not kept | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| a matched recipient is not remembered | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| a donor's gifts are not counted | `test_a_donor_gives_at_most_twice` |
| the gift is kept and only the match is sent | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| the match is kept and only the gift is sent | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| the gift is not added to what is held | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| a leader's reason is stored as sent | `test_the_reason_is_not_compared_and_is_stored_sanitised` |
| a leader's reason is stored uncapped | `test_the_reason_is_not_compared_and_is_stored_sanitised` |
| gifts are not linked | `test_a_recipient_left_unmatched_may_be_matched_by_a_later_gift` |
| the matcher may give | `test_the_matcher_cannot_give` |
| a gift is taken on a closed fund | `test_a_closed_fund_takes_no_gift` |
| gifts never close | `test_gifts_close_on_the_clock_before_any_model` |
| gifts close a second early | `test_gifts_close_on_the_clock_before_any_model` |
| a gift may be empty | `test_a_gift_must_carry_value` |
| any recipient string is accepted | `test_the_recipient_must_be_an_address` |
| a donor may give to itself | `test_a_donor_cannot_give_to_itself` |
| a gift to the matcher may be matched | `test_a_gift_to_the_matcher_is_refused` |
| a donor gives without limit | `test_a_donor_gives_at_most_twice` |
| a recipient is matched again | `test_an_address_is_matched_by_value_not_by_spelling` |
| a spent pool still asks the model | `test_the_last_match_takes_only_what_is_left_and_then_the_pool_is_spent` |
| a fund takes any number of gifts | `test_a_fund_takes_at_most_forty_gifts` |
| a cause of any length is accepted | `test_the_cause_length_bounds` |
| the pool closes while gifts are open | `test_nothing_closes_while_gifts_are_open` |
| a fund closes twice | `test_a_fund_closes_once` |
| the rest is not returned | `test_close_returns_what_is_left_to_the_matcher` |
| what was returned is not recorded | `test_close_returns_what_is_left_to_the_matcher` |
| the pool may be free | `test_a_pool_must_be_paid_in` |
| the held counter is not raised at open | `test_a_fund_opens_with_its_terms_frozen_and_the_pool_held` |
| a payout beyond what is held is sent | `test_a_payout_beyond_what_is_held_is_refused` |
| the held counter is not lowered | `test_a_gift_that_fits_is_passed_on_with_its_match` |
| the ratio is unbounded | `test_the_ratio_is_bounded` |
| the cap may be zero | `test_the_cap_is_bounded` |
| the window is unbounded | `test_the_window_is_bounded` |
| the window does not set the clock | `test_a_fund_opens_with_its_terms_frozen_and_the_pool_held` |
| the name is unbounded | `test_the_name_and_mission_are_bounded` |
| the mission is unbounded | `test_the_name_and_mission_are_bounded` |
| the fence is removed | `test_caller_text_is_stored_verbatim_and_fenced_only_at_the_prompt` |
| the fence leaves square brackets | `test_caller_text_is_stored_verbatim_and_fenced_only_at_the_prompt` |
| the cause reaches the prompt unfenced | `test_caller_text_is_stored_verbatim_and_fenced_only_at_the_prompt` |
| the mission reaches the prompt unfenced | `test_caller_text_is_stored_verbatim_and_fenced_only_at_the_prompt` |
| the name reaches the prompt unfenced | `test_every_value_interpolated_into_the_prompt_is_fenced_or_ours` |
| the prompt no longer names place and group | `test_the_prompt_judges_the_cause_and_never_shows_money` |
| the prompt no longer says partly is outside | `test_the_prompt_judges_the_cause_and_never_shows_money` |
| the prompt asks whether the cause is worthy | `test_the_prompt_judges_the_cause_and_never_shows_money` |
| control characters are stored | `test_clean_text_collapses_whitespace_and_control_characters` |
<!-- measured:mutations:end -->

## Design rules applied

- **Settle what can be settled before the model:** a gift that no verdict could match is refused for free.
- **The coarsest answer that still carries the judgment:** one of two options the contract wrote.
- **No single call reveals what only the contract should see:** no amount, donor, recipient or pool balance ever enters the prompt.
- **Uncertainty in the value, never in the comparison:** an order-dependent verdict is outside.
- **Every judgment has a clock:** nothing is judged after `closes_at`.
- **Tagging untrusted text is not a fence:** `fence()` at the prompt boundary, options labelled by the contract.
- **The deployment is the submission:** `scripts/verify_deployment.py` reads the deployed source back and lints it.

## Further reading in this repository

- [DECISIONS.md](DECISIONS.md) - why each rule is the way it is, and the known limits
- [DEPLOY.md](DEPLOY.md) - the demo, step by step
- [SUBMISSION.md](SUBMISSION.md) - what to check before submitting
- [`lib/match_consensus.py`](lib/match_consensus.py) - the matching rules, generated from the contract

## Related work

- [Rubric](https://github.com/meitipro/rubric) - a prize scored against a rubric written before the first entry
- [Tender](https://github.com/meitipro/tender) - a procurement round awarded to the cheapest bid that meets frozen requirements
- [Warranty](https://github.com/meitipro/warranty) - a warranty with its payouts paid in before the sale closes
