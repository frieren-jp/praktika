from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from entrypoints.run import app


def main() -> None:
    with TestClient(app) as client:
        user_response = client.post(
            "/users/",
            json={"email": "alice@example.com", "name": "Alice"},
        )
        print("POST /users/", user_response.status_code, user_response.text)
        user = user_response.json()

        response = client.get(f"/users/{user['id']}")
        print("GET /users/{id}", response.status_code, response.text)

        todo_response = client.post(
            "/todos/",
            json={"title": "Read archtool docs", "user_id": user["id"]},
        )
        print("POST /todos/", todo_response.status_code, todo_response.text)
        todo = todo_response.json()

        response = client.get(f"/todos/?user_id={user['id']}")
        print("GET /todos/?user_id=...", response.status_code, response.text)

        response = client.patch(f"/todos/{todo['id']}/complete")
        print("PATCH /todos/{id}/complete", response.status_code, response.text)


if __name__ == "__main__":
    main()
