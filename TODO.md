# TODO / DEVELOPMENT ROADMAP

## Completed Features & Functionality

- [x] **Manifest Parsing & Validation**  
  - [x] XML manifest discovery and parsing  
  - [x] Clip boundary identification  
  - [x] Temporal sequence validation  
  - [x] Frame index tracking

- [x] **Input Validation & Analysis**  
  - [x] Directory structure verification (preflight + validation)  
  - [x] Meta.json parsing and validation  
  - [x] Segment integrity checking  
  - [x] Missing segment detection  
  - [x] Storage requirement estimation

- [x] **Stream Processing**  
  - [x] Segment concatenation  
  - [x] Tile extraction and alignment  
  - [x] Overlap region handling  
  - [x] Frame assembly

- [x] **Output Generation**  
  - [x] Full resolution export  
  - [x] Multi-resolution output support  
  - [x] Encoder optimization

- [x] **System Integration**  
  - [x] FFmpeg availability verification  
  - [x] Codec support validation  
  - [x] Basic system requirement checking  
  - [x] Windows compatibility checks (path length, etc.)

- [x] **CLI Interface**  
  - [x] Non-interactive mode with CLI flags  
  - [x] Interactive mode with guided workflow (questionary)  
  - [x] Error handling and user feedback improvements

- [x] **Optional Enhancements (Partially Implemented)**  
  - [x] Self-test command (`--self-test`)  
  - [x] Update checking (Git-based)  
  - [x] Job name support integrated in `cosmos.py` (Needs final CLI integration)  
  - [x] Log file generation

*Skipping below for now:*
  - [-] Configuration persistence (basic load/save done, could be improved)  
  - [-] Multiple output format support (currently MP4 only)  
  - [-] Custom encoder settings (not yet implemented)  
  - [-] Resumable conversions (not implemented)  
  - [-] Batch processing mode (not necessary; tool already processes all detected clips)


Once these tasks are complete, the codebase should be stable, tested, and ready for initial client deployment.

---

## Outstanding Work and Codebase Review

**Code Review Observations**:

1. **Self-Test Handling**:  
   Currently, `run_self_test()` is implemented in `preflight.py` and invoked from `cosmos.py` when `--self-test` is passed. However, `cli.py` also references a `self_test()` function from `utils.py` that no longer exists in the current final implementation. This redundancy should be removed. The CLI should only handle arguments and pass them along; the actual self-test logic is now in `preflight.py` and triggered by `cosmos.py`.
   
   **Action**: Remove the call to `self_test()` in `cli.py`. The `cli.py` should not attempt to run self-tests directly. Instead, `cosmos.py` handles `--self-test`.

2. **Job Name Argument**:  
   The code discussions mentioned a `--job-name` argument and using it to produce a `job_info.txt` in the output directory. The `cosmos.py` code writes a `job_info.txt` with `job_name`, but the `cli.py` no longer includes a `--job-name` argument nor does it ask for job name in interactive mode. This is a slight inconsistency.

   **Action**: Add `--job-name` to `cli.py` and prompt for it in interactive mode so that `job_info.txt` creation aligns with user input. This is minor but would improve consistency.

3. **Preflight Checks and Validation**:  
   The code now has a fairly robust preflight check (`run_self_test()`), directory structure checks, and manifest discovery. The logic in `find_manifest()` and `preflight.py` is consistent and complements `InputValidator`. Minor duplication is acceptable since `preflight.py` aims to fail early with user-friendly messages, while `validation.py` provides detailed post-manifest parsing checks.

4. **Update Check**:  
   The update check now attempts a `git fetch` if `git` is available. If not, it prints a warning. This meets the requested requirement.

5. **Tests and Testing Framework**:  
   The code includes `pytest` tests under `tests/`. We have unit tests for `manifest`, `processing`, `validation`. Before releasing to clients, we should ensure:
   - A simple command to run tests (`pytest`) is documented.
   - Possibly add integration tests if needed.

6. **Documentation and User Instructions**:  
   The README should now fully document:
   - Installation steps (git clone + dependency installation)
   - Usage in both flag-based and interactive modes
   - System requirements (FFmpeg, Python version, etc.)
   - Directory structure expectations
   - How to run `--self-test`, `--check-updates`, etc.
   - How to run tests

**Next Steps Before Deployment**:

- Remove outdated references to `self_test()` in `cli.py`.
- Add `--job-name` argument back to `cli.py` and handle it in interactive mode.
- Complete testing instructions and possibly add a small integration test.
- Update the README and TODO as requested.

After these adjustments, the codebase should be ready for initial user testing.