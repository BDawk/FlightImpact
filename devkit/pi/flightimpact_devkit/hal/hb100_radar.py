"""HB100 radar HAL.

Two implementations:
  - PiAudioRadar: feeds the HB100 IF output into the Pi's audio input
    (via a USB sound card or HAT). This is the simplest setup — uses ALSA
    capture, no microcontroller needed.
  - SerialRadar: when the Uno is acting as the ADC sampler, sample blocks
    arrive over USB serial as binary frames.
  - MockRadar: synthesizes a Doppler-like signal for testing without hardware.
"""

from __future__ import annotations

import asyncio
import struct
import time
from typing import AsyncIterator

import numpy as np

from flightimpact_devkit.config import RadarConfig


class MockRadar:
    """Synthetic radar — emits a signal that ramps up like a club approach + impact."""

    def __init__(self, config: RadarConfig):
        self._config = config
        self._t = 0.0

    async def open(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def sample_blocks(self) -> AsyncIterator[np.ndarray]:
        sr = self._config.sample_rate_hz
        block_size = self._config.fft_size
        block_period = block_size / sr
        rng = np.random.default_rng(42)

        while True:
            await asyncio.sleep(block_period)
            block_t = np.arange(block_size) / sr + self._t

            # Background noise
            samples = 0.02 * rng.standard_normal(block_size)

            # Periodic "shot" — ramps from low freq (background) to high freq
            # (ball post-impact) every ~3 seconds.
            cycle = self._t % 3.0
            if 1.0 < cycle < 1.4:
                # Club approach — slowly increasing freq
                freq = 800 + (cycle - 1.0) * 4000
                samples += 0.3 * np.sin(2 * np.pi * freq * block_t)
            elif 1.4 <= cycle < 2.0:
                # Ball flight — high freq tone
                freq = 4500 + 200 * np.sin(cycle * 5)
                samples += 0.5 * np.sin(2 * np.pi * freq * block_t)

            self._t += block_period
            yield samples.astype(np.float32)

    @property
    def sample_rate_hz(self) -> int:
        return self._config.sample_rate_hz


class SerialRadar:
    """Reads sample blocks from the Uno over USB serial.

    Frame format (from Uno firmware):
        magic   : 2 bytes   0xAA 0x55
        n_samples : 2 bytes  little-endian uint16
        samples : n_samples * 2 bytes  little-endian int16, centered at 0
    """

    MAGIC = b"\xaa\x55"

    def __init__(self, config: RadarConfig):
        self._config = config
        self._serial = None

    async def open(self) -> None:
        # Lazy-import pyserial so the module can be imported without it
        import serial

        self._serial = serial.Serial(
            self._config.serial_port,
            self._config.baud_rate,
            timeout=1.0,
        )

    async def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    async def sample_blocks(self) -> AsyncIterator[np.ndarray]:
        if self._serial is None:
            raise RuntimeError("Serial port not opened")
        loop = asyncio.get_event_loop()
        while True:
            block = await loop.run_in_executor(None, self._read_block)
            if block is not None:
                yield block

    def _read_block(self) -> np.ndarray | None:
        ser = self._serial
        # Sync to magic header
        sync = b""
        while sync != self.MAGIC:
            byte = ser.read(1)
            if not byte:
                return None
            sync = (sync + byte)[-2:]

        header = ser.read(2)
        if len(header) != 2:
            return None
        (n,) = struct.unpack("<H", header)
        raw = ser.read(n * 2)
        if len(raw) != n * 2:
            return None
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        return samples

    @property
    def sample_rate_hz(self) -> int:
        return self._config.sample_rate_hz


class PiAudioRadar:
    """Reads sample blocks from the Pi's ALSA audio input.

    Cheapest option — feed the HB100 op-amp output into a USB sound card's
    line-in (after appropriate level scaling and DC blocking caps). The Pi
    samples at 48 kHz natively; we resample to the configured rate.
    """

    def __init__(self, config: RadarConfig):
        self._config = config
        self._stream = None

    async def open(self) -> None:
        try:
            import sounddevice as sd
        except ImportError as e:
            raise RuntimeError(
                "PiAudioRadar requires sounddevice. Install with: "
                "pip install sounddevice"
            ) from e

        self._sd = sd
        # Open the input stream — actual reads happen in sample_blocks
        self._block_size = self._config.fft_size

    async def close(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    async def sample_blocks(self) -> AsyncIterator[np.ndarray]:
        loop = asyncio.get_event_loop()
        sd = self._sd
        sd.default.device = self._config.audio_device
        sd.default.samplerate = self._config.sample_rate_hz
        sd.default.channels = 1

        while True:
            block = await loop.run_in_executor(
                None, sd.rec, self._block_size, self._config.sample_rate_hz, 1, "float32",
            )
            await loop.run_in_executor(None, sd.wait)
            yield block.flatten()

    @property
    def sample_rate_hz(self) -> int:
        return self._config.sample_rate_hz
