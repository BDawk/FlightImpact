"""Radar service — pulls IF samples, runs FFT, emits spectrum + triggers.

Architecture:
  - sample loop: pulls sample blocks from the HAL, DC-removes, runs FFT,
    detects peaks
  - per spectrum: pushes to subscribers (dev-mode waterfall view)
  - trigger detection: when a peak above the configured threshold appears,
    fires the trigger callback (typically: tell the processor to grab a clip)

Trigger logic for a launch-side rig:
  1. Idle — low-frequency ambient noise only
  2. Club approach — Doppler frequency rises steeply (clubhead moving toward radar)
  3. Impact — usually a brief silence or chaotic broadband burst
  4. Ball flight — sustained high-frequency tone (the ball moving away)

For now the trigger is a simple threshold on the speed estimate. We tune it
with real data once the rig is built.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Callable, Optional

import numpy as np

from core.algorithms.radar_dsp import compute_spectrum, detect_peak, freq_to_speed_mph
from core.models import RadarCalibration
from flightimpact_devkit.config import RadarConfig, TriggerConfig
from flightimpact_devkit.hal import RadarSource

logger = logging.getLogger(__name__)


class RadarService:
    def __init__(
        self,
        source: RadarSource,
        config: RadarConfig,
        trigger_config: TriggerConfig,
        calibration: RadarCalibration | None = None,
    ):
        self._source = source
        self._config = config
        self._trigger_config = trigger_config
        self._calibration = calibration or RadarCalibration(
            sample_rate_hz=config.sample_rate_hz,
            fft_size=config.fft_size,
        )
        self._running = False
        self._spectrum_subscribers: list[Callable[[np.ndarray, np.ndarray, Optional[float], Optional[float]], None]] = []
        self._trigger_callback: Optional[Callable[[float], None]] = None
        self._last_trigger_ns = 0
        self._sample_buffer: deque[np.ndarray] = deque(maxlen=int(self._config.sample_rate_hz * 3 / self._config.fft_size))

    @property
    def connected(self) -> bool:
        return self._running

    def subscribe_spectrum(
        self,
        fn: Callable[[np.ndarray, np.ndarray, Optional[float], Optional[float]], None],
    ) -> Callable[[], None]:
        self._spectrum_subscribers.append(fn)
        return lambda: self._spectrum_subscribers.remove(fn)

    def set_trigger_callback(self, fn: Callable[[float], None]) -> None:
        """Called with the trigger speed (mph) when a shot is detected."""
        self._trigger_callback = fn

    async def start(self) -> None:
        await self._source.open()
        self._running = True
        asyncio.create_task(self._sample_loop())
        logger.info("Radar service started")

    async def stop(self) -> None:
        self._running = False
        await self._source.close()

    async def _sample_loop(self) -> None:
        import time

        try:
            async for block in self._source.sample_blocks():
                if not self._running:
                    break
                self._sample_buffer.append(block)

                # DC removal
                centered = block - np.mean(block)

                freqs, mags = compute_spectrum(
                    centered,
                    self._calibration.sample_rate_hz,
                    self._calibration.window,
                )
                result = detect_peak(
                    freqs,
                    mags,
                    self._calibration.min_freq_hz,
                    self._calibration.max_freq_hz,
                    self._calibration.min_snr_db,
                )

                speed = None
                if result.peak_freq_hz is not None:
                    speed = freq_to_speed_mph(result.peak_freq_hz, self._calibration.speed_per_hz_mph)

                # Notify subscribers of the spectrum (for the dev waterfall)
                for fn in list(self._spectrum_subscribers):
                    try:
                        fn(freqs, mags, result.peak_freq_hz, speed)
                    except Exception:
                        logger.exception("Spectrum subscriber raised; dropping")

                # Trigger detection
                if speed is not None and speed >= self._trigger_config.radar_speed_threshold_mph:
                    now_ns = time.monotonic_ns()
                    # Debounce: don't re-trigger within the post-trigger window
                    cooldown_ns = self._trigger_config.post_trigger_ms * 1_000_000
                    if now_ns - self._last_trigger_ns > cooldown_ns:
                        self._last_trigger_ns = now_ns
                        if self._trigger_callback is not None:
                            try:
                                self._trigger_callback(speed)
                            except Exception:
                                logger.exception("Trigger callback raised")
        except Exception:
            logger.exception("Sample loop crashed")
            self._running = False

    def snapshot_samples(self) -> np.ndarray:
        """Return all buffered samples as a single array (for shot recording)."""
        if not self._sample_buffer:
            return np.array([], dtype=np.float32)
        return np.concatenate(list(self._sample_buffer))
