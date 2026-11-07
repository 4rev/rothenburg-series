title: UE5: a world subsystem's OnWorldBeginPlay runs before every actor's BeginPlay
date: 2026-11-07
tags: C++, Subsystems, AI
summary: Our citizens' first daily task sometimes found no destination building, even though the building was right there. The subsystem that spawns them runs before any building has had its BeginPlay.
---
In our town, a world subsystem spawns every citizen and starts their AI the moment the level opens. Early on, a citizen's very first schedule task sometimes found no destination at all. The building was placed in the level and visible on screen. The lookup still returned nothing.

**The cause:** `UCitizenGeneratorSubsystem::OnWorldBeginPlay` generates citizens and calls `SpawnCitizens`, which spawns each `ACitizenCharacter` and calls `InitializeCitizen` on it directly, in the same call stack. `InitializeCitizen` starts the StateTree right away:

```cpp
bCitizenDataReady = true;
if (ACitizenAIController* AIC = Cast<ACitizenAIController>(GetController()))
{
    AIC->StartCitizenLogic();
}
```

The StateTree's first task, `FStateTreeMoveToScheduleTargetTask::EnterState`, calls `Schedule->FindNearestBuildingOfType(Entry.DestinationBuilding)`. That function reads a registry kept by the same subsystem, found with `World->GetSubsystem<UCitizenGeneratorSubsystem>()`.

So the whole chain runs inside one function call: world begin play, spawn, start logic, first schedule lookup. All of it happens before the engine calls `BeginPlay` on a single actor. `UWorld::BeginPlay()` calls every world subsystem's `OnWorldBeginPlay` first, then walks the level and calls each actor's `BeginPlay`. If a building only added itself to the registry inside its own `BeginPlay`, the registry would still be empty when the first citizen asked for a destination.

**The fix:** buildings register themselves earlier, in `PostInitializeComponents`, which runs during actor spawn, well before `OnWorldBeginPlay`:

```cpp
void ACitizenBuilding::PostInitializeComponents()
{
    Super::PostInitializeComponents();
    ApplyBuildingTags();
    GetComponents<UCitizenInteractionSlot>(CachedSlots);

    if (UWorld* W = GetWorld())
    {
        if (UCitizenGeneratorSubsystem* Registry = W->GetSubsystem<UCitizenGeneratorSubsystem>())
        {
            Registry->RegisterBuilding(this);
        }
    }
}
```

**How to spot it:** if a world subsystem reads, in its `OnWorldBeginPlay`, state that another actor sets up in its own `BeginPlay`, that state is not there yet. Not sometimes — every time. Trace the call stack from `OnWorldBeginPlay` down. If it reaches another actor's data without going through a later tick or event, that actor has not run `BeginPlay` yet.

**Rule:** anything a world subsystem needs at `OnWorldBeginPlay` time must be set up at actor construction or in `PostInitializeComponents`, never in `BeginPlay`.
