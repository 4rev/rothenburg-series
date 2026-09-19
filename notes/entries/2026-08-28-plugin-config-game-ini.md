title: A plugin's DefaultGame.ini does not change the project's cook list. Config/Game.ini does.
date: 2026-08-28
tags: Plugins, Packaging, Config
summary: Our plugin shipped a cook list that Unreal never read. The file name decides whether plugin config changes the host project.
---
Our plugin loads a few assets by string, with `LoadObject<>(nullptr, TEXT("/WallSystem/..."))`. The cooker cannot see string paths, so those assets never get cooked. It works in PIE and fails silently in a packaged game: no cannon sound, no smoke.

The normal fix is `DirectoriesToAlwaysCook`. We put it in the plugin's `Config/DefaultGame.ini`. It shipped, it looked right, and it did nothing.

**Why:** Unreal reads plugin config files through two different paths, and the file name picks the path.

| File in the plugin | What it does |
|---|---|
| `Config/DefaultGame.ini` | The plugin's own private config. It does **not** change the project's `ProjectPackagingSettings`. |
| `Config/Game.ini` | **Merges into the host project's config.** This is the one that reaches the cook. |

You can see this in `ConfigHierarchy.h` (plugin layers vs. plugin modification layers). The same rule applies to other types, for example `Config/Engine.ini` for navigation settings.

**The fix:** rename the file to `Config/Game.ini`, and list it in `FilterPlugin.ini` so it ships in the package.

```
[/Script/UnrealEd.ProjectPackagingSettings]
+DirectoriesToAlwaysCook=(Path="/WallSystem/WallSystem/Sound_FX/CannonFire")
+DirectoriesToAlwaysCook=(Path="/WallSystem/WallSystem/Blueprints/Falconet/FX")
```

**How we proved it:** we did not trust the file. We read the live settings object in the editor with Python: `get_editor_property("DirectoriesToAlwaysCook")` on the `ProjectPackagingSettings` default object. It returned all 13 plugin directories, in a project whose own ini listed only 6.

**The lesson:** a shipped config file that nobody reads looks exactly like a fixed bug. Check the effect, not the file.
