# Architecture

## Deployment boundary

Deploy once per image or visual asset. The same source is reusable for another asset by deploying it with new facts, contributor, reviewer, and interpretation boundary.

Constructor data establishes the deployment subject and fixed role boundary. Later writes add only the bounded records permitted by the lifecycle; a completed instance cannot be reopened.

## Participants

The deployer is the publisher, one different address is the contributor, and a third address is the reviewer. Their write permissions stay separate throughout the workflow.

Addresses are normalized before authorization comparisons. Role checks and lifecycle gates execute before semantic assessment.

## State machine

`DEFINING_FACTS → AWAITING_DRAFT → READY_FOR_ACCESSIBILITY_CHECK → REVIEWER_DECISION → REVISION_REQUESTED or COMPLETE`

The phase-like field is the primary lifecycle lock. Each write advances that path, performs a documented bounded loop, or fails with an `[EXPECTED]` user error.

## Evidence assembly

The stored asset label, usage context, interpretation rule, ordered visible-fact declarations, and current alt-text draft. Validators do not fetch or inspect an image.

Before consensus, the contract normalizes bounded text, copies required storage into plain local values, serializes a sorted JSON packet, and places it between explicit START/END delimiters. Nondeterministic callbacks do not read contract storage.

## Consensus boundary

Return a fixed-order fact mask and READY, REVISE, or UNSUPPORTED accessibility label for the current draft.

The leader callback validates exact JSON shape, field types, closed labels, masks or codes, and length bounds. A validator reruns the same semantic operation and rejects disagreement before state is committed.

## Deterministic boundary

Fact registration, versioning, designated contributor revisions, reviewer decisions, revision caps, and final publication text are deterministic.

Important invariants:

- Visible facts freeze before the first draft is accepted.
- Only the designated contributor can submit or revise alt text.
- Only the designated reviewer can approve, reject, or request a revision.
- AI cannot inspect pixels, infer private traits, approve, or publish.

No method sends value, pays rewards, escrows assets, deletes external data, calls another contract, or invokes a webhook.

## Failure model

- Invalid caller input or lifecycle use raises `[EXPECTED]` and leaves state unchanged.
- Malformed or out-of-policy model output raises `[LLM_ERROR]` and cannot be stored.
- Validator disagreement cannot commit the semantic result.
- StudioNet proof reads explicitly target `LATEST_FINAL`, avoiding stale pre-final state.
