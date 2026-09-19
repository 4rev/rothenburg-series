title: UE 5.5+: CellSize and AgentMaxStepHeight in the ini do nothing
date: 2026-08-03
tags: Navigation, Config
summary: The flat RecastNavMesh ini keys are deprecated and silently ignored. Our wall stairs had navmesh holes until we set NavMeshResolutionParams instead.
---
Our AI guards kept getting stuck on the wall stairs. The navmesh had holes on the steps. We had already set a fine `CellSize` and a high `AgentMaxStepHeight` in `DefaultEngine.ini`. The numbers looked right, and they changed nothing.

**The reason:** since UE 5.5, these keys under `[/Script/NavigationSystem.RecastNavMesh]` are deprecated:

- `CellSize`
- `CellHeight`
- `AgentMaxStepHeight`

The navmesh generator does not read them any more. It reads `NavMeshResolutionParams[]`, one entry per resolution (Low, Default, High). Nothing warns you that the old keys are ignored.

**The fix:** set all three resolutions. A tile picks its resolution on its own, so if you fix only one, the holes just move somewhere else.

```
NavMeshResolutionParams[0]=(CellSize=10.000000,CellHeight=5.000000,AgentMaxStepHeight=45.000000)
NavMeshResolutionParams[1]=(CellSize=10.000000,CellHeight=5.000000,AgentMaxStepHeight=45.000000)
NavMeshResolutionParams[2]=(CellSize=10.000000,CellHeight=5.000000,AgentMaxStepHeight=45.000000)
```

The struct defaults are CellSize 25, CellHeight 10, AgentMaxStepHeight 35. `AgentRadius`, `AgentHeight`, `AgentMaxSlope` and `RuntimeGeneration` are not per-resolution. They stay as flat keys.

**How to spot it:** on every nav build the log prints a line like `AgentMaxStepHeight (35.000000) for resolution Low is not high enough`. If you set a higher value and still see 35, your setting is not being read.

In our demo this was the biggest single win for AI on stairs. It mattered more than any code change.
