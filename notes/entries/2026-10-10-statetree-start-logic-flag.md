title: bStartAILogicOnPossess does not start a StateTree AI
date: 2026-10-10
tags: C++, AI, StateTree
summary: We set bStartAILogicOnPossess = true on a citizen's AI controller and the pawn still stood idle. The flag does nothing for a StateTree component; it has to be started by hand, and only once the pawn's data is ready.
---
Our citizens are spawned at runtime and should walk their daily schedule through a StateTree. With only `bStartAILogicOnPossess = true` set on the AI controller, a freshly spawned citizen just stood still. No error, no warning.

**The cause:** `bStartAILogicOnPossess` is a flag on `AAIController`. A `UStateTreeAIComponent` is a separate component the controller owns, and the flag does not reach it. The tree only runs once something calls `StateTreeAI->StartLogic()` directly.

**The second trap:** calling `StartLogic()` straight from `OnPossess` is still wrong for a pawn that was just spawned. The generator subsystem calls `SpawnActor`, which possesses the pawn and fires `OnPossess` immediately. Only after `SpawnActor` returns does the subsystem call `InitializeCitizen()`, which sets the pawn's appearance, schedule and traits. Starting the tree inside `OnPossess` would run it before that data exists.

**The fix:** gate the start on a ready flag, and let the function that finishes setting up the data be the one that starts the tree.

```cpp
// CitizenAIController.cpp
void ACitizenAIController::OnPossess(APawn* InPawn)
{
    Super::OnPossess(InPawn);
    const ACitizenCharacter* Citizen = Cast<ACitizenCharacter>(InPawn);
    if (Citizen && Citizen->bCitizenDataReady)
    {
        StartCitizenLogic();
    }
}

void ACitizenAIController::StartCitizenLogic()
{
    if (StateTreeAI && !StateTreeAI->IsRunning())
    {
        StateTreeAI->StartLogic();
    }
}
```

```cpp
// CitizenCharacter.cpp, end of InitializeCitizen()
bCitizenDataReady = true;
if (ACitizenAIController* AIC = Cast<ACitizenAIController>(GetController()))
{
    AIC->StartCitizenLogic();
}
```

On first spawn, `bCitizenDataReady` is still false when `OnPossess` runs, so the controller skips starting the tree. `InitializeCitizen()` sets the flag and starts the tree once the citizen's data is actually in. Later, if a player drops a citizen back to AI control, the data is already there, so `OnPossess` starts the tree right away.

**How to spot it:** if a StateTree pawn is possessed but idle, and `bStartAILogicOnPossess` is the only thing turned on, look for any call to `StartLogic()` on the `UStateTreeAIComponent` itself. If there is none, that is the whole bug.

**Rule:** for a `UStateTreeAIComponent`, call `StartLogic()` yourself, and only once the pawn's data is actually ready.
