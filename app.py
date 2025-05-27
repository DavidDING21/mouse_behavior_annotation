from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime
from data_loader import load_experiment_data
from segment_sampler import prepare_segments_data

app = Flask(__name__)

# Configuration
DATA_ROOT = "."  # Data root directory
SEGMENTS_FILE = os.path.join(DATA_ROOT, "segments.json")
ANNOTATIONS_FILE = os.path.join(DATA_ROOT, "annotations.json")
CLIPS_DIR = os.path.join('static', 'clips')  # Clips storage directory

# Ensure clips directory exists
os.makedirs(CLIPS_DIR, exist_ok=True)

# Load data
print("Loading experiment data...")
experiments, all_segments = load_experiment_data(DATA_ROOT)
print(f"Loaded metadata for {len(all_segments)} potential segments from {len(experiments)} experiments")

# Load or create segment data
if os.path.exists(SEGMENTS_FILE):
    with open(SEGMENTS_FILE, 'r') as f:
        segments = json.load(f)
    print(f"Loaded {len(segments)} segments from {SEGMENTS_FILE}")
else:
    # Sample segments and extract clips - increased samples_per_cluster to 15
    segments = prepare_segments_data(all_segments, SEGMENTS_FILE, sample=True, samples_per_cluster=15)
    print(f"Created {len(segments)} segments with clips and saved to {SEGMENTS_FILE}")

# Load or create annotation data
if os.path.exists(ANNOTATIONS_FILE):
    with open(ANNOTATIONS_FILE, 'r') as f:
        annotations = json.load(f)
    print(f"Loaded {len(annotations)} annotations from {ANNOTATIONS_FILE}")
else:
    annotations = {}
    print("No existing annotations found, starting fresh")

@app.route('/')
def index():
    # Return main HTML page
    return render_template('index.html')

@app.route('/get_segments')
def get_segments():
    # Return all segment data
    return jsonify(segments)

@app.route('/get_annotations')
def get_annotations():
    # Return all annotation data
    return jsonify(annotations)

@app.route('/clips/<filename>')
def clip(filename):
    # Serve video clips
    return send_from_directory(CLIPS_DIR, filename)

@app.route('/save_annotation', methods=['POST'])
def save_annotation():
    data = request.json
    
    # Create unique key
    segment_key = f"{data['exp_id']}_{data['rat_id']}_{data['start_frame']}_{data['end_frame']}"
    
    # Save annotation data with behaviors for both mice
    annotations[segment_key] = {
        # Frame range information
        'start_frame': data['start_frame'],
        'end_frame': data['end_frame'],
        
        # Social interaction
        'has_interaction': data['has_interaction'],
        'interaction_confidence': data['interaction_confidence'],
        
        # Focal mouse behavior
        'focal_behavior': data['focal_behavior'],
        'focal_confidence': data['focal_confidence'],
        
        # Partner mouse behavior
        'partner_behavior': data['partner_behavior'],
        'partner_confidence': data['partner_confidence'],
        
        # Metadata for reference
        'exp_id': data['exp_id'],
        'rat_id': data['rat_id'],
        'partner_id': data.get('partner_id', ''),
        'annotation_time': data.get('annotation_time', datetime.now().isoformat())
    }
    
    # Write to file
    with open(ANNOTATIONS_FILE, 'w') as f:
        json.dump(annotations, f)
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)