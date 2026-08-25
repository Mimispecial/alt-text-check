import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address


def ok(receipt):
    assert tx_execution_succeeded(receipt)
    assert receipt.get("status_name") == TransactionStatus.FINALIZED.value
    assert receipt.get("result_name") in (None, "AGREE", "MAJORITY_AGREE")
    assert receipt.get("tx_execution_result_name") in (None, "FINISHED_WITH_RETURN")
    return receipt


@pytest.mark.integration
def test_studionet_alt_text_draft(default_account, secondary_account, tertiary_account):
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "alt_text_check.py")
    deployed = ok(factory.deploy_contract_tx(args=[secondary_account.address, tertiary_account.address, "Library entrance photo", "A daylight photograph used beside directions to the accessible library entrance.", "Describe only visible objects and layout; never infer identity, disability, health, emotion, intent, or private traits."], account=default_account, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    publisher = factory.build_contract(address, account=default_account)
    contributor = factory.build_contract(address, account=secondary_account)
    ok(publisher.register_fact(args=["DOOR", "A blue double door is centered beneath a white LIBRARY sign."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(publisher.register_fact(args=["RAMP", "A concrete ramp with a metal handrail approaches from the right."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(publisher.freeze_visual_record(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(contributor.submit_first_draft(args=["Blue library double doors beneath a white sign, with a concrete ramp and metal handrail approaching from the right."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    intelligent = ok(contributor.check_current_draft(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    state = publisher.get_state(args=[]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["stage"] == "REVIEWER_DECISION"
    assert state["current_accessibility"] in ("READY", "REVISE", "UNSUPPORTED")
    observed = {"accessibility": state["current_accessibility"], "fact_mask": state["current_mask"]}
    print("STUDIONET_RECORD=" + json.dumps({"address": address, "deploy_tx": deployed["hash"], "intelligent_tx": intelligent["hash"], "observed": observed}, sort_keys=True))
