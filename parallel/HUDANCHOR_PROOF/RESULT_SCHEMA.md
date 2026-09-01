# HUD Anchor Proof Result Schema

The Top-page probe returns one object.

## Terminal verdict

Successful proof:

```json
{
  "verdict": "IMPLEMENTATION_READY"
}
```

Any missing or disproved component fails closed:

```json
{
  "verdict": "FAILED_COMPONENT:<component>"
}
```

Representative components:

- `worker_bridge`
- `calibration`
- `camera`
- `camera_scroll_coverage`
- `depth_coverage`
- `jump_coverage`
- `x_camera_transform`
- `depth_y`
- `jump_z`
- `drawing_buffer`
- `resize_fullscreen`
- `p2p3_reuse`
- `above_character_clearance`
- `visual_confirmation`

## Success object

On `IMPLEMENTATION_READY`, `projection` contains the frozen implementation inputs:

```json
{
  "version": "wof-hudanchor-browser-proof-v1",
  "verdict": "IMPLEMENTATION_READY",
  "operatorDecision": "PASS_MINUS",
  "projection": {
    "camera": {
      "address": "0xFF....",
      "read": "u16be"
    },
    "native": {
      "width": 384,
      "height": 224,
      "xFormula": "worldX-camera+xBias",
      "xBias": 0,
      "yModel": "Y-Z",
      "yFormula": "worldY-z+yBias",
      "yBias": 0,
      "aboveCharacterOffsetNative": 0,
      "aboveCharacterOffsetMeaning": "logical constant from raw player floor/Z reference to chosen warning anchor; not sprite-height claim"
    },
    "drawingBuffer": {
      "source": "live WebGL VIEWPORT",
      "formula": "xDb=vp.x+nativeX/384*vp.width; yDb=vp.top+nativeY/224*vp.height",
      "viewportYConversion": "vp.top=dbHeight-(vp.y+vp.height)"
    }
  }
}
```

`PASS_PLUS` freezes `Y+Z`; `PASS_NONE` freezes `Y`.

## Evidence

The object also records:

- selected/ranked camera candidates and quality;
- calibration point in native coordinates;
- P1 world-X, floor-Y, Z and camera excursion ranges after calibration;
- Worker sample counts;
- direct-WebGL hook and marker draw counts;
- live WebGL viewport/drawing-buffer dimensions;
- baseline/current resize/fullscreen/DPR layout snapshots;
- observed layout changes and recovery;
- P1/P2/P3 focus time when extra players are live;
- an objective checklist used to gate PASS.

## Objective PASS gates

A PASS button is disabled until all observable required evidence is present:

- fresh Worker bridge;
- camera candidate had passed the bounded quality gate at calibration and remains locked;
- horizontal movement plus real camera excursion;
- floor/depth excursion;
- jump/Z excursion;
- direct WebGL marker draws with valid viewport;
- at least one resize/fullscreen/DPR/layout change followed by stable remapping;
- P2/P3 focus check when those players are live.

The final human input is only the visual classification of whether a candidate remains stably attached. The tool never turns insufficient objective coverage into success.

## Safety boundary fields

Every result includes:

```json
{
  "boundaries": {
    "alphaModified": false,
    "pixelTrackingUsed": false,
    "combatRequired": false
  }
}
```
