# cosm-c360-tools
Generate standard MP4s from COSM output streams. Standalone utility for parsing and converting COSM C360-style .ts outputs to standard video formats.

## Overview
`cosmos` is a specialized tool for processing multi-stream video data from COSM C360 cameras. It handles the complex task of converting the camera's native output format (multiple tiled HEVC streams with metadata) into standard MP4 files suitable for review and analysis.

### Core Processing Logic
1. **Manifest Parsing & Clip Identification**
   - Parse XML manifest to identify distinct recording clips
   - Extract temporal boundaries and frame indices for each clip
   - Validate clip metadata integrity and continuity

2. **Segment Analysis & Validation**
   - Scan directory structure for .ts segments and metadata
   - Parse meta.json files to map precise temporal locations
   - Validate segment sequence integrity within clip boundaries
   - Match segments to their respective clips

3. **Stream Processing**
   - Concatenate temporally sequential segments within clip boundaries
   - Extract and align the four HEVC tile streams from each segment
   - Handle tile overlap regions with precise cropping
   - Stack tiles into complete frames

4. **Output Generation**
   - Merge processed streams into standard MP4 container
   - Generate full-resolution master files
   - Create scaled variants (4K, 1080p) as requested

## Requirements & Features
Development checklist and implementation status:

### Core Functionality
- [x] Manifest parsing and validation
  - [x] XML manifest discovery and parsing
  - [x] Clip boundary identification
  - [x] Temporal sequence validation
  - [x] Frame index tracking

- [x] Input validation and analysis
  - [x] Directory structure verification
  - [x] Meta.json parsing and validation
  - [x] Segment integrity checking
  - [x] Missing segment detection
  - [x] Storage requirement estimation

- [x] Stream processing
  - [x] Segment concatenation
  - [x] Tile extraction and alignment
  - [x] Overlap region handling
  - [x] Frame assembly

- [x] Output generation
  - [x] Full resolution export
  - [x] Multi-resolution output support
  - [x] Encoder optimization

### CLI Interface
- [ ] Interactive mode with guided workflow
- [ ] Non-interactive mode with CLI flags
- [ ] Progress reporting and status updates
- [ ] Error handling and user feedback

### System Integration
- [x] FFmpeg availability verification
- [x] Codec support validation
- [x] Basic system requirement checking
- [x] Windows compatibility testing

### Optional Enhancements
highest->lowest priority P0, P1, P2, P3
- [ ] Job name (P0) (use for logfile name, writing job parameters to a textfile in the output dir)
- [ ] Self-test command (P0)
- [ ] Configuration persistence (P2) (this seems like a good idea. maybe json config file (easier to provide lists vs. yaml) but this is optional, and this is primarily a CLI tool, flags + interactive mode provides plenty of flexibility)
- [ ] Resumable conversions (P3) (less important, this seems difficult to implement)
- [ ] Log file generation (P0)
- [ ] Update checking (P1) (how would we do this? not sure that we want to deploy to pypi, simpler to just stick with a git repo)
- [ ] Multiple output format support (P2) (less important-- MP4 is always good, just need to make res/framerate/crf configurable, allowing multiple outputs for the same clip)
- [ ] Custom encoder settings (P3)
- [ ] Batch processing mode (P3) (not sure what this really means in this context, we already try to process everything in the input directory, and generally this tool won't be deployed to clusters)

## Installation
[Installation instructions TBD]

## Usage
[Usage instructions TBD]
