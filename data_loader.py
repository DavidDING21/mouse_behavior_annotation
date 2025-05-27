import os
import glob
import scipy.io as sio
import numpy as np

def find_consistent_segments(hljc, min_length=150, max_length=250):
    """Find segments where hljc values remain consistent"""
    segments = []
    i = 0
    
    while i < len(hljc):
        current_cluster = hljc[i][0]
        start = i
        
        # Find consecutive frames with the same cluster value
        while i < len(hljc) and hljc[i][0] == current_cluster:
            i += 1
        
        # Check segment length
        segment_length = i - start
        if segment_length >= min_length:
            # If segment is too long, split into multiple segments
            for j in range(start, i, max_length):
                end = min(j + max_length, i)
                if end - j >= min_length:
                    segments.append((j, end, current_cluster))
    
    return segments

def load_experiment_data(root_dir):
    """Load data from experiment folders and identify potential segments without extracting"""
    experiments = {}
    all_segments = []
    
    # Find all potential experiment folders
    for item in os.listdir(root_dir):
        exp_dir = os.path.join(root_dir, item)
        if not os.path.isdir(exp_dir):
            continue
            
        # Check if directory structure matches expected
        labels_dir = os.path.join(exp_dir, 'labels')
        videos_dir = os.path.join(exp_dir, 'videos')
        
        if not (os.path.exists(labels_dir) and os.path.exists(videos_dir)):
            continue
        
        # Load labels and videos
        experiment_data = {
            'date': item,
            'labels': {},
            'videos': [],
            'segments': []
        }
        
        # Load video files (keep reference to original videos)
        videos = []
        for ext in ['mp4', 'avi', 'mov']:
            video_files = glob.glob(os.path.join(videos_dir, f'*.{ext}'))
            videos.extend(video_files)
            experiment_data['videos'].extend(video_files)
        
        # Load only one .mat file - they contain data for both mice
        mat_files = glob.glob(os.path.join(labels_dir, '*.mat'))
        if mat_files:  # Only process the first mat file found
            try:
                mat_file = mat_files[0]
                print(f"Loading MAT file: {mat_file}")
                mat_data = sio.loadmat(mat_file)
                
                if 'sdannce' in mat_data:
                    sdannce = mat_data['sdannce']
                    
                    # Get IDs for both mice
                    focal_rat_id = str(sdannce['ratid'][0, 0][0])
                    partner_rat_id = str(sdannce['ratp_id'][0, 0][0])
                    
                    print(f"Found data for mice: {focal_rat_id} and {partner_rat_id}")
                    
                    # Get cluster data for segmentation
                    hljc = sdannce['hljc'][0, 0]
                    lljc = sdannce['lljc'][0, 0]
                    hlac = sdannce['hlac'][0, 0]
                    llac = sdannce['llac'][0, 0]
                    
                    # Partner data
                    part_hljc = sdannce['part_hljc'][0, 0] if 'part_hljc' in sdannce.dtype.names else None
                    part_lljc = sdannce['part_lljc'][0, 0] if 'part_lljc' in sdannce.dtype.names else None
                    part_hlac = sdannce['part_hlac'][0, 0] if 'part_hlac' in sdannce.dtype.names else None
                    part_llac = sdannce['part_llac'][0, 0] if 'part_llac' in sdannce.dtype.names else None
                    
                    # Find consistent segments
                    segments = find_consistent_segments(hljc)
                    
                    # Create segment data without extracting videos
                    for start_frame, end_frame, cluster in segments:
                        segment_data = {
                            'exp_id': item,
                            'rat_id': focal_rat_id,
                            'partner_id': partner_rat_id,
                            'start_frame': int(start_frame),
                            'end_frame': int(end_frame),
                            'cluster': int(cluster),
                            'videos': videos,  # Store references to original videos
                            'clips': [],  # Will be populated later after sampling
                            'cluster_data': {
                                'hljc': hljc[start_frame:end_frame].flatten().tolist(),
                                'lljc': lljc[start_frame:end_frame].flatten().tolist(),
                                'hlac': hlac[start_frame:end_frame].flatten().tolist(),
                                'llac': llac[start_frame:end_frame].flatten().tolist(),
                            }
                        }
                        
                        # Add partner data if available
                        if part_hljc is not None:
                            segment_data['partner_cluster_data'] = {
                                'hljc': part_hljc[start_frame:end_frame].flatten().tolist(),
                                'lljc': part_lljc[start_frame:end_frame].flatten().tolist(),
                                'hlac': part_hlac[start_frame:end_frame].flatten().tolist(),
                                'llac': part_llac[start_frame:end_frame].flatten().tolist(),
                            }
                        
                        experiment_data['segments'].append(segment_data)
                        all_segments.append(segment_data)
            except Exception as e:
                print(f"Error loading {mat_file}: {e}")
                import traceback
                traceback.print_exc()
        
        if experiment_data['videos'] and experiment_data['segments']:
            experiments[item] = experiment_data
    
    return experiments, all_segments