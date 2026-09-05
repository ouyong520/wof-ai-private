stageId: `<UPPER_SNAKE_CASE_STAGE_ID>`
dedupProtocol: `v2`
dedupKey: `<stable.logical-work-item>`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/<UPPER_SNAKE_CASE_STAGE_ID>_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/<UPPER_SNAKE_CASE_STAGE_ID>_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT <UPPER_SNAKE_CASE_STAGE_ID>`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/<DISPATCH_ID>.json`

# <Worker task title>

Repository: `ouyong520/wof-ai-private`

Read latest `main` first and treat this Git authority as the complete execution contract.

Terminal reporting must follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md` using the exact RESULT paths declared above.
