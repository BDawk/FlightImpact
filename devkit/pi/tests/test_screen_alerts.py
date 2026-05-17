"""Auto-transition tests for ScreenService.

These exercise the live-state wireup: battery and required-component health
should drive the screen into LOW_BATTERY / SENSOR_OFFLINE and back, without
the API needing to call set_mode explicitly.

The render loop is not started — the alert logic runs synchronously when
state mutators are invoked, which is exactly what we want to assert on.
"""

from __future__ import annotations

import pytest

from flightimpact_devkit.config import ScreenConfig
from flightimpact_devkit.hal.st7789 import MockDisplay
from flightimpact_devkit.services.screen import ScreenService
from flightimpact_devkit.services.screen import service as screen_service_mod
from flightimpact_devkit.services.screen.state import ScreenMode, ShotMetrics


def _make_service() -> ScreenService:
    cfg = ScreenConfig(snapshot_dir="")
    return ScreenService(MockDisplay(cfg), cfg)


def _arm_post_boot(svc: ScreenService) -> None:
    """Get a fresh service into a post-boot state with all systems green.

    The alert evaluator deliberately stays dormant during BOOT/INITIALIZING
    so tests have to walk through those modes the way lifespan does.
    """
    svc.set_mode(ScreenMode.BOOT)
    svc.set_mode(ScreenMode.INITIALIZING)
    svc.update_health(camera_ok=True, radar_ok=True, api_ok=True, storage_ok=True)
    svc.set_mode(ScreenMode.HOME)


# --- Battery ----------------------------------------------------------------

def test_low_battery_triggers_when_pct_drops_below_threshold():
    svc = _make_service()
    _arm_post_boot(svc)
    assert svc.state.mode == ScreenMode.HOME

    svc.update_state(battery_pct=18)
    assert svc.state.mode == ScreenMode.LOW_BATTERY


def test_low_battery_recovers_above_hysteresis_only():
    svc = _make_service()
    _arm_post_boot(svc)
    svc.update_state(battery_pct=10)
    assert svc.state.mode == ScreenMode.LOW_BATTERY

    # Within hysteresis band — still showing the warning.
    svc.update_state(battery_pct=22)
    assert svc.state.mode == ScreenMode.LOW_BATTERY

    # Above the recovery threshold — returns to whatever was on before.
    svc.update_state(battery_pct=40)
    assert svc.state.mode == ScreenMode.HOME


def test_low_battery_skipped_during_boot():
    svc = _make_service()
    svc.set_mode(ScreenMode.BOOT)
    svc.update_state(battery_pct=5)
    # Alerts only arm after boot completes.
    assert svc.state.mode == ScreenMode.BOOT


# --- Sensor offline ---------------------------------------------------------

def test_camera_drop_flips_to_sensor_offline():
    svc = _make_service()
    _arm_post_boot(svc)

    svc.update_health(camera_ok=False)
    assert svc.state.mode == ScreenMode.SENSOR_OFFLINE


def test_recovery_returns_to_prior_mode():
    svc = _make_service()
    _arm_post_boot(svc)
    svc.update_health(radar_ok=False)
    assert svc.state.mode == ScreenMode.SENSOR_OFFLINE

    svc.update_health(radar_ok=True)
    assert svc.state.mode == ScreenMode.HOME


def test_battery_takes_precedence_over_sensor():
    """When both fire, LOW_BATTERY wins — power is the prerequisite."""
    svc = _make_service()
    _arm_post_boot(svc)
    svc.update_health(camera_ok=False)
    assert svc.state.mode == ScreenMode.SENSOR_OFFLINE

    svc.update_state(battery_pct=5)
    assert svc.state.mode == ScreenMode.LOW_BATTERY

    # Battery recovers; the sensor is still down so we land on SENSOR_OFFLINE.
    svc.update_state(battery_pct=80)
    assert svc.state.mode == ScreenMode.SENSOR_OFFLINE


# --- Capture / Result interplay --------------------------------------------

def test_alerts_dont_yank_capture():
    """A drop-out mid-capture should not pull the screen off CAPTURE."""
    svc = _make_service()
    _arm_post_boot(svc)
    svc.set_mode(ScreenMode.CAPTURE)

    svc.update_health(camera_ok=False)
    assert svc.state.mode == ScreenMode.CAPTURE


def test_alerts_dont_yank_fresh_result():
    """Fresh RESULT screen should stick around even if sensors drop —
    the auto-return timer will land us on HOME, and *then* the alert
    evaluator can take over."""
    svc = _make_service()
    _arm_post_boot(svc)
    shot = ShotMetrics(
        shot_id=1, ball_speed_mph=150.0, carry_yd=240,
        launch_deg=12.0, spin_rpm=2500, smash_factor=1.48,
        apex_yd=30, hang_s=6.0, side_yd=0.0,
    )
    svc.on_shot(shot)
    assert svc.state.mode == ScreenMode.RESULT

    svc.update_health(camera_ok=False)
    assert svc.state.mode == ScreenMode.RESULT


def test_result_auto_return_after_hold(monkeypatch):
    """`_maybe_auto_return_from_result` should flip RESULT → HOME after the
    hold budget. Drive time via a fake monotonic clock so the test is
    deterministic."""
    svc = _make_service()
    _arm_post_boot(svc)

    fake_now = {"t": 100.0}

    def fake_monotonic() -> float:
        return fake_now["t"]

    monkeypatch.setattr(screen_service_mod.time, "monotonic", fake_monotonic)

    shot = ShotMetrics(
        shot_id=2, ball_speed_mph=140.0, carry_yd=220,
        launch_deg=10.0, spin_rpm=2300, smash_factor=1.45,
        apex_yd=28, hang_s=5.8, side_yd=1.0,
    )
    svc.on_shot(shot)
    assert svc.state.mode == ScreenMode.RESULT

    # Hold timer should not fire yet.
    fake_now["t"] += screen_service_mod.RESULT_HOLD_SECONDS - 1
    svc._maybe_auto_return_from_result()
    assert svc.state.mode == ScreenMode.RESULT

    # Past the budget — should return to HOME.
    fake_now["t"] += 2
    svc._maybe_auto_return_from_result()
    assert svc.state.mode == ScreenMode.HOME


# --- Renderer registration --------------------------------------------------

def test_alert_modes_have_renderers():
    """If a mode is auto-selectable, it must have a renderer registered or
    the screen will fall back to home.render and the alert becomes invisible.
    """
    from flightimpact_devkit.services.screen.screens import RENDERERS

    assert ScreenMode.LOW_BATTERY in RENDERERS
    assert ScreenMode.SENSOR_OFFLINE in RENDERERS
