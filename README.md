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
- [ ] Manifest parsing and validation
  - [ ] XML manifest discovery and parsing
  - [ ] Clip boundary identification
  - [ ] Temporal sequence validation
  - [ ] Frame index tracking

- [ ] Input validation and analysis
  - [ ] Directory structure verification
  - [ ] Meta.json parsing and validation
  - [ ] Segment integrity checking
  - [ ] Missing segment detection
  - [ ] Storage requirement estimation

- [ ] Stream processing
  - [ ] Segment concatenation
  - [ ] Tile extraction and alignment
  - [ ] Overlap region handling
  - [ ] Frame assembly

- [ ] Output generation
  - [ ] Full resolution export
  - [ ] Multi-resolution output support
  - [ ] Encoder optimization

### CLI Interface
- [ ] Interactive mode with guided workflow
- [ ] Non-interactive mode with CLI flags
- [ ] Progress reporting and status updates
- [ ] Error handling and user feedback

### System Integration
- [ ] FFmpeg availability verification
- [ ] Codec support validation
- [ ] Basic system requirement checking
- [ ] Windows compatibility testing

### Optional Enhancements
- [ ] Self-test command
- [ ] Configuration persistence
- [ ] Resumable conversions
- [ ] Log file generation
- [ ] Update checking
- [ ] Multiple output format support
- [ ] Custom encoder settings
- [ ] Batch processing mode

## Installation
[Installation instructions TBD]

## Usage
[Usage instructions TBD]
