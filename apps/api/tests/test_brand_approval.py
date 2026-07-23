from fastapi.testclient import TestClient


def test_canonical_document_version_requires_approval(authenticated_client: TestClient) -> None:
    documents = authenticated_client.get(
        "/api/v1/brand/documents",
        params={"canonical_status": "canonical"},
    ).json()
    document = documents[0]
    before = authenticated_client.get(f"/api/v1/brand/documents/{document['id']}").json()
    before_version_id = before["current_version"]["id"]

    result = authenticated_client.post(
        f"/api/v1/brand/documents/{document['id']}/versions",
        json={
            "content_markdown": "# Proposed canonical update\n\nThis is intentionally pending.",
            "change_summary": "Exercise the canonical approval boundary",
        },
    )
    assert result.status_code == 201
    payload = result.json()
    assert payload["activated"] is False
    assert payload["approval_id"]

    still_current = authenticated_client.get(f"/api/v1/brand/documents/{document['id']}").json()
    assert still_current["current_version"]["id"] == before_version_id

    approved = authenticated_client.post(
        f"/api/v1/approvals/{payload['approval_id']}/decision",
        json={"decision": "approved", "notes": "Test approval"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    after = authenticated_client.get(f"/api/v1/brand/documents/{document['id']}").json()
    assert after["current_version"]["id"] == payload["version"]["id"]
