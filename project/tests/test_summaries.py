import json


def test_create_summary(test_app_with_db):
    input_url = "https://foo.bar"
    response = test_app_with_db.post(
        "/summaries/", content=json.dumps({"url": input_url})
    )
    assert response.status_code == 201
    returned_url = response.json()["url"]
    assert returned_url.rstrip("/") == input_url


def test_create_summaries_invalid_json(test_app):
    response = test_app.post("/summaries/", content=json.dumps({}))
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {},
                "loc": ["body", "url"],
                "msg": "Field required",
                "type": "missing",
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


def test_read_summary(test_app_with_db):
    input_url = "https://foo.bar"
    response = test_app_with_db.post(
        "/summaries/", content=json.dumps({"url": input_url})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get(f"/summaries/{summary_id}/")
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"].rstrip("/") == input_url
    assert response_dict["summary"]


def test_read_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.get("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"

    response = test_app_with_db.get("/summaries/0/")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"gt": 0},
                "input": "0",
                "loc": ["path", "id"],
                "msg": "Input should be greater than 0",
                "type": "greater_than",
            }
        ]
    }


def test_read_all_summaries(test_app_with_db):
    response = test_app_with_db.post(
        "/summaries/", content=json.dumps({"url": "https://foo.bar"})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.get("/summaries/")
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1


def test_remove_summary(test_app_with_db):
    input_url = "https://foo.bar"
    response = test_app_with_db.post(
        "/summaries/", content=json.dumps({"url": input_url})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.delete(f"/summaries/{summary_id}/")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == summary_id
    assert response_data["url"].rstrip("/") == input_url


def test_remove_summary_incorrect_id(test_app_with_db):
    response = test_app_with_db.delete("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_update_summary(test_app_with_db):
    input_url = "https://foo.bar"
    response = test_app_with_db.post(
        "/summaries/", content=json.dumps({"url": input_url})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.put(
        f"/summaries/{summary_id}/",
        content=json.dumps({"url": "https://foo.bar", "summary": "updated!"}),
    )
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict["id"] == summary_id
    assert response_dict["url"].rstrip("/") == input_url
    assert response_dict["summary"] == "updated!"
    assert response_dict["created_at"]


def test_update_summary_incorrect_id(test_app_with_db):
    input_url = "https://foo.bar"
    response = test_app_with_db.put(
        "/summaries/999/",
        content=json.dumps({"url": input_url, "summary": "updated!"}),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"

    response = test_app_with_db.put(
        "/summaries/0/",
        content=json.dumps({"url": "https://foo.bar/", "summary": "updated!"}),
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"gt": 0},
                "input": "0",
                "loc": ["path", "id"],
                "msg": "Input should be greater than 0",
                "type": "greater_than",
            }
        ]
    }


def test_update_summary_invalid_json(test_app_with_db):
    input_url = "https://foo.bar"
    response = test_app_with_db.post(
        "/summaries/", content=json.dumps({"url": input_url})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.put(f"/summaries/{summary_id}/", content=json.dumps({}))
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {},
                "loc": ["body", "url"],
                "msg": "Field required",
                "type": "missing",
            },
            {
                "input": {},
                "loc": ["body", "summary"],
                "msg": "Field required",
                "type": "missing",
            },
        ]
    }


def test_update_summary_invalid_keys(test_app_with_db):
    input_url = "https://foo.bar"
    response = test_app_with_db.post(
        "/summaries/", content=json.dumps({"url": input_url})
    )
    summary_id = response.json()["id"]

    response = test_app_with_db.put(
        f"/summaries/{summary_id}/", content=json.dumps({"url": input_url})
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"url": input_url},
                "loc": ["body", "summary"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }

    response = test_app_with_db.put(
        f"/summaries/{summary_id}/",
        content=json.dumps({"url": "invalid://url", "summary": "updated!"}),
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"] == "URL scheme should be 'http' or 'https'"
    )
