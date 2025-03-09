# COSM C360 Tools - Input Directory Structure

This document provides detailed information about the expected format of COSM C360 camera footage directories for processing with the COSM C360 Tools.

## Required Directory Structure

The tool expects a specific hierarchical structure that reflects the camera's output organization. This structure is important for the tool to correctly identify and process the camera footage.

```
input_dir/
 ├── 0H/
 │   ├── 0M/
 │   │   ├── 0S/
 │   │   │   ├── meta.json
 │   │   │   ├── <segment .ts files>
 │   │   ├── 1S/
 │   │   │   ├── meta.json
 │   │   │   ├── <segment .ts files>
 │   │   └── ...
 │   └── 1M/
 │       ├── 0S/
 │       │   ├── meta.json
 │       │   ├── <segment .ts files>
 │       └── ...
 ├── MyManifest.xml
 └── AnotherManifest.xml (if multiple manifests exist)
```

## Structure Components

### 1. Top-Level Directory

- This is the directory you specify with `--input-dir`
- Must contain at least one `.xml` manifest file
- Contains hour-level subdirectories

### 2. Time-Based Directories

The directory structure follows a hierarchical time format:

- **Hour Directories**: Named like `0H`, `1H`, etc.
- **Minute Directories**: Named like `0M`, `1M`, etc. (inside hour directories)
- **Second Directories**: Named like `0S`, `1S`, etc. (inside minute directories)

### 3. Segment Files

Each second-level directory must contain:

- A `meta.json` file with frame timing information
- One or more `.ts` segment files containing video data

### 4. Manifest File

- XML format that describes clips and their temporal boundaries
- Located in the top-level directory
- If multiple manifest files exist, you must specify which one to use with the `--manifest` argument

## Example meta.json

Each second-level directory contains a `meta.json` file with timing information:

```json
{
  "Time": {
    "x0": 1723559335.914,
    "xi-x0": [0, 0.017, 0.033, 0.050, 0.067, 0.083, ...]
  }
}
```

- `x0`: Base timestamp for the segment
- `xi-x0`: Time offsets for each frame in the segment

## Common Issues

If the tool reports missing or invalid segments, check that:

1. The directory structure matches the expected format
2. All second-level directories contain valid `meta.json` files
3. The `.ts` segment files are present and not corrupted
4. The manifest file exists and is properly formatted

## Validating Your Input

You can validate your input directory structure by running:

```bash
python cosmos.py --self-test --input-dir /path/to/input --output-dir /path/to/output
```

This will check for common issues without processing any files.