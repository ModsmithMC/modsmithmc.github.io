(() => {
  const root = document.documentElement;

  document.querySelector("[data-theme-toggle]")?.addEventListener("click", () => {
    const dark =
      root.dataset.theme === "dark" ||
      (!root.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches);
    root.dataset.theme = dark ? "light" : "dark";
    try {
      localStorage.setItem("modsmith-theme", root.dataset.theme);
    } catch (error) {}
  });

  const menu = document.querySelector("[data-menu]");
  const sidebar = document.querySelector("[data-sidebar]");
  const isOpen = () => sidebar?.classList.contains("open") ?? false;
  const setOpen = (open) => {
    sidebar?.classList.toggle("open", open);
    menu?.setAttribute("aria-expanded", String(open));
  };
  menu?.addEventListener("click", () => setOpen(!isOpen()));
  document.addEventListener(
    "click",
    (event) => {
      if (!isOpen() || menu.contains(event.target)) return;
      if (sidebar.contains(event.target)) {
        if (event.target.closest("a")) setOpen(false);
        return;
      }
      if (!event.target.closest(".site-header")) {
        event.preventDefault();
        event.stopPropagation();
      }
      setOpen(false);
    },
    true,
  );

  const search = document.querySelector("[data-search]");
  document.addEventListener("keydown", (event) => {
    const typing = /^(INPUT|TEXTAREA)$/.test(document.activeElement?.tagName ?? "");
    if (event.key === "/" && !typing) {
      event.preventDefault();
      search?.focus();
    }
    if (event.key === "Escape" && isOpen()) {
      setOpen(false);
      menu.focus();
    }
  });

  // The site switcher in the header.
  const switcher = document.querySelector("[data-switch]");
  const switchButton = switcher?.querySelector("[data-switch-button]");
  const switchMenu = switcher?.querySelector("[data-switch-menu]");
  const setSwitch = (open) => {
    if (!switchMenu) return;
    switchMenu.hidden = !open;
    switchButton.setAttribute("aria-expanded", String(open));
  };
  switchButton?.addEventListener("click", () => setSwitch(switchMenu.hidden));
  document.addEventListener("click", (event) => {
    if (switcher && !switcher.contains(event.target)) setSwitch(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && switchMenu && !switchMenu.hidden) {
      setSwitch(false);
      switchButton.focus();
    }
  });

  // Tabs. Groups with the same choices switch together, and start on the
  // reader's system the first time.
  const system = /Windows/i.test(navigator.userAgent)
    ? "windows"
    : /Mac/i.test(navigator.userAgent)
      ? "macos"
      : "linux";
  let chosen = system;
  try {
    chosen = localStorage.getItem("modsmith-tab") ?? system;
  } catch (error) {}
  const groups = [...document.querySelectorAll("[data-tabs]")];
  const showTab = (name, remember) => {
    groups.forEach((group) => {
      const buttons = [...group.querySelectorAll("[data-tab]")];
      if (!buttons.some((button) => button.dataset.tab === name)) return;
      buttons.forEach((button) => button.setAttribute("aria-selected", String(button.dataset.tab === name)));
      group.querySelectorAll("[data-panel]").forEach((panel) => (panel.hidden = panel.dataset.panel !== name));
    });
    if (remember) {
      try {
        localStorage.setItem("modsmith-tab", name);
      } catch (error) {}
    }
  };
  groups.forEach((group) =>
    group.querySelectorAll("[data-tab]").forEach((button) =>
      button.addEventListener("click", () => showTab(button.dataset.tab, true)),
    ),
  );
  groups.forEach((group) => {
    const first = group.querySelector("[data-tab]")?.dataset.tab;
    const names = [...group.querySelectorAll("[data-tab]")].map((button) => button.dataset.tab);
    showTab(names.includes(chosen) ? chosen : first, false);
  });

  const languages = {
    python: "Python",
    bash: "Terminal",
    console: "Terminal",
    powershell: "PowerShell",
    pycon: "Python",
  };
  document.querySelectorAll("div.highlight").forEach((block) => {
    const name = block.parentElement.className.match(/highlight-(\w+)/)?.[1];
    const bar = document.createElement("div");
    bar.className = "code-bar";
    const label = document.createElement("span");
    label.textContent = languages[name] ?? "Code";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.textContent = "Copy";
    button.addEventListener("click", async () => {
      await navigator.clipboard.writeText(block.querySelector("pre").innerText);
      button.textContent = "Copied";
      setTimeout(() => (button.textContent = "Copy"), 1500);
    });
    bar.append(label, button);
    block.prepend(bar);
  });

  // Reference fields read as rows: name and type on the left, meaning on the right.
  document.querySelectorAll(".content dl.field-list > dt").forEach((label) => {
    // The signature already shows the return type.
    if (label.textContent.startsWith("Return type")) {
      label.nextElementSibling.remove();
      label.remove();
    }
  });
  document.querySelectorAll(".content dl.field-list > dd").forEach((field) => {
    const rows = field.querySelectorAll(":scope > ul > li > p, :scope > p");
    rows.forEach((row) => {
      const name = row.firstElementChild;
      const leading = row.firstChild === name;
      if (!leading || !name.matches("strong, a") || !row.textContent.includes("–")) return;
      const left = document.createElement("div");
      left.className = "field-name";
      const type = document.createElement("span");
      type.className = "field-type";
      const doc = document.createElement("div");
      doc.className = "field-doc";
      let target = type;
      [...row.childNodes].forEach((node) => {
        if (node === name) return left.append(node);
        const dash = node.nodeType === 3 ? node.textContent.indexOf("–") : -1;
        if (target === type && dash >= 0) {
          type.append(node.textContent.slice(0, dash));
          doc.append(node.textContent.slice(dash + 1).trimStart());
          target = doc;
        } else {
          target.append(node);
        }
      });
      type.textContent = type.textContent.replace(/^\s*\(|\)\s*$/g, "").trim() ? type.textContent : "";
      type.innerHTML = type.innerHTML.replace(/^\s*\(/, "").replace(/\)\s*$/, "");
      if (type.textContent) left.append(type);
      row.className = "field-row";
      row.replaceChildren(left, doc);
    });
  });

  // Reference entries in the table of contents show what kind of object they are.
  const kinds = { class: "class", exception: "exc", function: "func", method: "meth", attribute: "attr", property: "prop" };
  document.querySelectorAll(".site-toc a[href^='#']").forEach((link) => {
    const entry = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    const list = entry?.closest("dl.py");
    const kind = list && Object.keys(kinds).find((name) => list.classList.contains(name));
    if (kind) link.dataset.kind = kinds[kind];
  });

  // The page's table of contents follows the reader.
  const links = new Map();
  document.querySelectorAll(".site-toc a[href^='#']").forEach((link) => {
    const target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    if (target) links.set(target, link);
  });
  if (links.size) {
    const visible = new Set();
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) =>
          entry.isIntersecting ? visible.add(entry.target) : visible.delete(entry.target),
        );
        const first = [...links.keys()].find((target) => visible.has(target));
        if (!first) return;
        links.forEach((link) => link.classList.remove("active"));
        links.get(first).classList.add("active");
      },
      { rootMargin: "-70px 0px -70% 0px" },
    );
    links.forEach((_, target) => observer.observe(target));
  }

  const repo = document.querySelector("[data-repo]");
  const repoName = document.querySelector("[data-repo-name]");
  const facts = document.querySelector("[data-repo-facts]");
  const icons = {
    stars:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.7 5.8 6.3.8-4.6 4.3 1.2 6.2L12 17l-5.6 3.1 1.2-6.2L3 9.6l6.3-.8z"/></svg>',
    forks:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="5" r="2.5"/><circle cx="18" cy="5" r="2.5"/><circle cx="12" cy="19" r="2.5"/><path d="M6 7.5V10a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7.5M12 12v4.5"/></svg>',
  };
  const compact = (count) =>
    new Intl.NumberFormat("en", { notation: "compact" }).format(count);
  const show = ({ name, stars, forks }) => {
    if (name) repoName.textContent = name;
    facts.innerHTML =
      `<span title="Stars">${icons.stars}${compact(stars)}</span>` +
      `<span title="Forks">${icons.forks}${compact(forks)}</span>`;
  };
  // The sites share one origin, so each repository is cached on its own.
  const key = `modsmith-repo:${repo?.dataset.repo}`;
  const load = async () => {
    try {
      const cached = JSON.parse(sessionStorage.getItem(key) ?? "null");
      if (cached) return show(cached);
      const response = await fetch(`https://api.github.com/repos/${repo.dataset.repo}`);
      if (!response.ok) return;
      const data = await response.json();
      const summary = {
        name: data.full_name,
        stars: data.stargazers_count,
        forks: data.forks_count,
      };
      sessionStorage.setItem(key, JSON.stringify(summary));
      show(summary);
    } catch (error) {}
  };
  if (repo && repoName && facts) load();

  // Terminals type their command and show its output, over and over, while
  // they are on screen. A launcher drawing that follows a terminal shows the
  // installation it made. Readers who prefer less motion see the end at once.
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  document.querySelectorAll("[data-terminal]").forEach((terminal) => {
    const pre = terminal.querySelector("pre[data-command]");
    const typed = terminal.querySelector(".typed");
    const output = terminal.querySelector(".out");
    if (!pre || !typed || !output) return;
    const command = pre.dataset.command;
    const lines = output.innerHTML.split("\n");
    const launcher = terminal.id
      ? document.querySelector(`[data-follows="${terminal.id}"]`)
      : null;
    const status = launcher?.querySelector("[data-status]");
    const setLauncher = (state, text) => {
      if (!launcher) return;
      launcher.classList.toggle("added", state !== "empty");
      launcher.classList.toggle("playing", state === "playing");
      if (status) status.textContent = text;
    };
    if (still) {
      typed.textContent = command;
      output.innerHTML = lines.join("\n");
      terminal.classList.add("done");
      setLauncher("added", "");
      return;
    }
    let visible = false;
    let running = false;
    const play = async () => {
      running = true;
      while (visible) {
        terminal.classList.remove("done", "clearing");
        setLauncher("empty", "");
        typed.textContent = "";
        output.innerHTML = "";
        await sleep(500);
        for (let i = 1; i <= command.length; i += 1) {
          typed.textContent = command.slice(0, i);
          await sleep(38);
        }
        await sleep(450);
        for (let i = 0; i < lines.length; i += 1) {
          output.innerHTML = lines.slice(0, i + 1).join("\n");
          // A question waits a moment for its answer, as a player would.
          await sleep(/\[Y\/n\]/.test(lines[i]) ? 900 : 110);
        }
        terminal.classList.add("done");
        if (launcher) {
          await sleep(500);
          setLauncher("added", "A new installation, ready to play.");
          await sleep(1800);
          setLauncher("playing", "Starting Minecraft...");
          await sleep(1600);
        }
        await sleep(3500);
        terminal.classList.add("clearing");
        await sleep(500);
      }
      running = false;
    };
    new IntersectionObserver(
      (entries) => {
        visible = entries.some((entry) => entry.isIntersecting);
        if (visible && !running) play();
      },
      { threshold: 0.3 },
    ).observe(terminal);
  });
})();
