# Implementation Plan

- [x] 1. Set up project structure and copy microscope_api.py





  - Create `microscope_openwebui/` directory
  - Copy `microscope_api.py` from `microscope_real/` (or symlink if preferred)
  - Create `pyproject.toml` with dependencies: `fastapi`, `uvicorn`, `numpy`, `pillow`, `pycromanager`, `pydantic`
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1_

- [x] 2. Implement FastAPI server with tool manifest endpoint





  - Create `server.py` with FastAPI app instance
  - Instantiate `RealMicroscope()` at module level
  - Implement `GET /tools` endpoint that returns the Open WebUI tool manifest JSON
  - Define Pydantic models for `ToolParameter`, `ToolEntry`, `ToolManifest`
  - _Requirements: 1.1, 1.2, 1.3_

- [ ]* 2.1 Write property test for tool manifest completeness
  - **Property 1: Tool manifest completeness**
  - **Validates: Requirements 1.1, 1.3**

- [ ]* 2.2 Write property test for JSON round-trip consistency
  - **Property 2: JSON round-trip consistency**
  - **Validates: Requirements 1.4, 6.2**

- [x] 3. Implement snap_image tool endpoint




  - Create `POST /tools/snap_image` endpoint
  - Call `scope.snap_image()` and return the result as JSON
  - Wrap in try/except to return HTTP 500 with `{"error": "..."}` on exception
  - _Requirements: 2.1, 2.2, 2.3_

- [ ]* 3.1 Write property test for snap_image response structure
  - **Property 3: snap_image response structure**
  - **Validates: Requirements 2.1, 2.2**

- [x] 4. Implement move_stage tool endpoint




  - Define `MoveStageRequest(BaseModel)` with `x: float`, `y: float`, `z: float`
  - Create `POST /tools/move_stage` endpoint accepting `MoveStageRequest`
  - Call `scope.move_stage(x, y, z)` and return the result as JSON
  - Wrap in try/except to return HTTP 500 with `{"error": "..."}` on exception
  - FastAPI automatically returns 422 for missing fields
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ]* 4.1 Write property test for stage-returning endpoints
  - **Property 4: Stage-returning endpoints echo coordinates**
  - **Validates: Requirements 3.1, 3.2, 4.1, 4.2**

- [x] 5. Implement get_stage_position tool endpoint





  - Create `POST /tools/get_stage_position` endpoint
  - Call `scope.get_stage_position()` and return the result as JSON
  - Wrap in try/except to return HTTP 500 with `{"error": "..."}` on exception
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 6. Implement wait tool endpoint
  - Define `WaitRequest(BaseModel)` with `seconds: float`
  - Create `POST /tools/wait` endpoint accepting `WaitRequest`
  - Call `scope.wait(seconds)` and return the result as JSON
  - Wrap in try/except to return HTTP 500 with `{"error": "..."}` on exception
  - FastAPI automatically returns 422 for missing fields
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ]* 6.1 Write property test for wait response
  - **Property 5: wait response echoes duration**
  - **Validates: Requirements 5.1, 5.2**

- [x] 7. Verify OpenAPI auto-generation





  - Ensure FastAPI's built-in `GET /openapi.json` endpoint is accessible
  - Verify that all four tool endpoints appear in the OpenAPI doc with request/response schemas
  - _Requirements: 6.1, 6.2, 6.3_

- [ ]* 7.1 Write property test for OpenAPI doc coverage
  - **Property 6: OpenAPI doc covers all tool endpoints**
  - **Validates: Requirements 6.1, 6.3**

- [ ]* 8. Write unit tests for error conditions
  - Test that missing required fields return HTTP 422 with `detail` field
  - Test that exceptions from `RealMicroscope` return HTTP 500 with `error` field
  - Test that tool manifest endpoint returns HTTP 200 with `Content-Type: application/json`
  - _Requirements: 1.2, 2.3, 3.3, 3.4, 4.3, 5.3, 5.4_

- [x] 9. Add main block to run server




  - Add `if __name__ == "__main__":` block to `server.py`
  - Use `uvicorn.run(app, host="127.0.0.1", port=4202)`
  - _Requirements: 1.1_

- [x] 10. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
