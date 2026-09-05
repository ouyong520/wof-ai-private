(() => {
  "use strict";

  const API_SCHEMA = "wof-native-marker-renderer-submit-source-trace-v1";
  const SOURCE_SCHEMA = "wof-native-marker-renderer-submit-source-v1";
  const EVENT_SCHEMA = "wof-native-marker-renderer-submit-event-v1";
  const BLOCKER = "NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN";
  const MAX_EVENTS = 96;
  const MAX_WALL_MS = 15000;
  const ALLOWED_DERIVATIONS = new Set([
    "SOURCE_TRACED_POINTER",
    "DIRECT_RENDER_HOOK",
    "EXPORTED_RENDERER_POINTER",
  ]);

  const SAFETY = Object.freeze({
    readOnly: true,
    ramWrites: 0,
    inputInjection: false,
    ownerSelectionRequired: false,
    manualSeedRequired: false,
  });

  const clone = (value) => {
    if (typeof structuredClone === "function") {
      try { return structuredClone(value); } catch (_) {}
    }
    return JSON.parse(JSON.stringify(value));
  };

  const nonempty = (value) => typeof value === "string" && value.trim().length > 0;

  const bindingValid = (binding) =>
    binding && typeof binding === "object" &&
    nonempty(binding.runtimeEpoch) &&
    nonempty(binding.rendererEpoch) &&
    nonempty(binding.authorityKey);

  const sourceErrors = (source) => {
    if (!source || typeof source !== "object") return ["DIRECT_SOURCE_MISSING"];
    const errors = [];
    if (source.schema !== SOURCE_SCHEMA) errors.push("DIRECT_SOURCE_SCHEMA_INVALID");
    if (!ALLOWED_DERIVATIONS.has(source.derivationKind)) errors.push("DIRECT_SOURCE_DERIVATION_UNQUALIFIED");
    if (source.guessed !== false) errors.push("DIRECT_SOURCE_GUESSED_OR_UNSPECIFIED");
    if (source.displayedFrameCausalLink !== true) errors.push("DISPLAYED_FRAME_CAUSAL_LINK_MISSING");
    if (source.coordinateAuthority !== "NATIVE_RENDERER_OBJECT_384X224") errors.push("NATIVE_COORDINATE_AUTHORITY_MISSING");
    for (const field of [
      "screenshotCoordinatesUsed",
      "ocrCoordinatesUsed",
      "templateCoordinatesUsed",
      "worldProjectionCoordinatesUsed",
    ]) {
      if (source[field] !== false) errors.push(`${field.toUpperCase()}_FORBIDDEN`);
    }
    if (!Array.isArray(source.sourceTrace) || source.sourceTrace.length < 2 ||
        source.sourceTrace.some((item) => !nonempty(item))) {
      errors.push("SOURCE_TRACE_INCOMPLETE");
    }
    if (!nonempty(source.instrumentationId)) errors.push("DIRECT_SOURCE_INSTRUMENTATIONID_MISSING");
    if (!nonempty(source.hookSite)) errors.push("DIRECT_SOURCE_HOOKSITE_MISSING");
    if (source.readOnly !== true || source.ramWrites !== 0 || source.inputInjection !== false) {
      errors.push("DIRECT_SOURCE_SAFETY_BOUNDARY_INVALID");
    }
    if (source.ownerSelectionRequired !== false) errors.push("OWNER_SELECTION_FORBIDDEN");
    if (source.manualSeedRequired !== false) errors.push("MANUAL_SEED_FORBIDDEN");
    if (typeof source.subscribe !== "function") errors.push("DIRECT_SOURCE_SUBSCRIBE_HOOK_MISSING");
    return errors;
  };

  let state = null;

  const blank = () => ({
    schema: API_SCHEMA,
    state: "IDLE",
    blocker: BLOCKER,
    reason: "NOT_STARTED",
    binding: null,
    source: null,
    events: [],
    rejectedEvents: 0,
    sourceSurface: null,
    terminal: false,
    bounded: { maxEvents: MAX_EVENTS, maxWallMs: MAX_WALL_MS },
    ...SAFETY,
  });

  const stopSubscription = () => {
    if (!state) return;
    const stop = state._unsubscribe;
    state._unsubscribe = null;
    if (typeof stop === "function") {
      try { stop(); } catch (_) {}
    } else if (stop && typeof stop.stop === "function") {
      try { stop.stop(); } catch (_) {}
    } else if (stop && typeof stop.unsubscribe === "function") {
      try { stop.unsubscribe(); } catch (_) {}
    }
    if (state._timer != null) {
      try { clearTimeout(state._timer); } catch (_) {}
      state._timer = null;
    }
  };

  const seal = (reason = "BOUNDED_CAPTURE_SEALED") => {
    if (!state) return blank();
    if (!state.terminal) {
      stopSubscription();
      state.terminal = true;
      state.state = state.events.length ? "CAPTURE_READY" : "SOURCE_OBSERVED_NO_DIRECT_EVENTS";
      state.reason = reason;
      state.blocker = state.events.length ? null : BLOCKER;
    }
    return status();
  };

  const eventBindingMatches = (event, binding) =>
    event.runtimeEpoch === binding.runtimeEpoch &&
    event.rendererEpoch === binding.rendererEpoch &&
    event.authorityKey === binding.authorityKey;

  const acceptEvent = (incoming) => {
    if (!state || state.terminal) return false;
    const event = clone(incoming);
    if (!event || typeof event !== "object" || event.schema !== EVENT_SCHEMA) {
      state.rejectedEvents += 1;
      state.terminal = true;
      state.state = "REJECTED";
      state.reason = "DIRECT_RENDERER_SUBMIT_EVENT_SCHEMA_INVALID";
      state.blocker = BLOCKER;
      stopSubscription();
      return false;
    }
    if (!eventBindingMatches(event, state.binding)) {
      state.rejectedEvents += 1;
      state.terminal = true;
      state.state = "REJECTED";
      state.reason = "STALE_OR_MIXED_AUTHORITY_BINDING";
      state.blocker = BLOCKER;
      stopSubscription();
      return false;
    }
    if (event.displayedFrameCausalLink !== true ||
        event.coordinateAuthority !== "NATIVE_RENDERER_OBJECT_384X224" ||
        event.guessed !== false) {
      state.rejectedEvents += 1;
      state.terminal = true;
      state.state = "REJECTED";
      state.reason = "DIRECT_RENDERER_SUBMIT_EVENT_CAUSAL_CONTRACT_INVALID";
      state.blocker = BLOCKER;
      stopSubscription();
      return false;
    }
    state.events.push(event);
    if (state.events.length >= MAX_EVENTS) seal("BOUNDED_EVENT_LIMIT_REACHED");
    return true;
  };

  const surfaceCandidates = () => {
    const roots = [
      ["self", globalThis],
      ["self.Module", globalThis.Module],
      ["self.Module.asm", globalThis.Module && globalThis.Module.asm],
    ];
    const out = [];
    for (const [rootName, root] of roots) {
      if (!root || typeof root !== "object") continue;
      for (const key of [
        "__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__",
        "WOFNativeMarkerRendererSubmitSourceV1",
      ]) {
        let value = null;
        try { value = root[key]; } catch (_) {}
        if (value && typeof value === "object") out.push({ path: `${rootName}.${key}`, value });
      }
    }
    return out;
  };

  const sourceIdentity = (candidate) => {
    const source = candidate.value;
    return JSON.stringify([
      source.schema,
      source.derivationKind,
      source.instrumentationId,
      source.hookSite,
      source.sourceTrace,
    ]);
  };

  const discoverSource = () => {
    const candidates = surfaceCandidates()
      .map((candidate) => ({ ...candidate, errors: sourceErrors(candidate.value) }))
      .filter((candidate) => candidate.errors.length === 0);
    const unique = new Map();
    for (const candidate of candidates) unique.set(sourceIdentity(candidate), candidate);
    const values = [...unique.values()];
    if (values.length === 0) {
      return { ok: false, reason: "EXACT_DIRECT_RENDERER_SOURCE_SURFACE_NOT_EXPOSED", candidate: null };
    }
    if (values.length !== 1) {
      return { ok: false, reason: "AMBIGUOUS_DIRECT_RENDERER_SOURCE_SURFACE", candidate: null };
    }
    return { ok: true, reason: null, candidate: values[0] };
  };

  function start(binding) {
    stop();
    state = blank();
    if (!bindingValid(binding)) {
      state.state = "REJECTED";
      state.reason = "EXPECTED_BINDING_INVALID";
      state.terminal = true;
      return status();
    }
    state.binding = {
      runtimeEpoch: binding.runtimeEpoch,
      rendererEpoch: binding.rendererEpoch,
      authorityKey: binding.authorityKey,
    };

    const discovered = discoverSource();
    if (!discovered.ok) {
      state.state = "BLOCKED";
      state.reason = discovered.reason;
      state.blocker = BLOCKER;
      state.terminal = true;
      return status();
    }

    const candidate = discovered.candidate;
    state.sourceSurface = candidate.path;
    state.source = clone({
      schema: candidate.value.schema,
      derivationKind: candidate.value.derivationKind,
      guessed: candidate.value.guessed,
      displayedFrameCausalLink: candidate.value.displayedFrameCausalLink,
      coordinateAuthority: candidate.value.coordinateAuthority,
      screenshotCoordinatesUsed: candidate.value.screenshotCoordinatesUsed,
      ocrCoordinatesUsed: candidate.value.ocrCoordinatesUsed,
      templateCoordinatesUsed: candidate.value.templateCoordinatesUsed,
      worldProjectionCoordinatesUsed: candidate.value.worldProjectionCoordinatesUsed,
      sourceTrace: candidate.value.sourceTrace,
      instrumentationId: candidate.value.instrumentationId,
      hookSite: candidate.value.hookSite,
      readOnly: candidate.value.readOnly,
      ramWrites: candidate.value.ramWrites,
      inputInjection: candidate.value.inputInjection,
      ownerSelectionRequired: candidate.value.ownerSelectionRequired,
      manualSeedRequired: candidate.value.manualSeedRequired,
    });

    try {
      const subscription = candidate.value.subscribe(acceptEvent, clone(state.binding));
      state._unsubscribe = subscription;
      if (state.terminal) stopSubscription();
    } catch (error) {
      state.state = "BLOCKED";
      state.reason = "DIRECT_RENDERER_SOURCE_SUBSCRIBE_FAILED";
      state.blocker = BLOCKER;
      state.terminal = true;
      state.subscribeError = String(error && error.message ? error.message : error);
      stopSubscription();
      return status();
    }
    state.state = "OBSERVING";
    state.reason = "EXACT_DIRECT_RENDERER_SOURCE_OBSERVER_ACTIVE";
    state.blocker = null;
    state._timer = setTimeout(() => {
      if (state && !state.terminal) seal("BOUNDED_WALL_LIMIT_REACHED");
    }, MAX_WALL_MS);
    return status();
  }

  function status() {
    const s = state || blank();
    return clone({
      schema: API_SCHEMA,
      state: s.state,
      blocker: s.blocker,
      reason: s.reason,
      binding: s.binding,
      sourceSurface: s.sourceSurface,
      eventCount: s.events.length,
      rejectedEvents: s.rejectedEvents,
      terminal: s.terminal,
      bounded: s.bounded,
      subscribeError: s.subscribeError || null,
      ...SAFETY,
    });
  }

  function result() {
    const s = state || blank();
    return clone({
      schema: API_SCHEMA,
      state: s.state,
      blocker: s.blocker,
      reason: s.reason,
      runtimeEpoch: s.binding && s.binding.runtimeEpoch,
      rendererEpoch: s.binding && s.binding.rendererEpoch,
      authorityKey: s.binding && s.binding.authorityKey,
      source: s.source,
      sourceSurface: s.sourceSurface,
      events: s.events,
      rejectedEvents: s.rejectedEvents,
      terminal: s.terminal,
      bounded: s.bounded,
      ...SAFETY,
    });
  }

  function stop(reason = "STOPPED") {
    if (state) {
      stopSubscription();
      if (!state.terminal) {
        state.terminal = true;
        state.state = "STOPPED";
        state.reason = reason;
        state.blocker = BLOCKER;
      }
    }
    return status();
  }

  globalThis.WOFNATIVEMARKERSUBMITSOURCETRACEV1 = Object.freeze({
    schema: API_SCHEMA,
    start,
    status,
    result,
    seal,
    stop,
  });
})();
