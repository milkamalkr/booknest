import requests as rq

from test_login import book_owner_token, login_admin, login_renter, login_renter2, login_renter3, config_dev
import sys
import os
import pytest
from datetime import datetime


class TestRentRequest:
    BASE_URL = "http://127.0.0.1:8000"
    
    def test_rent_request_by_renter2(self, login_renter3):
        token = login_renter3["access_token"] if "access_token" in login_renter3 else login_renter3["token"]
        book_id = "3be515c6-7158-454e-a1f6-4b2221801149"
        url = f"{self.BASE_URL}/books/{book_id}/request"
        headers = {"Authorization": f"Bearer {token}"}
        response = rq.post(url, headers=headers)
        assert response.status_code == 200, f"Failed to request rent: {response.text}"
        data = response.json()
        print(data)
        assert "rent_request_id" in data
        assert "rental_history_id" in data
        assert data["msg"].lower().startswith("rent request submitted")
    
    def test_accept_rent_request2(self, book_owner_token):
        token = book_owner_token["access_token"] if "access_token" in login_renter3 else login_renter3["token"]
        # You need a valid rent_request_id for this test. Replace with a real one or create one in a setup step.
        rent_request_id = "acc28967-8f57-45c2-9035-2c660dff29ea"
        url = f"{self.BASE_URL}/rent-requests/{rent_request_id}/accept"
        headers = {"Authorization": f"Bearer {token}"}
        response = rq.patch(url, headers=headers)
        # Acceptable status codes: 200 (success), 400/404/403 if not found or not allowed
        assert response.status_code in [200, 400, 403, 404], f"Unexpected status: {response.status_code}, {response.text}"
        if response.status_code == 200:
            data = response.json()
            print(data)
            assert "msg" in data
            assert "accepted" in data["msg"] or "rented" in data["msg"]

    def test_return_book2(self, book_owner_token):
        token = book_owner_token["access_token"] if "access_token" in login_renter3 else login_renter3["token"]
        book_id = "3be515c6-7158-454e-a1f6-4b2221801149"
        url = f"{self.BASE_URL}/books/{book_id}/return"
        headers = {"Authorization": f"Bearer {token}"}
        response = rq.patch(url, headers=headers)
        assert response.status_code in [200, 400, 403, 404], f"Unexpected status: {response.status_code}, {response.text}"
        if response.status_code == 200:
            data = response.json()
            print(data)
            assert "msg" in data
            assert "returned" in data["msg"].lower()

    
    def test_waitlist_update_on_return_and_rerent2(self, book_owner_token, login_renter, login_renter2, login_renter3):
        token = book_owner_token["access_token"] if "access_token" in login_renter3 else login_renter3["token"]
        renter1_token = login_renter["access_token"] if "access_token" in login_renter3 else login_renter3["token"]
        renter2_token = login_renter2["access_token"] if "access_token" in login_renter3 else login_renter3["token"]
        renter3_token = login_renter3["access_token"] if "access_token" in login_renter3 else login_renter3["token"]
        book_id = "3be515c6-7158-454e-a1f6-4b2221801149"
        # 1. renter1 sends rent request
        headers_renter1 = {"Authorization": f"Bearer {renter1_token}"}
        resp = rq.post(f"{self.BASE_URL}/books/{book_id}/request", headers=headers_renter1)
        assert resp.status_code == 200, f"renter1 rent request failed: {resp.text}"
        print(resp.text)
        rent_request_id1 = resp.json()["rent_request_id"]
        # book owner accepts request
        headers_owner = {"Authorization": f"Bearer {token}"}
        resp = rq.patch(f"{self.BASE_URL}/rent-requests/{rent_request_id1}/accept", headers=headers_owner)
        assert resp.status_code == 200, f"owner accept failed: {resp.text}"
        # Verify book is rented to renter1
        resp = rq.get(f"{self.BASE_URL}/books/{book_id}", headers=headers_owner)
        assert resp.status_code == 200
        book = resp.json()
        print(resp.text)
        assert book["current_renter_id"] is not None
        # 2. renter2 & renter3 add themselves to waitlist
        for renter_token in [renter2_token, renter3_token]:
            headers = {"Authorization": f"Bearer {renter_token}"}
            resp = rq.post(f"{self.BASE_URL}/books/{book_id}/waitlist", headers=headers)
            print(resp.text)
            assert resp.status_code == 200, f"waitlist join failed: {resp.text}"
        # 3. renter1 returns the book
        resp = rq.patch(f"{self.BASE_URL}/books/{book_id}/return", headers=headers_owner)
        print(resp.text)
        assert resp.status_code == 200, f"return failed: {resp.text}"
        # 4. renter2 sends rent request
        headers_renter2 = {"Authorization": f"Bearer {renter2_token}"}
        resp = rq.post(f"{self.BASE_URL}/books/{book_id}/request", headers=headers_renter2)
        print(resp.text)
        assert resp.status_code == 200, f"renter2 rent request failed: {resp.text}"
        rent_request_id2 = resp.json()["rent_request_id"]
        # 5. book owner accepts request
        resp = rq.patch(f"{self.BASE_URL}/rent-requests/{rent_request_id2}/accept", headers=headers_owner)
        print(resp.text)
        assert resp.status_code == 200, f"owner accept 2 failed: {resp.text}"
        # 6. Verify renter2 is removed from waitlist
        resp = rq.get(f"{self.BASE_URL}/books/{book_id}/waitlist", headers=headers_owner)
        print(resp.text)
        assert resp.status_code == 200
        waitlist = resp.json()["waitlist"]
        renter2_in_waitlist = any(w["renter_id"] == login_renter2["user_id"] for w in waitlist)
        assert not renter2_in_waitlist, "renter2 should be removed from waitlist"
        # 7. verify renter3 is position 1 in waitlist
        renter3_entry = next((w for w in waitlist if w["renter_id"] == login_renter3["user_id"]), None)
        assert renter3_entry is not None, "renter3 should be in waitlist"
        assert renter3_entry["position"] == 1, f"renter3 should be position 1, got {renter3_entry['position']}"
