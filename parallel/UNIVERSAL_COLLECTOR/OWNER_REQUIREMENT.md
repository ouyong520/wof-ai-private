# Universal Collector Agent — Owner Requirement

The local Collector is a generic communication bridge between the Owner machine and Git.

Owner workflow:

```text
start CMD
-> fetch current Git collection request
-> show one concise Chinese instruction
-> press Enter once
-> stay running
-> collect through an installed supported adapter
-> upload new data to the destination named by the request
-> publish an exact manifest for AI
```

The local shell should not hard-code one research question. Git decides what supported data is needed next, which destination receives it, and which manifest AI should read.

The first adapter is Browser multi-room WOF collection. WinKawaks and other supported sources can use the same shell later.

After Enter, sources may appear, disappear, restart, increase or decrease without stopping other active sources.

CMD must print a copyable AI handoff line so the Owner does not need to explain context:

`AI联通：读取 collector/status/current.json`

When data is ready it prints:

`AI分析：读取 <exact manifest path>`

AI then reads that exact manifest and analyses the referenced new data.
