# COSM C360 Tools - Command Reference

This comprehensive reference guide documents all available commands and options for the COSM C360 Tools. This reference is particularly useful for advanced users who prefer command-line operation over interactive mode.

## 🔍 Basic Commands

### Interactive Mode (Recommended for Most Users)
```bash
python cosmos.py --interactive
```

### Process Videos with Default Settings (4K, Balanced Quality)
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output
```

### Windows Path Format Examples
```powershell
# Basic processing with Windows paths
python cosmos.py --input-dir C:\Users\YourName\Videos\COSM_Input --output-dir C:\Users\YourName\Videos\COSM_Output

# Note: For Windows paths with spaces, use quotes
python cosmos.py --input-dir "C:\Users\Your Name\Videos\COSM Input" --output-dir "C:\Users\Your Name\Videos\COSM Output"
```

### macOS/Linux Path Format Examples
```bash
# Using absolute paths
python cosmos.py --input-dir /home/username/Videos/COSM_Input --output-dir /home/username/Videos/COSM_Output

# Using home directory shorthand
python cosmos.py --input-dir ~/Videos/COSM_Input --output-dir ~/Videos/COSM_Output

# With spaces in paths
python cosmos.py --input-dir "/home/username/My Videos/COSM Input" --output-dir "/home/username/My Videos/Output"
```

## 🔧 System and Testing Commands

### Run System Self-Test (Verifies Setup without Processing)
```bash
python cosmos.py --self-test
```

### Run Self-Test on Specific Directories
```bash
python cosmos.py --self-test --input-dir /path/to/input --output-dir /path/to/output
```

### Check for Updates
```bash
python cosmos.py --check-updates
```

## 🎬 Output Configuration Options

### Set Output Resolution
```bash
# Using preset resolutions
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --output-resolution 1080p
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --output-resolution 4k
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --output-resolution 8k

# Using custom resolution
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --output-resolution 1920x1080
```
Available presets: `720p`, `1080p`, `4k`, `8k`, `original`

### Set Quality Mode
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --quality-mode balanced
```
Available modes:
- `quality`: Highest quality, slower processing
- `balanced`: Good balance of quality and speed (default)
- `performance`: Faster processing, lower quality
- `low_memory`: Reduced memory usage, slower
- `minimal`: Minimal resource usage, single thread (slowest)

### Enable Low Memory Mode
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --low-memory
```

### Set Custom CRF Value (Video Quality)
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --crf 23
```
Lower values (18-23) produce higher quality but larger files, higher values (24-28) produce smaller files with lower quality.

## 📂 Input/Output Options

### Name Your Processing Job
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --job-name MyJobName
```

### Specify a Particular Manifest File
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --manifest /path/to/specific_manifest.xml
```

## 📝 Logging Options

### Create a Log File
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --log-file processing.log
```

### Set Logging Level
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --log-level DEBUG
```
Available levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

## 💾 Configuration Management

### Load a Saved Configuration
```bash
python cosmos.py --config MySettings
```

### Save Current Settings as a Configuration
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --save-config MySettings
```

## 💡 Usage Examples for Common Scenarios

### Resource-Constrained Systems (16GB RAM or less)
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --quality-mode minimal --low-memory --output-resolution 1080p
```

### Highest Quality Output (Powerful Systems)
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --quality-mode quality --output-resolution 8k --crf 18
```

### Quick Preview Processing
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --quality-mode performance --output-resolution 720p
```

### Detailed Debugging for Troubleshooting
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --log-level DEBUG --log-file debug.log --self-test
```

## ⚠️ Common Command Combinations for Specific Use Cases

### For Large 8K+ Files on Limited Hardware (16GB RAM)
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --quality-mode minimal --low-memory --output-resolution 1080p
```

### For Fastest Processing (with Quality Trade-offs)
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --quality-mode performance --output-resolution 720p
```

### For Maximum Quality (with Longer Processing Time)
```bash
python cosmos.py --input-dir /path/to/input --output-dir /path/to/output --quality-mode quality --output-resolution original
```

## 💡 Tips for Command Line Use

- Always run `--self-test` the first time you use the tool on a new system
- Use unique job names to keep track of different processing runs
- Check the `job_info.txt` file in the output directory for processing details after each run
- If you find settings you like, save them with `--save-config` for easy reuse
- When troubleshooting, always use `--log-level DEBUG` to get more detailed information
- For best results on resource-constrained systems, close other applications during processing