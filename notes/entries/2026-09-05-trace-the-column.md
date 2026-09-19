title: A ground trace from above finds the arch, not the ground
date: 2026-09-05
tags: C++, Collision, Splines
summary: Our generated path climbed over ruined arches. One downward trace returns whatever hangs over the point. The fix traces the whole column and chooses.
---
The plugin lays a footpath outside the wall and snaps each point to the ground. Next to ruined sections, the path climbed up and ran over the top of the ruin arches.

**The cause:** each point used one `LineTraceSingleByChannel` that started 50 m up and went down. A single trace returns the first surface it hits. From 50 m up, that is whatever hangs over the point. Here it was the top of an arch.

**An ignore list does not fix it.** We already ignored the wall and its decorations. But a ruin placed by hand, a roof eave or a tree is never on the list. An ignore list is always incomplete.

**The second trap:** `LineTraceMultiByChannel` does not give you the column either. It also stops at the first **blocking** hit. The extra hits it returns are only overlaps. The arch and the ground both block, so the "multi" trace returned just the arch again.

**What works:** an object-type query. `LineTraceMultiByObjectType` has no block/overlap rules, so it returns every surface of the object types you ask for (we use `WorldStatic` and `WorldDynamic`). Then choose with two rules:

1. Take the highest surface that is not more than `MaxGroundRise` (150 cm) above the wall's own height at that spot. This skips an arch overhead.
2. If nothing passes, take the lowest surface in the column.

Setting the knob to 0 brings back the old "topmost hit" behaviour.

**How we checked it:** we built a test rig with a floor at Z=0 and a slab 400–500 cm above it, with the path running under it. With the new rule, every path tile sat at Z=0, under the slab.
