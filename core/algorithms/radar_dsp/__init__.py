"""Radar DSP — Doppler shift extraction from HB100 IF samples.

The HB100 outputs an audio-frequency signal whose frequency is proportional
to the radial velocity of the target. We sample it, FFT it, find the peak,
and convert to mph.

Reference: speed_mps = freq_hz * c / (2 * f_radar)
For HB100 at 10.525 GHz: 1 mph ≈ 31.36 Hz
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class SpectrumResult:
    """Single FFT result with optional detected peak."""

    freq_hz: np.ndarray
    magnitudes_db: np.ndarray
    peak_freq_hz: Optional[float]
    peak_magnitude_db: Optional[float]
    snr_db: Optional[float]


def compute_spectrum(
    samples: np.ndarray,
    sample_rate_hz: int,
    window: str = "hann",
) -> tuple[np.ndarray, np.ndarray]:
    """Windowed real-FFT producing (freq_bins_hz, magnitude_db).

    Args:
        samples: 1-D float array of IF samples, DC-removed by caller.
        sample_rate_hz: Sample rate of the ADC.
        window: One of hann / hamming / blackman.
    """
    n = len(samples)
    if window == "hann":
        w = np.hanning(n)
    elif window == "hamming":
        w = np.hamming(n)
    elif window == "blackman":
        w = np.blackman(n)
    else:
        raise ValueError(f"Unknown window: {window}")

    spectrum = np.fft.rfft(samples * w)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate_hz)
    # Magnitude in dB, with floor to avoid log(0)
    mags = 20.0 * np.log10(np.abs(spectrum) / n + 1e-12)
    return freqs, mags


def detect_peak(
    freqs: np.ndarray,
    mags_db: np.ndarray,
    min_freq_hz: float,
    max_freq_hz: float,
    min_snr_db: float,
) -> SpectrumResult:
    """Find the strongest peak inside [min_freq_hz, max_freq_hz] with SNR check.

    SNR is computed as peak magnitude minus the median magnitude in the band.
    """
    mask = (freqs >= min_freq_hz) & (freqs <= max_freq_hz)
    if not mask.any():
        return SpectrumResult(freqs, mags_db, None, None, None)

    band_mags = mags_db[mask]
    band_freqs = freqs[mask]

    peak_idx = int(np.argmax(band_mags))
    peak_mag = float(band_mags[peak_idx])
    peak_freq = float(band_freqs[peak_idx])
    noise_floor = float(np.median(band_mags))
    snr = peak_mag - noise_floor

    if snr < min_snr_db:
        return SpectrumResult(freqs, mags_db, None, None, snr)

    return SpectrumResult(freqs, mags_db, peak_freq, peak_mag, snr)


def freq_to_speed_mph(freq_hz: float, speed_per_hz_mph: float = 0.03187) -> float:
    """Convert a Doppler frequency to ball speed in mph.

    The default coefficient is the textbook value for HB100 at 10.525 GHz
    with the radar pointing directly at the target. Real installations
    have a cosine error from non-zero look angle, which is corrected via
    calibration (per RadarCalibration.speed_per_hz_mph).
    """
    return freq_hz * speed_per_hz_mph
