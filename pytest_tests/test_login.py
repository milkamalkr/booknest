import sys
import os
import pytest
from fastapi.testclient import TestClient
from fastapi import status

# Add the fastapi_template directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fastapi_template')))

from main import app

client = TestClient(app)
# Remove this line; tokens will be provided by fixtures

class config_dev:
    book_owner_id = "f2416074-ffe4-4585-b02c-1174e8f4a5b8"
    login_user_id = None
    renter_id = None

@pytest.fixture(scope="session")
def book_owner_token():
    response = client.post(
        "/auth/login",
        json={
            "email": "bookowner@booknest.com",
            "password": "secret"
        }
    )
    print("/auth/login book owner")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data or "token" in data
    data["user_id"] = 'f2416074-ffe4-4585-b02c-1174e8f4a5b8'
    return data

@pytest.fixture(scope="session")
def book_owner_token5():
    response = client.post(
        "/auth/login",
        json={
            "email": "bookowner5@booknest.com",
            "password": "secret"
        }
    )
    print("/auth/login book owner 5")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data or "token" in data
    data["user_id"] = '253b10ae-5e94-4d4c-b6bd-0b0e8a521f28'
    return data

@pytest.fixture(scope="session")
def book_owner_token6():
    response = client.post(
        "/auth/login",
        json={
            "email": "bookowner6@booknest.com",
            "password": "secret"
        }
    )
    print("/auth/login book owner 6")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data or "token" in data
    data["user_id"] = '0995dd36-c3d1-4512-b505-9b80f7aa09b5'
    return data

@pytest.fixture(scope="session")
def book_owner_token7():
    response = client.post(
        "/auth/login",
        json={
            "email": "bookowner7@booknest.com",
            "password": "secret"
        }
    )
    print("/auth/login book owner 7")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data or "token" in data
    data["user_id"] = '0995dd36-c3d1-4512-b505-9b80f7aa09b5'
    return data


@pytest.fixture(scope="session")
def login_admin():
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@booknest.com",
            "password": "secret"
        }
    )
    print("/auth/login admin")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data or "token" in data
    data["user_id"] = '55b904fc-16a7-4909-9ef1-734af969e986'
    return data

@pytest.fixture(scope="session")
def login_renter():
    response = client.post(
        "/auth/login",
        json={
            "email": "Renterer@booknest.com",
            "password": "secret"
        }
    )
    print("/auth/login renter")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data or "token" in data
    data["user_id"] = '4ab50e04-9cf0-405f-9ea2-335fa829277d'
    return data

@pytest.fixture(scope="session")
def login_renter2():
    response = client.post(
        "/auth/login",
        json={
            "email": "renter2@booknest.com",
            "password": "secret"
        }
    )
    print("/auth/login renter 2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data or "token" in data
    data["user_id"] = '12cc0dbb-7ed8-4c22-98f6-8d9aa87d45ae'
    return data

@pytest.fixture(scope="session")
def login_renter3():
    response = client.post(
        "/auth/login",
        json={
            "email": "renter3@booknest.com",
            "password": "secret"
        }
    )
    print("/auth/login renter 3")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data or "token" in data
    data["user_id"] = '73fd0c3c-0211-4734-89b0-7d856db42f15'
    return data


def login_token(book_owner_token, login_admin, login_renter):
    assert book_owner_token is not None
    assert login_admin is not None
    assert login_renter is not None
    print(book_owner_token)



