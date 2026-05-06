"""Tests for form_analysis.py — pure functions, no mocking needed."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import pytest
from form_analysis import angle_between, kp_by_name, compute_squat_metrics, detect_squat_faults


class TestAngleBetween:
    def test_right_angle(self):
        """90-degree angle: a=(0,1), b=(0,0), c=(1,0)."""
        angle = angle_between((0, 1), (0, 0), (1, 0))
        assert abs(angle - 90.0) < 0.001

    def test_straight_line_180(self):
        """Collinear points → 180 degrees."""
        angle = angle_between((-1, 0), (0, 0), (1, 0))
        assert abs(angle - 180.0) < 0.001

    def test_zero_length_vector_returns_none(self):
        """Degenerate case: a == b → magnitude 0 → returns None."""
        result = angle_between((1, 1), (1, 1), (2, 2))
        assert result is None

    def test_acute_angle(self):
        angle = angle_between((1, 0), (0, 0), (1, 1))
        assert 44 < angle < 46   # ~45 degrees


class TestKpByName:
    def test_builds_name_dict(self):
        kps = [{'name': 'left_knee', 'x': 1, 'y': 2, 'score': 0.9}]
        d = kp_by_name(kps)
        assert 'left_knee' in d
        assert d['left_knee']['x'] == 1

    def test_empty_list(self):
        assert kp_by_name([]) == {}


class TestComputeSquatMetrics:
    def _make_kps(self, lhip, lknee, lankle, rhip, rknee, rankle):
        return [
            {'name': 'left_hip',    'x': lhip[0],   'y': lhip[1],   'score': 0.9},
            {'name': 'left_knee',   'x': lknee[0],  'y': lknee[1],  'score': 0.9},
            {'name': 'left_ankle',  'x': lankle[0], 'y': lankle[1], 'score': 0.9},
            {'name': 'right_hip',   'x': rhip[0],   'y': rhip[1],   'score': 0.9},
            {'name': 'right_knee',  'x': rknee[0],  'y': rknee[1],  'score': 0.9},
            {'name': 'right_ankle', 'x': rankle[0], 'y': rankle[1], 'score': 0.9},
        ]

    def test_standing_pose_near_180(self):
        """Straight legs → knee angle near 180°."""
        kps = self._make_kps(
            (0, 0), (0, 10), (0, 20),   # left: hip, knee, ankle — straight vertical
            (5, 0), (5, 10), (5, 20),   # right: same
        )
        m = compute_squat_metrics(kps)
        assert abs(m['left_knee']  - 180.0) < 1.0
        assert abs(m['right_knee'] - 180.0) < 1.0

    def test_deep_squat_low_angle(self):
        """Bent knee → angle < 90°.
        hip=(0,0), knee=(0,5), ankle=(3,3) → ~56° at the knee (verified analytically)."""
        kps = self._make_kps(
            (0, 0), (0, 5), (3, 3),   # hip→knee vertical, ankle offset → ~56° (verified)
            (0, 0), (0, 5), (3, 3),
        )
        m = compute_squat_metrics(kps)
        assert m['left_knee'] < 90

    def test_missing_keypoints_returns_empty(self):
        """Missing keypoints should return {} not raise."""
        m = compute_squat_metrics([{'name': 'nose', 'x': 0, 'y': 0, 'score': 0.9}])
        assert m == {}

    def test_both_keys_present(self):
        kps = self._make_kps(
            (0, 0), (0, 10), (0, 20),
            (5, 0), (5, 10), (5, 20),
        )
        m = compute_squat_metrics(kps)
        assert 'left_knee'  in m
        assert 'right_knee' in m


class TestDetectSquatFaults:
    def test_no_faults_at_standing(self):
        assert detect_squat_faults({'left_knee': 170, 'right_knee': 165}) == []

    def test_both_knees_too_bent(self):
        faults = detect_squat_faults({'left_knee': 50, 'right_knee': 55})
        assert 'left_knee_bend_too_far'  in faults
        assert 'right_knee_bend_too_far' in faults

    def test_only_left_fault(self):
        faults = detect_squat_faults({'left_knee': 60, 'right_knee': 80})
        assert 'left_knee_bend_too_far'  in faults
        assert 'right_knee_bend_too_far' not in faults

    def test_boundary_exactly_70_is_ok(self):
        """Angle == 70 is not a fault (condition is < 70)."""
        assert detect_squat_faults({'left_knee': 70, 'right_knee': 70}) == []

    def test_empty_metrics_no_crash(self):
        assert detect_squat_faults({}) == []
