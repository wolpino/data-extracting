"""API tests: GET /api/v1/activity (metadata list; no self-logging)."""


def test_activity_lists_after_create(client) -> None:
    before = client.get("/api/v1/activity").json()
    assert before == []

    created = client.post(
        "/api/v1/orders",
        json={
            "first_name": "Buffy",
            "last_name": "Summers",
            "date_of_birth": "1981-01-19",
        },
    )
    assert created.status_code == 201
    order_id = created.json()["id"]

    # list_orders also writes activity; create alone is enough for this check.
    rows = client.get("/api/v1/activity").json()
    assert len(rows) >= 1
    create_row = next(r for r in rows if r["action"] == "create")
    assert create_row["entity_type"] == "order"
    assert create_row["entity_id"] == order_id
    assert create_row.get("detail") is None or "PDF" not in (create_row.get("detail") or "")
    # Listing activity must not append a new "list" row for /activity itself.
    activity_paths = [r.get("path") for r in rows]
    assert not any(p and p.endswith("/activity") for p in activity_paths)


def test_activity_limit(client) -> None:
    for i in range(3):
        client.post(
            "/api/v1/orders",
            json={
                "first_name": f"Person{i}",
                "last_name": "Test",
                "date_of_birth": "1980-01-01",
            },
        )
    rows = client.get("/api/v1/activity?limit=2").json()
    assert len(rows) == 2
