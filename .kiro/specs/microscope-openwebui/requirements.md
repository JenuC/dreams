# Requirements Document

## Introduction

This feature creates a new `microscope_openwebui` module that mirrors the `microscope_real` module but exposes microscope control tools as an Open WebUI-compatible HTTP tool server. The server implements the Open WebUI Tools JSON specification so that Open WebUI can discover, invoke, and display results from microscope operations (snap image, move stage, get position, wait) directly within its chat interface.

## Glossary

- **Open WebUI**: An open-source, self-hosted web UI for interacting with LLMs, supporting external tool servers via a defined JSON specification.
- **Open WebUI Tool Server**: An HTTP server that exposes a `/openapi.json` (or equivalent manifest) and callable endpoints conforming to the Open WebUI external tools specification.
- **Tool Manifest**: A JSON document served at a well-known endpoint that describes available tools, their input schemas, and invocation URLs, conforming to the Open WebUI tools spec.
- **RealMicroscope**: The Python class in `microscope_api.py` that wraps pycromanager Core to control a physical microscope.
- **pycromanager**: A Python library providing remote control of Micro-Manager-based microscopes.
- **Stage Position**: A dictionary with float keys `x`, `y`, `z` representing microscope stage coordinates in micrometres (µm).
- **Snap Image**: The operation of capturing a single frame from the microscope camera and saving it as a PNG file.
- **Tool Server**: The HTTP server process that hosts the Open WebUI-compatible endpoints.
- **Endpoint**: A specific HTTP URL path that accepts requests and returns responses.
- **JSON Schema**: A vocabulary for annotating and validating JSON documents, used to describe tool input parameters.

---

## Requirements

### Requirement 1

**User Story:** As an Open WebUI user, I want to connect to a microscope tool server, so that I can discover and invoke microscope tools from within the Open WebUI chat interface.

#### Acceptance Criteria

1. WHEN the Tool Server starts, THE Tool Server SHALL serve a tool manifest at `GET /tools` that lists all available microscope tools with their names, descriptions, and JSON Schema input definitions, conforming to the Open WebUI external tools specification.
2. WHEN Open WebUI requests the tool manifest, THE Tool Server SHALL respond with HTTP 200 and a `Content-Type: application/json` header.
3. WHEN the tool manifest is requested, THE Tool Server SHALL include entries for `snap_image`, `move_stage`, `get_stage_position`, and `wait` tools.
4. WHEN the tool manifest is serialized to JSON and then deserialized, THE Tool Server SHALL produce an equivalent manifest object (round-trip consistency).

---

### Requirement 2

**User Story:** As an Open WebUI user, I want to snap an image from the microscope, so that I can view the latest captured frame in the chat interface.

#### Acceptance Criteria

1. WHEN a caller sends `POST /tools/snap_image` with a valid (possibly empty) JSON body, THE Tool Server SHALL invoke `RealMicroscope.snap_image()` and return HTTP 200 with a JSON body containing `status`, `filename`, `position`, `image_path`, `shape`, and `dtype` fields.
2. WHEN `snap_image` succeeds, THE Tool Server SHALL return a response whose `status` field equals `"ok"`.
3. IF `RealMicroscope.snap_image()` raises an exception, THEN THE Tool Server SHALL return HTTP 500 with a JSON body containing an `error` field describing the failure.

---

### Requirement 3

**User Story:** As an Open WebUI user, I want to move the microscope stage to specific coordinates, so that I can position the sample for imaging.

#### Acceptance Criteria

1. WHEN a caller sends `POST /tools/move_stage` with a JSON body containing numeric fields `x`, `y`, and `z`, THE Tool Server SHALL invoke `RealMicroscope.move_stage(x, y, z)` and return HTTP 200 with a JSON body containing the resulting stage position.
2. WHEN `move_stage` is called with valid coordinates, THE Tool Server SHALL return a response whose `x`, `y`, `z` fields match the requested coordinates.
3. IF the request body is missing any of `x`, `y`, or `z`, THEN THE Tool Server SHALL return HTTP 422 with a JSON body containing a `detail` field describing the missing fields.
4. IF `RealMicroscope.move_stage()` raises an exception, THEN THE Tool Server SHALL return HTTP 500 with a JSON body containing an `error` field.

---

### Requirement 4

**User Story:** As an Open WebUI user, I want to query the current stage position, so that I can know where the microscope is pointed.

#### Acceptance Criteria

1. WHEN a caller sends `POST /tools/get_stage_position` with a valid JSON body, THE Tool Server SHALL invoke `RealMicroscope.get_stage_position()` and return HTTP 200 with a JSON body containing `x`, `y`, and `z` fields.
2. WHEN `get_stage_position` returns a position, THE Tool Server SHALL include all three coordinate fields (`x`, `y`, `z`) in the response.
3. IF `RealMicroscope.get_stage_position()` raises an exception, THEN THE Tool Server SHALL return HTTP 500 with a JSON body containing an `error` field.

---

### Requirement 5

**User Story:** As an Open WebUI user, I want to pause microscope execution for a specified duration, so that I can introduce delays between acquisition steps.

#### Acceptance Criteria

1. WHEN a caller sends `POST /tools/wait` with a JSON body containing a numeric field `seconds`, THE Tool Server SHALL invoke `RealMicroscope.wait(seconds)` and return HTTP 200 with a JSON body containing `status` and `waited_seconds` fields.
2. WHEN `wait` completes, THE Tool Server SHALL return a response whose `waited_seconds` field equals the requested `seconds` value.
3. IF the request body is missing the `seconds` field, THEN THE Tool Server SHALL return HTTP 422 with a JSON body containing a `detail` field.
4. IF `RealMicroscope.wait()` raises an exception, THEN THE Tool Server SHALL return HTTP 500 with a JSON body containing an `error` field.

---

### Requirement 6

**User Story:** As a developer, I want the tool server to expose an OpenAPI spec, so that Open WebUI and other clients can auto-discover the API structure.

#### Acceptance Criteria

1. WHEN a caller sends `GET /openapi.json`, THE Tool Server SHALL return HTTP 200 with a valid OpenAPI 3.x JSON document describing all tool endpoints.
2. WHEN the OpenAPI document is serialized to JSON and then deserialized, THE Tool Server SHALL produce an equivalent document (round-trip consistency).
3. WHEN the OpenAPI document is generated, THE Tool Server SHALL include request body schemas and response schemas for each tool endpoint.
