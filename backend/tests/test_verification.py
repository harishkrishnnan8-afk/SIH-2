def test_verification_simulation_label(client, token_admin_ins1):
    res = client.post(
        "/api/v1/verification/verify",
        json={"id": "123456789012"},
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["formatValid"] is True
    assert data["isSimulated"] is True
    # Explicit simulation disclaimer label required by prompt
    assert data["simulationLabel"] == "SIMULATED — NOT OFFICIAL APAAR VERIFICATION"
    assert data["providerStatus"] == "Mock provider"


def test_verification_invalid_format(client, token_admin_ins1):
    res = client.post(
        "/api/v1/verification/verify",
        json={"id": "1234"},
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["formatValid"] is False
    assert data["internalMatch"] is False
