import pytest

from tests.api.helpers import EMAIL, PASSWORD, assert_error, bearer, login, register


class TestRegister:
    def test_returns_201_with_user_and_no_password(self, client):
        response = register(client, first_name="Alice", last_name="Doe")

        assert response.status_code == 201
        body = response.json()
        assert body["id"] == 1
        assert body["email"] == EMAIL
        assert body["first_name"] == "Alice"
        assert "password" not in body

    def test_duplicate_email_returns_409(self, client):
        register(client)

        assert_error(register(client), 409, "users-001", "email has already been used")

    @pytest.mark.parametrize(
        ("payload", "message"),
        [
            ({"email": "not-an-email", "password": PASSWORD}, "email"),
            ({"email": EMAIL, "password": ""}, "password"),
            ({"email": EMAIL, "password": "a" * 73}, "72 bytes"),
            ({"password": PASSWORD}, "email: Field required"),
        ],
        ids=["bad-email", "empty-password", "password-too-long", "missing-email"],
    )
    def test_invalid_body_returns_400(self, client, payload, message):
        response = client.post("/api/v1/users/register", json=payload)

        assert_error(response, 400, "middlware-003", message)


class TestLogin:
    def test_returns_user_and_tokens(self, client):
        register(client)

        response = client.post("/api/v1/users/login", json={"email": EMAIL, "password": PASSWORD})

        assert response.status_code == 200
        body = response.json()
        assert body["user"]["email"] == EMAIL
        assert "password" not in body["user"]
        assert body["token"]["access"] and body["token"]["refresh"]

    @pytest.mark.parametrize(
        ("email", "password"),
        [(EMAIL, "wrong-password"), ("ghost@example.com", PASSWORD)],
        ids=["wrong-password", "unknown-email"],
    )
    def test_bad_credentials_return_401(self, client, email, password):
        register(client)

        response = client.post("/api/v1/users/login", json={"email": email, "password": password})

        assert_error(response, 401, "users-002", "email or password is invalid")


class TestProfile:
    @pytest.mark.parametrize("method", ["GET", "POST"])
    def test_returns_current_user(self, client, auth_headers, method):
        response = client.request(method, "/api/v1/users/profile", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["email"] == EMAIL

    @pytest.mark.parametrize(
        ("headers", "message"),
        [
            ({}, "token is missing"),
            (bearer("garbage"), "token format is invalid"),
            ({"Authorization": "Basic abc"}, "token is missing"),
        ],
        ids=["no-header", "garbage-token", "wrong-scheme"],
    )
    def test_requires_valid_bearer_token(self, client, headers, message):
        response = client.get("/api/v1/users/profile", headers=headers)

        assert_error(response, 401, "middlware-002", message)

    def test_rejects_refresh_token(self, client):
        register(client)
        refresh = login(client)["refresh"]

        response = client.get("/api/v1/users/profile", headers=bearer(refresh))

        assert_error(response, 401, "middlware-002", "token type is invalid")


class TestSessionLifecycle:
    def test_login_refresh_logout(self, client, clock):
        register(client)
        first = login(client)
        clock.advance(1)

        # Refresh: new tokens work, old ones are revoked
        response = client.post("/api/v1/users/refresh-token", json={"refresh_token": first["refresh"]})
        assert response.status_code == 200
        second = response.json()["token"]
        assert client.get("/api/v1/users/profile", headers=bearer(second["access"])).status_code == 200
        assert_error(
            client.get("/api/v1/users/profile", headers=bearer(first["access"])),
            401, "middlware-002", "user token not found",
        )
        assert_error(
            client.post("/api/v1/users/refresh-token", json={"refresh_token": first["refresh"]}),
            401, "users-003", "user token not found",
        )

        # Logout: returns null, then the session is gone
        response = client.post("/api/v1/users/logout", json={"refresh_token": second["refresh"]})
        assert response.status_code == 200
        assert response.json() is None
        assert_error(
            client.get("/api/v1/users/profile", headers=bearer(second["access"])),
            401, "middlware-002", "user token not found",
        )
        assert_error(
            client.post("/api/v1/users/logout", json={"refresh_token": second["refresh"]}),
            401, "users-004", "user token not found",
        )

    def test_new_login_revokes_previous_session(self, client, clock):
        register(client)
        first = login(client)
        clock.advance(1)
        second = login(client)

        assert_error(
            client.get("/api/v1/users/profile", headers=bearer(first["access"])), 401, "middlware-002"
        )
        assert client.get("/api/v1/users/profile", headers=bearer(second["access"])).status_code == 200

    def test_refresh_rejects_access_token(self, client):
        register(client)
        access = login(client)["access"]

        response = client.post("/api/v1/users/refresh-token", json={"refresh_token": access})

        assert_error(response, 401, "users-003", "token type is invalid")

    def test_logout_requires_refresh_token_field(self, client):
        response = client.post("/api/v1/users/logout", json={})

        assert_error(response, 400, "middlware-003", "refresh_token: Field required")
