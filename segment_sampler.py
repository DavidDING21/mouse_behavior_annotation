import numpy as np
import json
import os
from collections import defaultdict
from tqdm import tqdm
from video_processor import extract_video_segment

def sample_segments_by_cluster(all_segments, samples_per_cluster=2):
    """Sample segments ensuring each hljc cluster type has representatives"""
    # Group by cluster
    cluster_segments = defaultdict(list)
    for segment in all_segments:
        cluster = int(segment['cluster'])
        cluster_segments[cluster].append(segment)
    
    # Sample from each cluster
    sampled_segments = []
    for cluster, segments in cluster_segments.items():
        n_samples = min(len(segments), samples_per_cluster)
        if n_samples > 0:
            indices = np.random.choice(len(segments), n_samples, replace=False)
            for idx in indices:
                sampled_segments.append(segments[idx])
    
    return sampled_segments

def extract_clips_for_segments(sampled_segments):
    """Extract video clips for sampled segments with progress bar"""
    print("Extracting video clips for sampled segments...")
    
    total_videos = sum(len(segment['videos']) for segment in sampled_segments)
    with tqdm(total=total_videos, desc="Extracting clips") as pbar:
        for segment in sampled_segments:
            segment_clips = []
            for video_path in segment['videos']:
                clip_path = extract_video_segment(
                    video_path,
                    segment['start_frame'],
                    segment['end_frame']
                )
                if clip_path:
                    segment_clips.append(clip_path)
                pbar.update(1)
            
            # Update segment with extracted clips
            segment['clips'] = segment_clips
    
    # Filter out segments with no clips
    return [segment for segment in sampled_segments if segment['clips']]

def prepare_segments_data(all_segments, output_json, sample=True, samples_per_cluster=2):
    """Prepare segment data, sample, extract clips, and save to JSON"""
    print(f"Found {len(all_segments)} total segments across all experiments")
    
    # Sample segments if requested
    if sample:
        sampled_segments = sample_segments_by_cluster(all_segments, samples_per_cluster)
        print(f"Sampled {len(sampled_segments)} segments ({samples_per_cluster} per cluster type)")
    else:
        sampled_segments = all_segments
        print(f"Using all {len(sampled_segments)} segments without sampling")
    
    # Extract clips for sampled segments
    segments_with_clips = extract_clips_for_segments(sampled_segments)
    print(f"Successfully extracted clips for {len(segments_with_clips)} segments")
    
    # Save to JSON
    with open(output_json, 'w') as f:
        json.dump(segments_with_clips, f)
    
    return segments_with_clips