# HB100 amplifier — breadboard build

The HB100 produces a tiny IF signal — typically a few hundred microvolts to
a few millivolts. Before any ADC can sample it usefully, it needs ~60–80 dB
of gain plus high-pass filtering to get rid of the DC bias.

## Two-stage topology

```
         +---------------+        +---------------+
HB100 IF─┤ Stage 1       ├────────┤ Stage 2       ├──→ Line out
         │ LM358         │        │ TL072         │     (to ADC / sound card)
         │ Gain ≈ 100×   │        │ Gain ≈ 50×    │
         │ HPF fc=20 Hz  │        │ LPF fc=8 kHz  │
         +---------------+        +---------------+
         total gain ≈ 5000× (74 dB)
         passband ≈ 20 Hz – 8 kHz
```

The HPF in stage 1 removes the DC offset and 1/f noise. The LPF in stage 2
brick-walls the band of interest — golf Doppler returns sit between roughly
200 Hz (slow club approach) and 5500 Hz (driver ball flight).

## Component values

Pick values for non-inverting amplifier topology:
- **Stage 1 (LM358)**: Rf = 100k, Ri = 1k → gain = 101
  - HPF: input cap 1 µF + 8.2k bias resistor → fc ≈ 20 Hz
- **Stage 2 (TL072)**: Rf = 47k, Ri = 1k → gain = 48
  - LPF: feedback cap 470 pF across Rf → fc ≈ 7.2 kHz

## Power

Run the amps on a 9V battery, not the Pi 5V rail. The Pi rail is full of
switching noise that ends up in your audio band as a constant ~kHz hum.
Use a 78L05 to derive 5V for the HB100 itself, but keep the op-amp rails
isolated.

## Grounding

Star-ground at the battery negative. The HB100 ground, both op-amp grounds,
the output cable shield, and the bias network all return to the same physical
node. Don't daisy-chain.

## Shielding

The 10.525 GHz radiation from the HB100 will couple back into your amplifier
inputs if they're long traces on a breadboard. Keep stage-1 input wires under
2 cm. Once the rig works, build it on a small piece of perf board with a
ground plane underneath — this is the single biggest noise reduction you can
make.

## What to expect

With no target moving, you should see ~50 mV peak-to-peak of broadband noise
on a scope at the output. Wave your hand a foot away from the HB100 and you
should see a ~500 mV burst at a few hundred Hz. If you don't, check:
- HB100 powered from 5V (not 9V — it'll work but get hot)
- Op-amp pin 1 wired correctly (the LM358 pinout is non-obvious — pin 1 is
  output A, not input A)
- Battery actually connected (yes, this is the most common failure mode)
