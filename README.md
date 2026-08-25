# Alt Text Check

Checks a versioned alt-text draft against publisher-frozen visible facts and an accessibility rule before a separate human reviewer approves, rejects, or requests revision.

## Why it is an Intelligent Contract

Return a fixed-order fact mask and READY, REVISE, or UNSUPPORTED accessibility label for the current draft. GenLayer validators independently replay that semantic judgment before it becomes shared state. Fact registration, versioning, designated contributor revisions, reviewer decisions, revision caps, and final publication text are deterministic.

## Reusable deployment model

Deploy once per image or visual asset. The same source is reusable for another asset by deploying it with new facts, contributor, reviewer, and interpretation boundary.

A completed deployment is an auditable record and is not reset or silently repurposed. Reuse means deploying the same reviewed source with new constructor data.

## Roles and workflow

The deployer is the publisher, one different address is the contributor, and a third address is the reviewer. Their write permissions stay separate throughout the workflow.

State path: `DEFINING_FACTS → AWAITING_DRAFT → READY_FOR_ACCESSIBILITY_CHECK → REVIEWER_DECISION → REVISION_REQUESTED or COMPLETE`

## Evidence boundary

The stored asset label, usage context, interpretation rule, ordered visible-fact declarations, and current alt-text draft. Validators do not fetch or inspect an image.

## Core invariants

- Visible facts freeze before the first draft is accepted.
- Only the designated contributor can submit or revise alt text.
- Only the designated reviewer can approve, reject, or request a revision.
- AI cannot inspect pixels, infer private traits, approve, or publish.

## Public interface

Write methods: `approve_current_draft, check_current_draft, freeze_visual_record, register_fact, reject_current_draft, request_revision, submit_first_draft, submit_revision`

View methods: `get_policy, get_state, get_version`

`get_policy` exposes the machine-readable operating boundary and confirms that this contract never custodies funds.

## Verification

Pinned GenVM runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/alt_text_check.py
genvm-lint typecheck contracts/alt_text_check.py
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5 --no-browser
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The StudioNet smoke test is opt-in and uses three disposable Mimi-only accounts protected outside the workspace. It asserts finalized successful execution and reads committed state with `LATEST_FINAL`.

## Final StudioNet proof

- Contract: https://explorer-studio.genlayer.com/address/0x2660def9A94E69b5B4698a77614703d248EB6ED0
- Studio import: https://studio.genlayer.com/?import-contract=0x2660def9A94E69b5B4698a77614703d248EB6ED0
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0x1428079d8d4afcd5ba7dee3a2347caa15f54e8fd304d3079a8c6a30131990016
- Intelligent transaction: https://explorer-studio.genlayer.com/tx/0xd2a51c3ef11018f309bcc757c4412dc1d605ce6445d8f2b9ea5101d6794b9dab
- Observed committed state: `{"accessibility":"READY","fact_mask":"11"}`
- Audited source SHA-256: `8790881f36879110289dfce1c44c8828a0553fb92e940869b9a668dd52b2d9f3`

## Limitations

- Quality depends on the publisher's visible-fact declarations being complete and accurate.
- The contract does not inspect the underlying image or prove that declared facts are visible.
- Accessibility labels are bounded drafting support and do not replace user testing.

## Repository map

- `contracts/alt_text_check.py` — Intelligent Contract source
- `tests/direct` — hardened leader/validator and lifecycle tests
- `tests/integration/test_glsim_consensus.py` — five-validator simulator flow
- `tests/integration/test_studionet_smoke.py` — live opt-in proof
- `deployments/studionet.json` — source-bound public deployment evidence
- `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md` — reviewer material

License: MIT.
