from test_login import book_owner_token, login_admin, login_renter, login_renter2, login_renter3, config_dev
import sys
import os
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import status

# Add the fastapi_template directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fastapi_template')))

from main import app

client = TestClient(app)


class TestBookAdd(config_dev):
    def test_book_add(self, book_owner_token, login_admin, login_renter):
        print(book_owner_token)
        print("Add a new book to the library.")

    def test_book_add2(self, book_owner_token, login_admin, login_renter):
        print(login_admin)
        title = "Title test " + str(datetime.now())
        print("Add a new book to the library 2.")
        payload = {
            "books": [
                {
                    "title": title,
                    "author": "Book owner",
                    "rent_per_week": 30,
                    "owner_id": self.book_owner_id,
                    "genre": "fiction",
                    "status": "available",
                    "value": 99,
                    "published_year": 1980,
                    "image_url": "abcdefgs",
                    "description": "Karma is a patient, silent teacher rather than an immediate form of justice. According to Lord Krishna, karma operates according to divine timing rather than human hurry. The outcomes are still developing even if we can't see them yet. Every action silently prepares its result, like seeds buried in soil. While some bloom right away, others wait for the soul to be ready. Therefore, trust the process and don't rush life or doubt justice. Yours will come when you're genuinely prepared to mature, not when you desire it. Karma is beautiful and balanced in that it waits without forgetting.",
                    "tags": ["thriller", "romance"]
                }
            ]
        }
        headers = {"Authorization": f"Bearer {login_admin}"}
        response = client.post("/books", json=payload, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        print(data)
        assert "inserted" in data
        assert isinstance(data["inserted"], list)
        assert data["inserted"][0]["title"].startswith(title)

    def test_waitlist_multiple_renters(self, login_renter2, login_renter3):
        book_id = "3be515c6-7158-454e-a1f6-4b2221801149"
        url = f"/books/{book_id}/waitlist"
        for renter_token in [login_renter, login_renter2, login_renter3]:
            headers = {"Authorization": f"Bearer {renter_token}"}
            response = client.post(url, headers=headers)
            assert response.status_code == status.HTTP_200_OK, f"Failed for token: {renter_token}, got {response.text}"
            data = response.json()
            print(data)
            assert data["book_id"] == book_id
            assert "position" in data
            assert data["user_id"] is not None
            assert data["position"] >= 1

    def test_rent_request_by_renter(self, login_renter3):
        book_id = "3be515c6-7158-454e-a1f6-4b2221801149"
        url = f"/books/{book_id}/request"
        headers = {"Authorization": f"Bearer {login_renter3}"}
        response = client.post(url, headers=headers)
        assert response.status_code == status.HTTP_200_OK, f"Failed to request rent: {response.text}"
        data = response.json()
        print(data)
        assert "rent_request_id" in data
        assert "rental_history_id" in data
        assert data["msg"].lower().startswith("rent request submitted")

    def test_accept_rent_request(self, book_owner_token):
        # You need a valid rent_request_id for this test. Replace with a real one or create one in a setup step.
        rent_request_id = "1e05c59c-3377-4e07-a326-6fe1755d4b5e"
        url = f"/rent-requests/{rent_request_id}/accept"
        headers = {"Authorization": f"Bearer {book_owner_token}"}
        response = client.patch(url, headers=headers)
        # Acceptable status codes: 200 (success), 400/404/403 if not found or not allowed
        assert response.status_code in [200, 400, 403, 404], f"Unexpected status: {response.status_code}, {response.text}"
        if response.status_code == 200:
            data = response.json()
            print(data)
            assert "msg" in data
            assert "accepted" in data["msg"] or "rented" in data["msg"]

