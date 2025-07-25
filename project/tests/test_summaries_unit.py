import json
from datetime import datetime, timezone

import pytest
from dateutil.parser import isoparse

from app.api import crud


def test_create_summary(test_app, monkeypatch):
    test_request_payload = {"url": "https://foo.bar"}
    test_response_payload = {"id": 1, "url": "https://foo.bar/"}

    async def mock_post(payload):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post(
        "/summaries/",
        content=json.dumps(test_request_payload),
    )

    assert response.status_code == 201
    assert response.json() == test_response_payload


def test_create_summaries_invalid_json(test_app):
    response = test_app.post("/summaries/", content=json.dumps({}))
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "url"],
                "msg": "Field required",
                "input": {},
            }
        ]
    }

    response = test_app.post(
        "/summaries/", content=json.dumps({"url": "invalid://url"})
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"] == "URL scheme should be 'http' or 'https'"
    )


def test_read_summary(test_app, monkeypatch):
    test_data = {
        "id": 1,
        "url": "https://foo.bar",
        "summary": "summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    async def mock_get(id):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/summaries/1/")
    assert response.status_code == 200

    actual = response.json()

    # Normalize the datetimes to datetime objects for comparison
    expected = test_data.copy()
    expected["created_at"] = isoparse(expected["created_at"])
    actual["created_at"] = isoparse(actual["created_at"])

    assert actual == expected


def test_read_summary_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_read_all_summaries(test_app, monkeypatch):
    test_data = [
        {
            "id": 1,
            "url": "https://foo.bar",
            "summary": "summary",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "id": 2,
            "url": "https://testdrivenn.io",
            "summary": "summary",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    ]

    async def mock_get_all():
        return test_data

    monkeypatch.setattr(crud, "get_all", mock_get_all)

    response = test_app.get("/summaries/")
    assert response.status_code == 200

    actual = response.json()

    # Normalize datetime strings to datetime objects
    for a, e in zip(actual, test_data):
        a["created_at"] = isoparse(a["created_at"])
        e["created_at"] = isoparse(e["created_at"])

    assert actual == test_data


def test_remove_summary(test_app, monkeypatch):
    async def mock_get(id):
        return {
            "id": 1,
            "url": "https://foo.bar",
            "summary": "summary",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(id):
        return id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/summaries/1/")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "url": "https://foo.bar/"}


def test_remove_summary_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_update_summary(test_app, monkeypatch):
    test_request_payload = {"url": "https://foo.bar", "summary": "updated"}
    test_response_payload = {
        "id": 1,
        "url": "https://foo.bar",
        "summary": "summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    async def mock_put(id, payload):
        return test_response_payload

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put(
        "/summaries/1/",
        content=json.dumps(test_request_payload),
    )

    assert response.status_code == 200

    actual = response.json()

    # Normalize datetimes for comparison
    actual["created_at"] = isoparse(actual["created_at"])
    expected = test_response_payload.copy()
    expected["created_at"] = isoparse(expected["created_at"])

    assert actual == expected


@pytest.mark.parametrize(
    "summary_id, payload, status_code, detail",
    [
        [
            999,
            {"url": "https://foo.bar", "summary": "updated!"},
            404,
            "Summary not found",
        ],
        [
            0,
            {"url": "https://foo.bar", "summary": "updated!"},
            422,
            [
                {
                    "type": "greater_than",
                    "loc": ["path", "id"],
                    "msg": "Input should be greater than 0",
                    "input": "0",
                    "ctx": {"gt": 0},
                }
            ],
        ],
        [
            1,
            {},
            422,
            [
                {
                    "type": "missing",
                    "loc": ["body", "url"],
                    "msg": "Field required",
                    "input": {},
                },
                {
                    "type": "missing",
                    "loc": ["body", "summary"],
                    "msg": "Field required",
                    "input": {},
                },
            ],
        ],
        [
            1,
            {"url": "https://foo.bar"},
            422,
            [
                {
                    "type": "missing",
                    "loc": ["body", "summary"],
                    "msg": "Field required",
                    "input": {"url": "https://foo.bar"},
                }
            ],
        ],
    ],
)
def test_update_summary_invalid(
    test_app, monkeypatch, summary_id, payload, status_code, detail
):
    async def mock_put(id, payload):
        return None

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put(f"/summaries/{summary_id}/", content=json.dumps(payload))
    assert response.status_code == status_code
    assert response.json()["detail"] == detail


def test_update_summary_invalid_url(test_app):
    response = test_app.put(
        "/summaries/1/",
        content=json.dumps({"url": "invalid://url", "summary": "updated!"}),
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"] == "URL scheme should be 'http' or 'https'"
    )
