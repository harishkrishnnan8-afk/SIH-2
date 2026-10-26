import io


def test_upload_valid_csv(client, token_admin_ins1):
    csv_content = (
        "student_name,apaar_id,programme_code,academic_year,admission_category,admission_status,date_of_birth\n"
        "Rohan Gupta,111122223333,BT-CSE,2026–27,General,Admitted,2006-03-15\n"
    )
    files = {"file": ("students.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    res = client.post(
        "/api/v1/uploads",
        files=files,
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["accepted"] == 1
    assert data["rejected"] == 0
    assert data["persisted"] is True


def test_upload_invalid_rows_returns_row_level_errors(client, token_admin_ins1):
    # Row 2: invalid 5-digit APAAR
    # Row 3: missing student name
    csv_content = (
        "student_name,apaar_id,programme_code,academic_year,admission_category,admission_status,date_of_birth\n"
        "Bad Apaar Student,12345,BT-CSE,2026–27,General,Admitted,2006-03-15\n"
        ",111122224444,BT-CSE,2026–27,General,Admitted,2006-03-15\n"
    )
    files = {"file": ("invalid_batch.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    res = client.post(
        "/api/v1/uploads",
        files=files,
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["rejected"] == 2
    assert len(data["errors"]) >= 2
    fields = [e["field"] for e in data["errors"]]
    assert "apaar_id" in fields
    assert "student_name" in fields


def test_download_row_errors_csv(client, token_admin_ins1):
    csv_content = (
        "student_name,apaar_id,programme_code,academic_year,admission_category,admission_status,date_of_birth\n"
        "Bad Student,999,BT-CSE,2026–27,General,Admitted,2006-03-15\n"
    )
    files = {"file": ("error_batch.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    upload_res = client.post(
        "/api/v1/uploads",
        files=files,
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    batch_id = upload_res.json()["batch_id"]

    # Download error report
    res = client.get(
        f"/api/v1/uploads/{batch_id}/errors.csv",
        headers={"Authorization": f"Bearer {token_admin_ins1}"},
    )
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "row,field,value,rule" in res.text
