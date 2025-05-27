# Mouse Behavior Annotation System

A system for annotating mouse behavior in video segments using a standardized ethogram. This tool helps researchers efficiently label social interactions and behaviors in mouse experiment videos.

## Overview

This annotation system:
- Automatically extracts consistent behavior segments from videos
- Provides a web-based interface for behavior annotation
- Uses a standardized mouse ethogram for classification
- Supports annotation of both mice in social interactions
- Records confidence levels for all annotations

## Requirements

### Dependencies

```bash
# Core dependencies
pip install flask numpy scipy tqdm

# Video processing 
brew install ffmpeg  # for macOS
# OR
sudo apt install ffmpeg  # for Ubuntu/Debian
```

### System Requirements

- Python 3.6+
- Modern web browser (Chrome, Firefox, Safari)
- Sufficient disk space for video clips (depends on dataset size)

## Data Organization

Organize your data in the following structure:

```
DATA_ROOT/
├── 20220922M3M4/                  # Experiment folder (format: YYYYMMDD + mouse IDs)
│   ├── videos/                    # Video files
│   │   ├── cam1.mp4               # Camera 1 view  
│   │   └── cam2.mp4               # Camera 2 view
│   └── labels/                    # Label files
│       └── sdannce_data.mat       # Contains tracking data in sdannce format
├── 20221015M1M2/                  # Another experiment
│   ├── videos/
│   └── labels/
└── ...
```

### MAT File Format

The system expects a MAT file with an sdannce structure containing:

- `ratid`: ID of the focal mouse
- `ratp_id`: ID of the partner mouse
- `hljc`: High-level joint clusters

- `lljc`: Low-level joint clusters
- `hlac`: High-level action clusters
- `llac`: Low-level action clusters
- `part_hljc`, `part_lljc`, `part_hlac`, `part_llac`: Partner mouse data

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DavidDING21/mouse_behavior_annotation.git
   cd mouse-behavior-annotation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the data path in **app.py**:

   ```python
   # Change this to your data directory
   DATA_ROOT = "/path/to/your/experiment/data" 
   ```

## Usage

### Starting the Application

```bash
python app.py
```

The system will:
1. Load experiment data from the DATA_ROOT directory
2. Identify potential segments of consistent behavior
3. Sample segments (5 examples per behavior cluster by default)
4. Extract video clips for the sampled segments
5. Start a web server at http://127.0.0.1:5000/

### Annotation Workflow

1. **Select a Video Segment**:
   - Choose a segment from the dropdown menu
   - Click "Load Segment" to view the video clips

2. **Watch the Video Clips**:
   - Multiple camera views will be displayed
   - Each clip shows the same time segment from different angles

3. **Annotate Behaviors**:
   - First, determine if there is a social interaction (Yes/No)
   - For the focal mouse (BLUE), select a behavior from the ethogram
   - For the partner mouse (RED), select a behavior from the ethogram
   - Set confidence levels for each annotation (0-1 scale)

4. **Save Your Annotation**:
   - Click "Save Annotation" to record your labels
   - The segment will be marked as annotated in the dropdown

## Output Files

The system generates and uses the following files:

1. **segments.json**: Contains all sampled video segments with their metadata
   
   > Delete this file to force re-sampling of segments

2. **annotations.json**: Contains all human annotations

   > Format: Key-value pairs where keys are segment identifiers

   Each annotation includes:

   - Frame range information
   - Social interaction status with confidence
   - Focal mouse behavior with confidence
   - Partner mouse behavior with confidence
   - Metadata (experiment ID, mouse IDs, timestamp)

3. **Video Clips**: Extracted video segments
   - Location: `static/clips/` directory
   - Format: MP4 files with unique UUIDs as filenames

## Customization

### Changing Sampling Parameters

Edit the following parameters in **app.py**:

```python
# Increase number of samples per cluster (default is 15)
segments = prepare_segments_data(all_segments, SEGMENTS_FILE, sample=True, samples_per_cluster=10)
```

### Adjusting Segment Length

Edit the following parameters in **data_loader.py**:

```python
# Change min and max segment length (in frames)
def find_consistent_segments(hljc, min_length=150, max_length=250):
```

## Citation

If you use this annotation system in your research, please cite:

```
@software{MouseBehaviorAnnotation,
  author = {Honghe Ding},
  title = {Mouse Behavior Annotation System},
  year = {2025},
  url = {https://github.com/DavidDING21/mouse_behavior_annotation.git}
}
```