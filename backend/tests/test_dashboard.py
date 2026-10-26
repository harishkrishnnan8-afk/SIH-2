def test_central_dashboard_aggregation(client, token_central):
    res = client.get(
        "/api/v1/dashboard/central",
        headers={"Authorization": f"Bearer {token_central}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["institutionsInScope"] >= 2
    assert "institutions" in data
    assert "totalEnrolment" in data
    assert "intakeUtilisationPct" in data


def test_reports_data_and_export(client, token_admin_ins1):
    res_data = client.get(
        "/api/v1/reports/data?key=enrolment",
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res_data.status_code == 200
    assert "headers" in res_data.json()
    assert "rows" in res_data.json()

    res_csv = client.get(
        "/api/v1/reports/export?key=enrolment",
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "DEMO ENVIRONMENT — SYNTHETIC DATA" in res_csv.text
