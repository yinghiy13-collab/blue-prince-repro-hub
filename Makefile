.PHONY: test opa-test verify verify-chain verify-witness verify-keys

test:
	pytest tests/ -v

opa-test:
	opa test policy/ -v

verify: verify-chain verify-witness verify-keys

verify-chain:
	python src/verify_chain.py --fixture examples/audit_chain.valid.jsonl

verify-witness:
	python src/verify_witness.py

verify-keys:
	python src/verify_keys.py

ci-local: opa-test verify test
