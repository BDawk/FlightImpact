"""Smoke tests — make sure all models construct, serialize, and round-trip."""

from core.models import (
    CameraCalibration,
    DeviceStatus,
    RadarCalibration,
    RadarSpectrum,
    Shot,
    ShotMetrics,
    ShotStatus,
)


def test_shot_construct_and_dump():
    shot = Shot(
        status=ShotStatus.COMPLETE,
        metrics=ShotMetrics(
            ball_speed_mph=152.4,
            launch_angle_deg=12.6,
            spin_rate_rpm=2710,
        ),
        club="Driver",
    )
    payload = shot.model_dump_json()
    restored = Shot.model_validate_json(payload)
    assert restored.metrics.ball_speed_mph == 152.4
    assert restored.club == "Driver"
    assert restored.status == ShotStatus.COMPLETE


def test_shot_metrics_clamping():
    """Pydantic should reject out-of-range values."""
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ShotMetrics(ball_speed_mph=999)


def test_camera_calibration_roundtrip():
    cal = CameraCalibration(
        fx=1500.0,
        fy=1500.0,
        cx=960.0,
        cy=540.0,
        distortion=[-0.12, 0.04, 0.0, 0.0, 0.0],
        width=1920,
        height=1080,
        mm_per_pixel=0.42,
    )
    payload = cal.model_dump_json()
    restored = CameraCalibration.model_validate_json(payload)
    assert restored.mm_per_pixel == 0.42


def test_radar_defaults_are_sane():
    cal = RadarCalibration()
    assert cal.sample_rate_hz == 20000
    assert cal.fft_size == 1024
    assert 0.02 < cal.speed_per_hz_mph < 0.05


def test_telemetry_messages():
    status = DeviceStatus(
        camera_connected=True,
        radar_connected=True,
        uno_connected=False,
        cpu_percent=12.4,
        memory_percent=34.1,
        temperature_c=48.2,
        uptime_s=3600,
        ap_mode=True,
        wifi_ssid="FlightImpact-A1B2",
        ip_address="192.168.4.1",
    )
    payload = status.model_dump_json()
    assert "camera_connected" in payload

    spec = RadarSpectrum(
        freq_hz=[100, 200, 300],
        magnitudes_db=[-40, -30, -50],
        peak_freq_hz=200,
        peak_speed_mph=6.4,
    )
    assert RadarSpectrum.model_validate_json(spec.model_dump_json()).peak_speed_mph == 6.4


def test_radar_dsp_fft_runs():
    """End-to-end smoke test for the radar DSP module."""
    import numpy as np

    from core.algorithms.radar_dsp import compute_spectrum, detect_peak, freq_to_speed_mph

    sr = 20000
    n = 1024
    target_freq = 4775.0  # ~152 mph at default coefficient
    t = np.arange(n) / sr
    samples = 0.6 * np.sin(2 * np.pi * target_freq * t)
    samples += 0.05 * np.random.RandomState(0).randn(n)

    freqs, mags = compute_spectrum(samples, sr)
    result = detect_peak(freqs, mags, min_freq_hz=200, max_freq_hz=6000, min_snr_db=10)

    assert result.peak_freq_hz is not None
    # Peak should land within one bin of the target
    bin_hz = sr / n
    assert abs(result.peak_freq_hz - target_freq) <= bin_hz

    speed = freq_to_speed_mph(result.peak_freq_hz)
    assert 150 < speed < 155
