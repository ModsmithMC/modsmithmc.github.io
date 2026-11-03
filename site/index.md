# Modsmith

```{raw} html
<div class="hero">
  <picture>
    <source media="(max-width: 560px)" srcset="_static/hero-small.svg">
    <img src="_static/hero.svg" alt="">
  </picture>
  <div class="hero-copy">
    <h2>Modpacks for the official launcher</h2>
    <p>Install Minecraft modpacks, mods, resource packs and shaders from Modrinth and CurseForge. Modsmith prepares the files and adds an installation to the official launcher, where you choose it and play.</p>
    <div class="actions">
      <a class="button primary" href="https://modsmithmc.org/modsmith/get-started/installation/">Get Modsmith</a>
      <a class="button" href="https://github.com/ModsmithMC/modsmith">View on GitHub</a>
    </div>
  </div>
</div>

<div class="band">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">Install</p>
      <h2>A modpack in one command</h2>
      <p>Modsmith downloads the pack, its mod loader and Minecraft, then adds an installation with the pack's icon to the launcher. It shows what it will do first, and asks.</p>
    </div>
    <div>
```

```console
$ modsmith install fabulously-optimized --name fo
Install Fabulously Optimized 14.1.2 as fo
  + mods/sodium-fabric-0.9.2+mc26.2.jar
  + mods/iris-fabric-1.11.4+mc26.2.jar
  + and 100 more
102 to add; 45.0 MB to download.
Install it? [Y/n]:
```

```{raw} html
    </div>
  </div>
</div>

<div class="band alternate flip">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">Add</p>
      <h2>Add what you like</h2>
      <p>Add mods, resource packs and shaders to any instance. The mods they need come along, and go again when nothing needs them.</p>
    </div>
    <div>
```

```console
$ modsmith add fo jei
Add to fo
  + mods/mezz_config-26.2-fabric-0.6.10.jar
  + mods/jei-26.2-fabric-30.42.0.236.jar
    MezzConfig comes too, because a mod needs it
2 to add; 2.8 MB to download.
```

```{raw} html
    </div>
  </div>
</div>

<div class="band">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">Update</p>
      <h2>Updates that keep your changes</h2>
      <p>Update the pack and what you added, and read what changed in each release. Files you edited stay exactly as they are.</p>
    </div>
    <div class="changes">
      <p class="add"><b>added</b> mods/sodium.jar</p>
      <p class="update"><b>updated</b> mods/iris.jar</p>
      <p class="keep"><b>kept</b> config/options.toml <small>changed by you</small></p>
      <p class="remove"><b>removed</b> mods/old-mod.jar</p>
    </div>
  </div>
</div>

<div class="band alternate center">
  <div class="band-inner">
    <p class="eyebrow">Load</p>
    <h2>Every major mod loader</h2>
    <p class="lede">Modsmith installs the loader a pack needs, or the one you choose.</p>
    <div class="loaders">
      <div class="loader"><strong>Forge</strong><span>1.13.2 and later</span></div>
      <div class="loader"><strong>NeoForge</strong><span>1.20.1 and later</span></div>
      <div class="loader"><strong>Fabric</strong><span>1.14 and later</span></div>
      <div class="loader"><strong>Quilt</strong><span>1.14.4 and later</span></div>
    </div>
  </div>
</div>

<div class="band center">
  <div class="band-inner">
    <p class="eyebrow">Details</p>
    <h2>Made for players</h2>
    <p class="lede">The things that make a modded game easy to keep.</p>
    <div class="features">
      <div class="feature"><img src="_static/pixel/key.svg" alt=""><h3>No account</h3><p>Modsmith never signs in or starts the game. The official launcher does that.</p></div>
      <div class="feature"><img src="_static/pixel/list.svg" alt=""><h3>See it first</h3><p>Every change is shown before it happens, and waits for your yes.</p></div>
      <div class="feature"><img src="_static/pixel/link.svg" alt=""><h3>Bring your own</h3><p>Take over an installation you made in the launcher, mods and all.</p></div>
      <div class="feature"><img src="_static/pixel/download.svg" alt=""><h3>Blocked downloads</h3><p>CurseForge files you download by hand are found and checked.</p></div>
      <div class="feature"><img src="_static/pixel/check.svg" alt=""><h3>Your choices kept</h3><p>Optional files you picked stay picked when the pack updates.</p></div>
      <div class="feature"><img src="_static/pixel/shield.svg" alt=""><h3>Nothing half done</h3><p>A failed update leaves the instance as it was.</p></div>
    </div>
  </div>
</div>

<div class="band alternate flip">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">Build</p>
      <h2>Make your own tools</h2>
      <p>Everything Modsmith does comes from its Python library, which you can use to build your own installer, updater or launcher helper.</p>
      <div class="actions">
        <a class="button" href="https://modsmithmc.org/modsmith-python/">Read the library's guide</a>
      </div>
    </div>
    <div>
```

```python
import modsmith as ms

with ms.platforms.Modrinth("my-tool/1.0") as modrinth:
    project = modrinth.get_project("fabulously-optimized")
    release = next(modrinth.iter_releases(project))
    print(release.name)
```

```{raw} html
    </div>
  </div>
</div>

<div class="band center closing">
  <div class="band-inner">
    <h2>Get Modsmith</h2>
    <p class="lede">The command line works on Windows, macOS and Linux. A desktop app is on its way.</p>
    <div class="actions">
      <a class="button primary" href="https://modsmithmc.org/modsmith/get-started/installation/">Install the command line</a>
    </div>
  </div>
</div>
```
