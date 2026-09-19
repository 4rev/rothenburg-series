title: SpawnActor ignores your location when the actor has no root component
date: 2026-08-23
tags: C++, Actors
summary: A tower appeared inside the wall ring at every Play and sank away. The cause was one SpawnActor call whose location was silently discarded.
---
At every Play in our demo map, a tower-shaped object appeared inside the wall ring. After a few seconds it sank out of sight. The wall itself was fine.

**What it was:** a shader warm-up. Before play starts, the game mode draws the collapse geometry once, 500 m under the map. That way the first real collapse does not stutter while its shaders compile. The code spawned a bare actor there (`WarmupDepthZ` is -50000):

```
AActor* Host = World->SpawnActor<AActor>(AActor::StaticClass(),
    FVector(0.0, 0.0, WarmupDepthZ), FRotator::ZeroRotator, Params);
```

**The trap:** a bare `AActor` has no root component when `SpawnActor` runs. An actor with no root has nowhere to store a transform, so the location you pass is thrown away. We created and registered the root after the spawn, with an identity transform. That put the actor at the world origin, which in our map is in the middle of the wall ring.

UE gives no warning or log line. The actor just appears at 0,0,0.

**The fix:** set the location again once a root exists.

```
USceneComponent* Root = NewObject<USceneComponent>(Host, TEXT("WarmupRoot"));
Root->SetMobility(EComponentMobility::Movable);
Host->SetRootComponent(Root);
Root->RegisterComponent();

// The spawn location above was discarded. Set it again now.
Host->SetActorLocation(FVector(0.0, 0.0, WarmupDepthZ));
```

**Rule:** if you spawn a class that builds its root at runtime (a bare `AActor`, or any actor without a default root), pass the location again after the root is registered.
