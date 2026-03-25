"""
Tests for task 7: Verify OpenAPI auto-generation.
Requirements: 6.1, 6.2, 6.3
"""
import json
import sys
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Build the app with mocked RealMicroscope so pycromanager is never loaded.
# We do this once at module level inside the patch context so the app object
# is fully initialised (including OpenAPI schema generation) before any test
# runs.
# ---------------------------------------------------------------------------

_mock_scope = MagicMock()
_mock_scope.snap_image.return_value = {
    "status": "ok",
    "filename": "image_0001.tif",
    "position": {"x": 0.0, "y": 0.0, "z": 0.0},
    "image_path": "/tmp/scope_real_0001.png",
    "shape": [512, 512],
    "dtype": "uint16",
}
_mock_scope.move_stage.return_value = {"x": 1.0, "y": 2.0, "z": 3.0}
_mock_scope.get_stage_position.return_value = {"x": 1.0, "y": 2.0, "z": 3.0}
_mock_scope.wait.return_value = {"status": "ok", "waited_seconds": 1.0}

# Remove any previously cached server module so the patch takes effect.
for _mod in list(sys.modules.keys()):
    if _mod in ("server", "microscope_api"):
        del sys.modules[_mod]

sys.path.insert(0, os.path.dirname(__file__))

_pycromanager_mock = MagicMock()
with patch.dict("sys.modules", {"pycromanager": _pycromanager_mock}):
    with patch("microscope_api.Core", return_value=MagicMock()):
        import server as _server_module

_server_module.scope = _mock_scope

# Force OpenAPI schema generation now (while mock is in place) so it is
# cached on the app object before any test calls client.get("/openapi.json").
with patch.dict("sys.modules", {"pycromanager": _pycromanager_mock}):
    _server_module.app.openapi()

client = TestClient(_server_module.app)

EXPECTED_TOOL_PATHS = [
    "/tools/snap_image",
    "/tools/move_stage",
    "/tools/get_stage_position",
    "/tools/wait",
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_openapi_endpoint_returns_200():
    """Requirement 6.1: GET /openapi.json returns HTTP 200."""
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_openapi_content_type_is_json():
    """Requirement 6.1: Response has application/json content type."""
    response = client.get("/openapi.json")
    assert "application/json" in response.headers["content-type"]


def test_openapi_is_valid_openapi3():
    """Requirement 6.1: Document is a valid OpenAPI 3.x JSON document."""
    response = client.get("/openapi.json")
    doc = response.json()
    assert "openapi" in doc
    assert doc["openapi"].startswith("3.")
    assert "paths" in doc
    assert "info" in doc


def test_openapi_covers_all_tool_endpoints():
    """Requirement 6.3: All four tool endpoints appear in the OpenAPI doc."""
    response = client.get("/openapi.json")
    doc = response.json()
    paths = doc.get("paths", {})
    for path in EXPECTED_TOOL_PATHS:
        assert path in paths, f"Missing path in OpenAPI doc: {path}"


def test_openapi_tool_endpoints_have_post_method():
    """Requirement 6.3: Each tool endpoint has a POST operation defined."""
    response = client.get("/openapi.json")
    doc = response.json()
    paths = doc.get("paths", {})
    for path in EXPECTED_TOOL_PATHS:
        assert "post" in paths[path], f"No POST operation for {path}"


def test_openapi_move_stage_has_request_body_schema():
    """Requirement 6.3: move_stage endpoint has a request body schema."""
    response = client.get("/openapi.json")
    doc = response.json()
    post_op = doc["paths"]["/tools/move_stage"]["post"]
    assert "requestBody" in post_op, "move_stage missing requestBody"
    content = post_op["requestBody"]["content"]
    assert "application/json" in content


def test_openapi_wait_has_request_body_schema():
    """Requirement 6.3: wait endpoint has a request body schema."""
    response = client.get("/openapi.json")
    doc = response.json()
    post_op = doc["paths"]["/tools/wait"]["post"]
    assert "requestBody" in post_op, "wait missing requestBody"
    content = post_op["requestBody"]["content"]
    assert "application/json" in content


def test_openapi_endpoints_have_response_schemas():
    """Requirement 6.3: Each tool endpoint has at least one response schema."""
    response = client.get("/openapi.json")
    doc = response.json()
    paths = doc.get("paths", {})
    for path in EXPECTED_TOOL_PATHS:
        post_op = paths[path]["post"]
        assert "responses" in post_op, f"No responses defined for {path}"
        assert len(post_op["responses"]) > 0, f"Empty responses for {path}"


def test_openapi_json_round_trip():
    """Requirement 6.2: Serializing then deserializing the OpenAPI doc produces an equivalent document."""
    response = client.get("/openapi.json")
    doc = response.json()
    serialized = json.dumps(doc)
    deserialized = json.loads(serialized)
    assert deserialized == doc
