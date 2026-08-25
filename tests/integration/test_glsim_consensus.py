from pathlib import Path
import json

from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address

PROMPT = "Check one alt-text draft"


def context():
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {PROMPT: json.dumps({"fact_mask": "11", "accessibility": "READY"})}})
    return {"validators": [validator.to_dict() for validator in validators]}


def ok(receipt):
    assert tx_execution_succeeded(receipt)


def test_five_validator_accessibility_revision_case():
    publisher_account, contributor_account, reviewer_account = create_accounts(3)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "alt_text_check.py")
    deployed = factory.deploy_contract_tx(args=[contributor_account.address, reviewer_account.address, "Library entrance photo", "A daylight photograph used beside directions to the accessible library entrance.", "Describe only visible objects and layout; never infer identity, disability, health, emotion, intent, or private traits."], account=publisher_account, wait_transaction_status=TransactionStatus.FINALIZED)
    ok(deployed)
    address = extract_contract_address(deployed)
    publisher = factory.build_contract(address, account=publisher_account)
    contributor = factory.build_contract(address, account=contributor_account)
    reviewer = factory.build_contract(address, account=reviewer_account)
    ok(publisher.register_fact(args=["DOOR", "A blue double door is centered beneath a white LIBRARY sign."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(publisher.register_fact(args=["RAMP", "A concrete ramp with a metal handrail approaches from the right."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(publisher.freeze_visual_record(args=[]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(contributor.submit_first_draft(args=["Blue library double doors beneath a white sign, with a concrete ramp and metal handrail approaching from the right."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    ok(contributor.check_current_draft(args=[]).transact(transaction_context=context(), wait_transaction_status=TransactionStatus.FINALIZED))
    ok(reviewer.approve_current_draft(args=["Approved because the draft covers both material visible facts without inference."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert publisher.get_state(args=[]).call()["final_outcome"] == "APPROVED"
