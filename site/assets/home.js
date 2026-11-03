// The home page's terminal types its command, then shows the output, once it
// scrolls into view. Readers who prefer less motion see it all at once.
(() => {
  const terminal = document.querySelector("[data-terminal]");
  const pre = terminal?.querySelector("pre");
  const typed = terminal?.querySelector(".typed");
  const output = terminal?.querySelector(".out");
  if (!terminal || !pre || !typed || !output) return;

  const command = pre.dataset.command;
  const lines = output.innerHTML.split("\n");
  const finish = () => {
    typed.textContent = command;
    output.innerHTML = lines.join("\n");
    terminal.classList.add("done");
  };
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    finish();
    return;
  }
  output.innerHTML = "";

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const play = async () => {
    for (let i = 1; i <= command.length; i += 1) {
      typed.textContent = command.slice(0, i);
      await wait(38);
    }
    await wait(450);
    for (let i = 0; i < lines.length; i += 1) {
      output.innerHTML = lines.slice(0, i + 1).join("\n");
      // The question waits a moment for its answer, as a player would.
      await wait(lines[i].includes("[Y/n]") ? 900 : 120);
    }
    terminal.classList.add("done");
  };

  const observer = new IntersectionObserver(
    (entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        observer.disconnect();
        play();
      }
    },
    { threshold: 0.4 },
  );
  observer.observe(terminal);
})();
