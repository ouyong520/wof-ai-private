# WOF Python Launcher Foundation — Start Prompt

You own a fresh, independent productization lane for a future local WOF launcher. This lane must not modify or block the current Alpha RC5 bootstrap fix and must not interfere with WOF-052 collection.

Repository:
- `ouyong520/wof-ai-private`
- read-only reference as needed: `ouyong520/wof-winkawaks-bridge`

## Product intent

Long-term user experience should move toward one local launcher / packaged EXE rather than requiring Tampermonkey, manual Worker console selection, or pasted JavaScript.

Target architecture to investigate and prototype:

`Python/EXE Launcher -> Chrome/Edge CDP -> discover the live WOF page/Worker -> attach read-only bridge -> identify World 921031 -> expose connection/status UI`

The launcher should let the game create its native Worker normally. Do not replace `window.Worker`, do not rewrite the game Worker URL, and do not depend on the current broken Alpha bootstrap path.

## Scope for this foundation stage

Build only the launcher/control foundation:
- launch or attach to a Chromium browser through a supported debugging interface;
- discover WOF page targets and `gstyphoon*.js` Worker targets after the game has started normally;
- prove a post-start attachment path that does not block room entry;
- read-only inspect/evaluate the live Worker context;
- locate/confirm the game WASM module / heap using existing Browser knowledge where appropriate;
- expose a minimal local status UI/CLI showing at least: browser connected, WOF page found, WOF Worker found, module/heap found, supported build/identity status, read-only mode;
- design clean reconnect behavior for reload, room changes, Worker recreation, and browser restart;
- keep the game fully usable when the launcher cannot attach.

## Hard boundaries

Do NOT in this stage:
- modify `product/alpha/**`;
- modify current RC5 work;
- modify WOF-052 collectors;
- inject gameplay inputs;
- write WASM/game RAM;
- implement one-key moves / command injection;
- implement autoplay;
- change game speed;
- do Beta HUD work;
- expand attack research.

This stage is read-only foundation only.

## Safety / reliability invariants

- Base game must continue normally even if Python/CDP attachment fails.
- No RAM writes and no input injection.
- Do not attach by blindly selecting an arbitrary Worker; identify the WOF Worker robustly.
- Version/build checks must be explicit; reuse the authoritative Browser `wof / World 921031` evidence and golden SHA-256 only where the same logical bytes are actually being verified.
- Browser reload / Worker replacement must not leave stale control state.
- Prefer supported browser debugging APIs over Windows `ReadProcessMemory/WriteProcessMemory` against Chrome process memory.

## Deliverables

Create a new non-product area such as `parallel/PYLAUNCH/**` containing:
- architecture note;
- minimal runnable Python prototype;
- dependency/setup instructions for Windows;
- target/Worker discovery logic;
- read-only attachment/status proof;
- reconnect strategy;
- packaging plan toward a single EXE;
- a short result report that states exactly what is proven vs not yet proven.

Keep dependencies modest and explain why each one is needed.

## Human-operation goal

Minimize owner steps. Ideal first proof:
1. owner starts launcher;
2. launcher opens or attaches to browser;
3. owner enters WOF normally;
4. launcher automatically reports that the correct WOF page/Worker/module is connected;
5. no DevTools/Worker-console selection required.

If a browser debugging flag/profile setup is unavoidable, reduce it to one exact command or one launcher button.

## Stop condition

Stop only when either:

A. a read-only Python launcher prototype can automatically attach to an already normally-started WOF Browser session and identify the relevant page/Worker/module without interfering with room entry, leaving only one minimal owner Browser proof; or

B. the feasibility is reduced to one precise browser/platform limitation that requires a minimal owner observation.

Do not implement one-key moves yet. That becomes a separate post-foundation lane after the read-only launcher connection path is proven.
