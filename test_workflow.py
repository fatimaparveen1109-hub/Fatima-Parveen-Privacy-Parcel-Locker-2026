from services.passwords import hash_password, verify_password
from services.workflow_rules import ALLOWED

def test_password_hash_roundtrip():
    encoded = hash_password('Correct-Horse-Example-2026')
    assert encoded.startswith('pbkdf2_sha256$')
    assert verify_password('Correct-Horse-Example-2026', encoded)
    assert not verify_password('wrong-password', encoded)

def test_order_transition_map():
    assert 'paid' in ALLOWED['placed']
    assert 'deposited' in ALLOWED['at_hub']
    assert 'return_approved' in ALLOWED['return_requested']
