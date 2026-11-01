"""
HTTP client for the Mental Health Score Prediction FastAPI backend.

The frontend never loads the model. Every prediction goes through
POST /predict, and the connection check uses GET /.
"""

import os
from dataclasses import dataclass, field
from typing import Any

import requests

# Base URL can be changed with an environment variable, e.g.
#   $env:API_BASE_URL = "http://127.0.0.1:8001"
DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

HEALTH_TIMEOUT = 6    # seconds (backend can be slow while it reloads the model)
PREDICT_TIMEOUT = 15  # seconds


@dataclass
class ApiResult:
    """Outcome of an API call. Exactly one of `data` / `error` is set."""
    ok: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    details: list[str] = field(default_factory=list)
    status_code: int | None = None


def _url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def check_health(base_url: str) -> ApiResult:
    """Call GET / and report whether the backend is reachable."""
    try:
        resp = requests.get(_url(base_url, "/"), timeout=HEALTH_TIMEOUT)
        resp.raise_for_status()
        body = resp.json()
        if body.get("status") == "ok":
            return ApiResult(ok=True, data=body, status_code=resp.status_code)
        return ApiResult(ok=False, error="Backend replied, but not with status 'ok'.",
                         status_code=resp.status_code)
    except requests.exceptions.ConnectionError:
        return ApiResult(ok=False, error="Cannot reach the backend.")
    except requests.exceptions.Timeout:
        return ApiResult(ok=False, error="Backend did not respond in time.")
    except (requests.exceptions.HTTPError, ValueError) as exc:
        return ApiResult(ok=False, error=f"Unexpected health response: {exc}")


def _format_validation_errors(body: Any) -> list[str]:
    """Turn FastAPI's 422 `detail` list into readable lines."""
    lines = []
    detail = body.get("detail") if isinstance(body, dict) else None
    if isinstance(detail, list):
        for item in detail:
            loc = item.get("loc", [])
            field_name = str(loc[-1]).replace("_", " ") if loc else "input"
            lines.append(f"{field_name}: {item.get('msg', 'invalid value')}")
    elif detail:
        lines.append(str(detail))
    return lines


def predict(base_url: str, payload: dict[str, Any]) -> ApiResult:
    """Send the student features to POST /predict and return the score."""
    try:
        resp = requests.post(_url(base_url, "/predict"), json=payload,
                             timeout=PREDICT_TIMEOUT)
    except requests.exceptions.ConnectionError:
        return ApiResult(ok=False, error="Cannot reach the backend. Is FastAPI running?",
                         details=["Start it with: python -m uvicorn main:app --reload"])
    except requests.exceptions.Timeout:
        return ApiResult(ok=False, error=f"The backend took longer than {PREDICT_TIMEOUT}s to respond.")
    except requests.exceptions.RequestException as exc:
        return ApiResult(ok=False, error=f"Request failed: {exc}")

    # Parse JSON once; some error pages are plain text
    try:
        body = resp.json()
    except ValueError:
        body = None

    if resp.status_code == 422:
        return ApiResult(ok=False, status_code=422,
                         error="The backend rejected some input values.",
                         details=_format_validation_errors(body))
    if resp.status_code >= 500:
        return ApiResult(ok=False, status_code=resp.status_code,
                         error="The backend hit an internal error while predicting.",
                         details=["Check the uvicorn terminal for the traceback."])
    if not resp.ok:
        return ApiResult(ok=False, status_code=resp.status_code,
                         error=f"Unexpected HTTP {resp.status_code} from the backend.")

    # Validate the response shape
    score = body.get("Predicted_Mental_Health_Score") if isinstance(body, dict) else None
    if not isinstance(score, (int, float)):
        return ApiResult(ok=False, status_code=resp.status_code,
                         error="The backend response did not contain a numeric "
                               "'Predicted_Mental_Health_Score'.",
                         details=[f"Received: {str(body)[:200]}"])

    return ApiResult(ok=True, data={"score": float(score)}, status_code=resp.status_code)
