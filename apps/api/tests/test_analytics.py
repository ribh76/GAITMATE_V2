from gaitmate_api.analytics import SensorMetrics, threshold_level


def test_threshold_level_at_boundaries() -> None:
    assert threshold_level(SensorMetrics(1.9, 0.9, 0.24)) == 1
    assert threshold_level(SensorMetrics(2.0, 0.0, 0.0)) == 2
    assert threshold_level(SensorMetrics(0.0, 0.0, 1.5)) == 5
