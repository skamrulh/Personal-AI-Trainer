import math

def kp_by_name(keypoints):
    """
    keypoints: list of {name,x,y,score}
    returns dict name -> kp
    """
    return {kp['name']: kp for kp in keypoints}

def angle_between(a, b, c):
    (x1, y1) = a
    (x2, y2) = b
    (x3, y3) = c
    v1 = (x1 - x2, y1 - y2)
    v2 = (x3 - x2, y3 - y2)
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    if mag1 == 0 or mag2 == 0:
        return None
    cosang = max(-1.0, min(1.0, dot / (mag1*mag2)))
    ang = math.degrees(math.acos(cosang))
    return ang

def compute_squat_metrics(keypoints):
    kps = kp_by_name(keypoints)
    metrics = {}
    try:
        left_knee = angle_between(
            (kps['left_hip']['x'], kps['left_hip']['y']),
            (kps['left_knee']['x'], kps['left_knee']['y']),
            (kps['left_ankle']['x'], kps['left_ankle']['y'])
        )
        right_knee = angle_between(
            (kps['right_hip']['x'], kps['right_hip']['y']),
            (kps['right_knee']['x'], kps['right_knee']['y']),
            (kps['right_ankle']['x'], kps['right_ankle']['y'])
        )
    except KeyError:
        return {}
    metrics['left_knee'] = left_knee
    metrics['right_knee'] = right_knee
    return metrics

def detect_squat_faults(metrics):
    faults = []
    l = metrics.get('left_knee')
    r = metrics.get('right_knee')
    if l is not None and l < 70:
        faults.append('left_knee_bend_too_far')
    if r is not None and r < 70:
        faults.append('right_knee_bend_too_far')
    return faults
