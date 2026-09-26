title: A world subsystem's OnWorldBeginPlay runs before any actor's BeginPlay
date: 2026-09-26
tags: C++, Actors, Subsystems
summary: A spawned citizen asked a world subsystem for its home building and got nothing back. The building had not registered yet, because registration lived in the wrong lifecycle function.
---
Citizens find their home and workplace through a small registry: each building type maps to a list of building actors. A citizen never scans the level for its target. It just asks the registry.

**The cause:** the registry lives on `UCitizenGeneratorSubsystem`, a `UWorldSubsystem`. That same subsystem spawns the citizens, from its `OnWorldBeginPlay`:

```cpp
void UCitizenGeneratorSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
    Super::OnWorldBeginPlay(InWorld);
    ...
    TArray<FInhabitantData> Data = GenerateCitizens(Config->CitizenCount, Seed, Config->CultureConfig);
    SpawnCitizens(Data, Config);
}
```

A world subsystem's `OnWorldBeginPlay` fires before `BeginPlay` runs on any actor placed in the level. Buildings normally set themselves up in `BeginPlay` — that is where actor setup usually goes. But if a building registered itself there, it would still be unregistered at the moment citizens spawn. The registry a fresh citizen queries would be empty, because no building's `BeginPlay` had run yet.

**The fix:** buildings register in `PostInitializeComponents` instead, which runs earlier, during actor construction, well before `OnWorldBeginPlay` fires for anyone:

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

Unregistering is symmetric, in `EndPlay`, which is unaffected by this ordering issue:

```cpp
void ACitizenBuilding::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UWorld* W = GetWorld())
    {
        if (UCitizenGeneratorSubsystem* Registry = W->GetSubsystem<UCitizenGeneratorSubsystem>())
        {
            Registry->UnregisterBuilding(this);
        }
    }
    Super::EndPlay(EndPlayReason);
}
```

The same function also applies the building's gameplay tags (`Home`, `Tavern`, `Market`, and so on), for the same reason: anything another system reads during or right after `OnWorldBeginPlay` has to be ready before `BeginPlay`, not during it.

**How to spot it:** if code inside or triggered by a `UWorldSubsystem::OnWorldBeginPlay` reads state from a placed actor and gets nothing on the first frame, check where that actor sets the state up. `BeginPlay` is too late for a world subsystem that acts during its own `OnWorldBeginPlay`.

**Rule:** anything a world subsystem's `OnWorldBeginPlay` depends on belongs in the depended-on actor's `PostInitializeComponents`, not its `BeginPlay`.
