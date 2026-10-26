from backend.app.models.finding import ValidationFinding


def test_review_action_state_transition_and_audit(client, token_admin_ins1, db):
    # Create test finding
    finding = ValidationFinding(
        id="FND-TEST-001",
        institution_id="INS-001",
        category="Possible duplicate",
        severity="High",
        rule="R-DUP-01: duplicate name test",
        evidence="Test duplicate evidence",
        next_steps="Test review steps",
        status="Open",
    )
    db.add(finding)
    db.commit()

    # 1. Start review
    res1 = client.post(
        f"/api/v1/findings/{finding.id}/actions",
        json={"action": "Start review", "note": "Review in progress by admin."},
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res1.status_code == 200
    assert res1.json()["status"] == "Under review"

    # 2. Escalate
    res2 = client.post(
        f"/api/v1/findings/{finding.id}/actions",
        json={"action": "Escalate", "note": "Escalating for verification."},
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "Escalated"

    # 3. Resolve
    res3 = client.post(
        f"/api/v1/findings/{finding.id}/actions",
        json={"action": "Resolve", "note": "Discrepancy resolved with original documents."},
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res3.status_code == 200
    assert res3.json()["status"] == "Resolved"

    # Verify audit event was logged
    audit_res = client.get("/api/v1/audit", headers={"Authorization": f"Bearer {token_admin_ins1}"})
    assert audit_res.status_code == 200
    action_names = [a["action"] for a in audit_res.json()]
    assert any("Resolve" in a for a in action_names)
