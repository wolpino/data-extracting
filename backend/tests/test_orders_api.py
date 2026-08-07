"""API tests: Order CRUD happy path + edges."""

from __future__ import annotations


def _willow() -> dict:
    return {
        "first_name": "Willow",
        "last_name": "Rosenberg",
        "date_of_birth": "1981-05-01",
        "source_filename": "willow-rosenberg-chart.pdf",
    }


def test_orders_crud_roundtrip(client) -> None:
    created = client.post("/api/v1/orders", json=_willow())
    assert created.status_code == 201
    body = created.json()
    order_id = body["id"]
    assert body["first_name"] == "Willow"

    listed = client.get("/api/v1/orders")
    assert listed.status_code == 200
    assert any(row["id"] == order_id for row in listed.json())

    got = client.get(f"/api/v1/orders/{order_id}")
    assert got.status_code == 200
    assert got.json()["last_name"] == "Rosenberg"

    updated = client.put(
        f"/api/v1/orders/{order_id}",
        json={
            "first_name": "Willow",
            "last_name": "Rosenberg",
            "date_of_birth": "1981-05-01",
            "source_filename": "updated.pdf",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["source_filename"] == "updated.pdf"

    patched = client.patch(
        f"/api/v1/orders/{order_id}",
        json={"first_name": "Will"},
    )
    assert patched.status_code == 200
    assert patched.json()["first_name"] == "Will"

    deleted = client.delete(f"/api/v1/orders/{order_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/orders/{order_id}").status_code == 404


def test_get_order_404(client) -> None:
    assert client.get("/api/v1/orders/99999").status_code == 404


def test_create_rejects_blank_name(client) -> None:
    res = client.post(
        "/api/v1/orders",
        json={
            "first_name": "  ",
            "last_name": "Harris",
            "date_of_birth": "1981-03-15",
        },
    )
    assert res.status_code == 422


def test_create_rejects_pathy_filename(client) -> None:
    res = client.post(
        "/api/v1/orders",
        json={
            "first_name": "Xander",
            "last_name": "Harris",
            "date_of_birth": "1981-03-15",
            "source_filename": "../evil.pdf",
        },
    )
    assert res.status_code == 422


def test_no_buffy_seed_when_disabled(client) -> None:
    # SEED_DEMO_DATA=false in fixture — empty DB except what tests create.
    rows = client.get("/api/v1/orders").json()
    assert rows == []
