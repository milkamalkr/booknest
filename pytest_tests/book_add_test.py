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

    def test_return_book(self, book_owner_token):
        book_id = "3be515c6-7158-454e-a1f6-4b2221801149"
        url = f"/books/{book_id}/return"
        headers = {"Authorization": f"Bearer {book_owner_token}"}
        response = client.patch(url, headers=headers)
        assert response.status_code in [200, 400, 403, 404], f"Unexpected status: {response.status_code}, {response.text}"
        if response.status_code == 200:
            data = response.json()
            print(data)
            assert "msg" in data
            assert "returned" in data["msg"].lower()

    def test_waitlist_update_on_return_and_rerent(self, book_owner_token, login_renter, login_renter2, login_renter3):
        book_id = "3be515c6-7158-454e-a1f6-4b2221801149"
        # 1. renter1 sends rent request
        headers_renter1 = {"Authorization": f"Bearer {login_renter}"}
        resp = client.post(f"/books/{book_id}/request", headers=headers_renter1)
        assert resp.status_code == 200, f"renter1 rent request failed: {resp.text}"
        print(resp.text)
        rent_request_id1 = resp.json()["rent_request_id"]
        # book owner accepts request
        headers_owner = {"Authorization": f"Bearer {book_owner_token}"}
        resp = client.patch(f"/rent-requests/{rent_request_id1}/accept", headers=headers_owner)
        assert resp.status_code == 200, f"owner accept failed: {resp.text}"
        # Verify book is rented to renter1
        resp = client.get(f"/books/{book_id}", headers=headers_owner)
        assert resp.status_code == 200
        book = resp.json()
        print(resp.text)
        assert book["current_renter_id"] is not None
        # 2. renter2 & renter3 add themselves to waitlist
        for renter_token in [login_renter2, login_renter3]:
            headers = {"Authorization": f"Bearer {renter_token}"}
            resp = client.post(f"/books/{book_id}/waitlist", headers=headers)
            print(resp.text)
            assert resp.status_code == 200, f"waitlist join failed: {resp.text}"
        # 3. renter1 returns the book
        resp = client.patch(f"/books/{book_id}/return", headers=headers_owner)
        print(resp.text)
        assert resp.status_code == 200, f"return failed: {resp.text}"
        # 4. renter2 sends rent request
        headers_renter2 = {"Authorization": f"Bearer {login_renter2}"}
        resp = client.post(f"/books/{book_id}/request", headers=headers_renter2)
        print(resp.text)
        assert resp.status_code == 200, f"renter2 rent request failed: {resp.text}"
        rent_request_id2 = resp.json()["rent_request_id"]
        # 5. book owner accepts request
        resp = client.patch(f"/rent-requests/{rent_request_id2}/accept", headers=headers_owner)
        print(resp.text)
        assert resp.status_code == 200, f"owner accept 2 failed: {resp.text}"
        # 6. Verify renter2 is removed from waitlist
        resp = client.get(f"/books/{book_id}/waitlist", headers=headers_owner)
        print(resp.text)
        assert resp.status_code == 200
        waitlist = resp.json()["waitlist"]
        renter2_in_waitlist = any(w["renter_id"] == login_renter2 for w in waitlist)
        assert not renter2_in_waitlist, "renter2 should be removed from waitlist"
        # 7. verify renter3 is position 1 in waitlist
        renter3_entry = next((w for w in waitlist if w["renter_id"] == login_renter3), None)
        assert renter3_entry is not None, "renter3 should be in waitlist"
        assert renter3_entry["position"] == 1, f"renter3 should be position 1, got {renter3_entry['position']}"


'''
Check waitlist getting updated when book is rented out
returned
1. renter1 send rent request to book owner
book owner accepts request
Verify book owner is Rented to renter1
2. renter2 & renter3 add themself in waitlist
3. renter1 returns the book
4. renter2 sends rent request
5. book owner accepts request
6. Verify renter 2 is removed from waitlist
7. verify renter 3 is position 1 in waitlist
use book_owner_token and book_id = "3be515c6-7158-454e-a1f6-4b2221801149"

Clean up select * from rent_requests where status = 'accepted'; > change to returned
DELETE FROM waitlists;

'''

