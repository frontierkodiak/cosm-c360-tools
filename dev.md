# input directory structure/example metadata
a structured directory of .ts files (for data produced by a rather exotic ultra-high resolution camera, which saves four separate streams per file, and in approximately 1/10second chunks. 

You can get a good sense of the directory structure of the input data, and the two types of metadata available (a single clip manifest .xml, and meta.json files for each second) here:
```
Directory tree, stemming from root "/home/caleb/ladybird_failed_copy":
├── 0H (321 lines)
│   ├── 0M (180)
│   │   ├── 0S (3)
│   │   │   └── meta.json (3)
│   │   ├── 10S (3)
│   │   │   └── meta.json (3)
│   │   ├── 11S (3)
│   │   │   └── meta.json (3)
│   │   ├── 12S (3)
│   │   │   └── meta.json (3)
│   │   ├── 13S (3)
│   │   │   └── meta.json (3)
│   │   ├── 14S (3)
│   │   │   └── meta.json (3)
│   │   ├── 15S (3)
│   │   │   └── meta.json (3)
│   │   ├── 16S (3)
│   │   │   └── meta.json (3)
│   │   ├── 17S (3)
│   │   │   └── meta.json (3)
│   │   ├── 18S (3)
│   │   │   └── meta.json (3)
│   │   ├── 19S (3)
│   │   │   └── meta.json (3)
│   │   ├── 1S (3)
│   │   │   └── meta.json (3)
│   │   ├── 20S (3)
│   │   │   └── meta.json (3)
│   │   ├── 21S (3)
│   │   │   └── meta.json (3)
│   │   ├── 22S (3)
│   │   │   └── meta.json (3)
│   │   ├── 23S (3)
│   │   │   └── meta.json (3)
│   │   ├── 24S (3)
│   │   │   └── meta.json (3)
│   │   ├── 25S (3)
│   │   │   └── meta.json (3)
│   │   ├── 26S (3)
│   │   │   └── meta.json (3)
│   │   ├── 27S (3)
│   │   │   └── meta.json (3)
│   │   ├── 28S (3)
│   │   │   └── meta.json (3)
│   │   ├── 29S (3)
│   │   │   └── meta.json (3)
│   │   ├── 2S (3)
│   │   │   └── meta.json (3)
│   │   ├── 30S (3)
│   │   │   └── meta.json (3)
│   │   ├── 31S (3)
│   │   │   └── meta.json (3)
│   │   ├── 32S (3)
│   │   │   └── meta.json (3)
│   │   ├── 33S (3)
│   │   │   └── meta.json (3)
│   │   ├── 34S (3)
│   │   │   └── meta.json (3)
│   │   ├── 35S (3)
│   │   │   └── meta.json (3)
│   │   ├── 36S (3)
│   │   │   └── meta.json (3)
│   │   ├── 37S (3)
│   │   │   └── meta.json (3)
│   │   ├── 38S (3)
│   │   │   └── meta.json (3)
│   │   ├── 39S (3)
│   │   │   └── meta.json (3)
│   │   ├── 3S (3)
│   │   │   └── meta.json (3)
│   │   ├── 40S (3)
│   │   │   └── meta.json (3)
│   │   ├── 41S (3)
│   │   │   └── meta.json (3)
│   │   ├── 42S (3)
│   │   │   └── meta.json (3)
│   │   ├── 43S (3)
│   │   │   └── meta.json (3)
│   │   ├── 44S (3)
│   │   │   └── meta.json (3)
│   │   ├── 45S (3)
│   │   │   └── meta.json (3)
│   │   ├── 46S (3)
│   │   │   └── meta.json (3)
│   │   ├── 47S (3)
│   │   │   └── meta.json (3)
│   │   ├── 48S (3)
│   │   │   └── meta.json (3)
│   │   ├── 49S (3)
│   │   │   └── meta.json (3)
│   │   ├── 4S (3)
│   │   │   └── meta.json (3)
│   │   ├── 50S (3)
│   │   │   └── meta.json (3)
│   │   ├── 51S (3)
│   │   │   └── meta.json (3)
│   │   ├── 52S (3)
│   │   │   └── meta.json (3)
│   │   ├── 53S (3)
│   │   │   └── meta.json (3)
│   │   ├── 54S (3)
│   │   │   └── meta.json (3)
│   │   ├── 55S (3)
│   │   │   └── meta.json (3)
│   │   ├── 56S (3)
│   │   │   └── meta.json (3)
│   │   ├── 57S (3)
│   │   │   └── meta.json (3)
│   │   ├── 58S (3)
│   │   │   └── meta.json (3)
│   │   ├── 59S (3)
│   │   │   └── meta.json (3)
│   │   ├── 5S (3)
│   │   │   └── meta.json (3)
│   │   ├── 6S (3)
│   │   │   └── meta.json (3)
│   │   ├── 7S (3)
│   │   │   └── meta.json (3)
│   │   ├── 8S (3)
│   │   │   └── meta.json (3)
│   │   └── 9S (3)
│   │       │   └── meta.json (3)
│   └── 1M (141)
│       │   ├── 0S (3)
│       │   │   └── meta.json (3)
│       │   ├── 10S (3)
│       │   │   └── meta.json (3)
│       │   ├── 11S (3)
│       │   │   └── meta.json (3)
│       │   ├── 12S (3)
│       │   │   └── meta.json (3)
│       │   ├── 13S (3)
│       │   │   └── meta.json (3)
│       │   ├── 14S (3)
│       │   │   └── meta.json (3)
│       │   ├── 15S (3)
│       │   │   └── meta.json (3)
│       │   ├── 16S (3)
│       │   │   └── meta.json (3)
│       │   ├── 17S (3)
│       │   │   └── meta.json (3)
│       │   ├── 18S (3)
│       │   │   └── meta.json (3)
│       │   ├── 19S (3)
│       │   │   └── meta.json (3)
│       │   ├── 1S (3)
│       │   │   └── meta.json (3)
│       │   ├── 20S (3)
│       │   │   └── meta.json (3)
│       │   ├── 21S (3)
│       │   │   └── meta.json (3)
│       │   ├── 22S (3)
│       │   │   └── meta.json (3)
│       │   ├── 23S (3)
│       │   │   └── meta.json (3)
│       │   ├── 24S (3)
│       │   │   └── meta.json (3)
│       │   ├── 25S (3)
│       │   │   └── meta.json (3)
│       │   ├── 26S (3)
│       │   │   └── meta.json (3)
│       │   ├── 27S (3)
│       │   │   └── meta.json (3)
│       │   ├── 28S (3)
│       │   │   └── meta.json (3)
│       │   ├── 29S (3)
│       │   │   └── meta.json (3)
│       │   ├── 2S (3)
│       │   │   └── meta.json (3)
│       │   ├── 30S (3)
│       │   │   └── meta.json (3)
│       │   ├── 31S (3)
│       │   │   └── meta.json (3)
│       │   ├── 32S (3)
│       │   │   └── meta.json (3)
│       │   ├── 33S (3)
│       │   │   └── meta.json (3)
│       │   ├── 34S (3)
│       │   │   └── meta.json (3)
│       │   ├── 35S (3)
│       │   │   └── meta.json (3)
│       │   ├── 36S (3)
│       │   │   └── meta.json (3)
│       │   ├── 37S (3)
│       │   │   └── meta.json (3)
│       │   ├── 38S (3)
│       │   │   └── meta.json (3)
│       │   ├── 39S (3)
│       │   │   └── meta.json (3)
│       │   ├── 3S (3)
│       │   │   └── meta.json (3)
│       │   ├── 40S (3)
│       │   │   └── meta.json (3)
│       │   ├── 41S (3)
│       │   │   └── meta.json (3)
│       │   ├── 42S (3)
│       │   │   └── meta.json (3)
│       │   ├── 43S (3)
│       │   │   └── meta.json (3)
│       │   ├── 44S (3)
│       │   │   └── meta.json (3)
│       │   ├── 45S (3)
│       │   │   └── meta.json (3)
│       │   ├── 46S (3)
│       │   │   └── meta.json (3)
│       │   ├── 47S (3)
│       │   │   └── meta.json (3)
│       │   ├── 48S (3)
│       │   │   └── meta.json (3)
│       │   ├── 49S (3)
│       │   │   └── meta.json (3)
│       │   ├── 4S (3)
│       │   │   └── meta.json (3)
│       │   ├── 50S (3)
│       │   │   └── meta.json (3)
│       │   ├── 51S (3)
│       │   │   └── meta.json (3)
│       │   └── 52S (0)
└── LADYBIRD.xml (8)
----
----
Full Path: LADYBIRD.xml

<Clip_Manifest NumDirs="498">
  <_1 Name="CLIP2" In="1.6261465427355111E-307" InIdx="228" Out="1.6261466707242047E-307" OutIdx="4110" Locked="True" InStr="07:27:16.618 08/13/2024" Epoch="1723559236.618" Pos="0H/0M/3.8S/" />
  <_2 Name="CLIP1" In="1.6261465850368715E-307" InIdx="1511" Out="1.6261470057932999E-307" OutIdx="14273" Locked="True" InStr="07:27:38.022 08/13/2024" Epoch="1723559258.0219998" Pos="0H/0M/25.1833333333333S/" />
  <_3 Name="CLIP3" In="1.6261501214407288E-307" InIdx="14658" Out="1.6261501214407288E-307" OutIdx="14658" Locked="True" InStr="07:57:27.463 08/13/2024" Epoch="1723561047.4629998" Pos="0H/4M/4.30000000000001S/" />
  <_4 Name="CLIP4" In="1.6261504029336424E-307" InIdx="15096" Out="1.6261504567393675E-307" OutIdx="16728" Locked="True" InStr="07:59:49.900 08/13/2024" Epoch="1723561189.8999999" Pos="0H/4M/11.6S/" />
  <_5 Name="CLIP6" In="1.626151890120643E-307" InIdx="17124" Out="1.6261520105896575E-307" OutIdx="20778" Locked="True" InStr="08:12:22.425 08/13/2024" Epoch="1723561942.425" Pos="0H/4M/45.4S/" />
  <_6 Name="CLIP7" In="1.6261529151745092E-307" InIdx="21221" Out="1.6261531935026773E-307" OutIdx="29663" Locked="True" InStr="08:21:01.108 08/13/2024" Epoch="1723562461.108" Pos="0H/5M/53.6833333333333S/" />
</Clip_Manifest>

----
Full Path: 0H/1M/43S/meta.json

{
"Time":{"x0":1723559335.914, "xi-x0":[0,0.017,0.033,0.050,0.067,0.083,0.100,0.117,0.133,0.150,0.167,0.183,0.200,0.217,0.233,0.250,0.267,0.284,0.300,0.317,0.334,0.350,0.367,0.384,0.400,0.417,0.434,0.450,0.467,0.484,0.500,0.517,0.534,0.550,0.567,0.584,0.601,0.617,0.634,0.651,0.667,0.684,0.701,0.717,0.734,0.751,0.767,0.784,0.801,0.817,0.834,0.851,0.867,0.884,0.901,0.917,0.934,0.951,0.968,0.984]}
}

----
Full Path: 0H/1M/44S/meta.json

{
"Time":{"x0":1723559336.915, "xi-x0":[0,0.017,0.033,0.050,0.067,0.083,0.100,0.117,0.133,0.150,0.167,0.183,0.200,0.217,0.233,0.250,0.267,0.284,0.300,0.317,0.334,0.350,0.367,0.384,0.400,0.417,0.434,0.450,0.467,0.484,0.500,0.517,0.534,0.550,0.567,0.584,0.600,0.617,0.634,0.651,0.667,0.684,0.701,0.717,0.734,0.751,0.767,0.784,0.801,0.817,0.834,0.851,0.867,0.884,0.901,0.917,0.934,0.951,0.968,0.984]}
}
```


---

# COSM C360 Tools Project Context

## Overview
The COSM C360 Tools project (`cosmos`) is a utility for converting specialized video output from COSM C360 cameras (commonly used in professional sports production, e.g., NFL pylon cameras) into standard MP4 format. The tool processes the camera's unique output format, which consists of multiple tiled HEVC streams with accompanying metadata.

## Target Users
- **Primary Users**: Ecologists and scientists deploying these cameras for field research
- **Technical Level**: Non-technical users who need to review footage before submitting to main analysis pipeline
- **Use Case**: Converting raw camera format to standard MP4s for review and ingest into ecological analysis tools

## User Considerations
1. **Technical Expertise**
   - Users are not technically sophisticated
   - Need simple, guided interface
   - Should handle errors gracefully with clear explanations
   - Must provide clear feedback about processing status

2. **System Requirements**
   - Must support Windows (primary platform for users)
   - Must work on low-end systems (not workstation-grade machines)
   - Should provide options for memory-constrained systems
   - Should automatically detect and use best available encoding options

3. **Workflow Integration**
   - Tool will eventually be integrated into main ecological analysis software
   - Currently needed as standalone utility for pre-processing
   - Should maintain compatibility with analysis pipeline requirements

## Key Requirements Beyond Technical Specs

1. **Usability**
   - Interactive mode for guided operation
   - Clear progress indication
   - Informative error messages
   - Pre-flight validation to catch issues early
   - No technical knowledge required for basic operation

2. **Robustness**
   - Automatic encoder selection and fallback
   - Handles partial or corrupted data gracefully
   - Works across different platforms
   - Adapts to available system resources

3. **System Adaptation**
   - Automatic detection of optimal settings
   - Low-memory mode for constrained systems
   - Fallback to software encoding if hardware encoding unavailable
   - Clear warnings about system requirements

4. **Error Handling**
   - Clear, non-technical error messages
   - Validation before processing starts
   - Helpful suggestions for resolving issues
   - Graceful handling of partial or corrupted data

## Development Priorities
1. **Core Functionality**
   - Reliable video processing
   - Robust input validation
   - Cross-platform compatibility
   - Memory usage optimization

2. **User Experience**
   - Simple, guided interface
   - Clear progress reporting
   - Informative feedback
   - Error resilience

3. **Optional Enhancements**
   - Configuration saving
   - Processing resumption
   - Automated updates
   - Additional format support

## Deployment Considerations
- Tool will be distributed via public repository
- Users will need to pull repo and follow installation instructions
- Should minimize external dependencies
- Must include clear installation and usage documentation
- Should provide support for common issues

## Integration Context
This tool is part of a larger ecological analysis pipeline:
1. Raw footage captured with COSM C360 cameras
2. Conversion to standard MP4 format (this tool)
3. Ingestion into ecological analysis software
4. Analysis of ecological activity in footage

## Future Considerations
- Tool may be integrated directly into main analysis software
- May need to handle additional camera formats
- Could expand to support batch processing
- Might need additional output format options