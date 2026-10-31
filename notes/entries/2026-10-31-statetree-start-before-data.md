title: bStartAILogicOnPossess can start a StateTree before the pawn has real data
date: 2026-10-31
tags: C++, AI, StateTree
summary: Our citizen AI controller sets bStartAILogicOnPossess true, the normal way to auto-start AI logic. For a freshly spawned pawn, that flag alone starts the tree before the pawn's own init step has run.
---
Each citizen in our game gets an `ACitizenAIController` on spawn. The constructor sets `bStartAILogicOnPossess = true` - the usual way to make an AI controller start its logic as soon as it possesses a pawn.

**The cause:** `OnPossess` fires as soon as the controller takes the pawn. But the citizen's real data - occupation, traits, and the weekly schedule it should follow - is set afterwards, in a separate call: `ACitizenCharacter::InitializeCitizen()`, run by `UCitizenGeneratorSubsystem::SpawnCitizens()` right after it spawns and possesses the pawn. Until `InitializeCitizen` runs, the citizen's `SeasonalSchedule` array is empty. If the StateTree starts in `OnPossess`, it starts against that empty data. `bStartAILogicOnPossess` only tells the engine to start AI logic on possession - it gives no guarantee that the pawn's own setup has finished first.

**The fix:** gate the start behind a readiness flag, and call it from two places.

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

On first spawn, `OnPossess` runs before `bCitizenDataReady` is true, so it does not start the tree. `InitializeCitizen` starts it instead, once the schedule and traits are set. On re-possession - the player drops a citizen and the AI takes it back - `bCitizenDataReady` is already true, so `OnPossess` starts it directly, and `InitializeCitizen` is not called again.

**How to spot it:** check which call sets up a pawn's own data after `Possess()` runs. If your controller starts AI logic straight from `OnPossess`, and your pawn still has an init step like `InitializeCitizen` that runs after spawn, the tree can start before that step has run - with whatever the data members default to.

**The rule:** `bStartAILogicOnPossess` only means "start on possession." If your pawn needs its own init step after being possessed, do not rely on the flag alone - gate the actual start on a readiness flag your init step sets, and call `StartLogic` from there.
