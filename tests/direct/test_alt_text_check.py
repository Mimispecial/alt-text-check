from pathlib import Path
import json

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "alt_text_check.py"
SDK = "v0.2.16"
PROMPT = "Check one alt-text draft"


def address(account):
    return "0x" + account.hex()


def case(vm, direct_deploy, publisher, contributor, reviewer):
    vm.sender = publisher
    contract = direct_deploy(
        str(CONTRACT), address(contributor), address(reviewer), "Library entrance photo",
        "A daylight photograph used beside directions to the library's accessible entrance.",
        "Describe only visible objects and layout; do not infer identity, disability, health, emotion, intent, or private traits.", sdk_version=SDK,
    )
    contract.register_fact("DOOR", "A blue double door is centered beneath a white LIBRARY sign.")
    contract.register_fact("RAMP", "A concrete ramp with a metal handrail approaches from the right.")
    contract.freeze_visual_record()
    return contract


def test_designated_contributor_check_and_reviewer_approval(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = case(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender = direct_bob
    contract.submit_first_draft("Blue library double doors beneath a white sign, with a concrete ramp and metal handrail approaching from the right.")
    direct_vm.mock_llm(PROMPT, json.dumps({"fact_mask": "11", "accessibility": "READY"}))
    contract.check_current_draft()
    leader = direct_vm._captured_validators[-1][0]
    assert direct_vm.run_validator(leader_result=leader) is True
    direct_vm.sender = direct_charlie
    contract.approve_current_draft("Approved because the draft concisely covers both material visible facts without inference.")
    assert contract.get_state()["final_outcome"] == "APPROVED"
    assert contract.get_version(1)["current"] is True


def test_reviewer_requests_contributor_revision(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = case(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender = direct_bob
    contract.submit_first_draft("A blue library doorway photographed in daylight near an entrance ramp.")
    direct_vm.mock_llm(PROMPT, json.dumps({"fact_mask": "10", "accessibility": "REVISE"}))
    contract.check_current_draft()
    direct_vm.sender = direct_charlie
    contract.request_revision("Add the visible ramp approach and handrail while keeping the description factual and concise.")
    direct_vm.sender = direct_bob
    contract.submit_revision("Blue library double doors beneath a white sign, reached by a concrete ramp with a metal handrail from the right.")
    assert contract.get_state()["current_version"] == 2
    assert contract.get_state()["revision_count"] == 1


def test_role_separation_and_invalid_mask_fail_closed(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = case(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("only_contributor"):
        contract.submit_first_draft("The publisher cannot fill the separate designated contributor role in this accessibility workflow.")
    direct_vm.sender = direct_bob
    contract.submit_first_draft("Blue library double doors with a concrete ramp and handrail approaching from the right.")
    direct_vm.mock_llm(PROMPT, json.dumps({"fact_mask": "111", "accessibility": "READY"}))
    with direct_vm.expect_revert("invalid_mask"):
        contract.check_current_draft()
    assert contract.get_state()["stage"] == "READY_FOR_ACCESSIBILITY_CHECK"
