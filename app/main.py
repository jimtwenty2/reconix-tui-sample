import asyncio
import random

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical

from textual.widgets import (
    DataTable,
    Footer, 
    Input, 
    ProgressBar, 
    RichLog, 
    Static
)

BANNER = r"""
██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗██╗██╗  ██╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║██║╚██╗██╔╝
██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║██║ ╚███╔╝
██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║██║ ██╔██╗
██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║██║██╔╝ ██╗
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝
      recon · analysis · exploit   ::  cybersecurity-team@kshrd
"""

#Theme
PRIMARY = "#00E5FF"     # success, open ports, progress, focus
BACKGROUND = "#000000"  # app background
SECONDARY = "#7C3AED"   # prompt, headers, warnings, badges

class ReconixApp(App):
    CSS = f"""
    Screen {{ background: {BACKGROUND}; }}
    #banner {{ color: {PRIMARY}; padding: 0 1; }}
    #body {{ height: 1fr; }}
    #left {{ width: 2fr; }}
    #right {{ width: 3fr; }}
    Input {{ border: tall {SECONDARY}; background: {BACKGROUND}; }}
    Input:focus {{ border: tall {PRIMARY}; }}
    RichLog {{ border: round {SECONDARY}; height: 1fr; background: {BACKGROUND}; }}
    DataTable {{ border: round {SECONDARY}; height: 1fr; background: {BACKGROUND}; }}
    ProgressBar {{ padding: 0 1; }}
    Bar > .bar--bar {{ color: {PRIMARY}; }}
    .section {{ color: {SECONDARY}; text-style: bold; padding: 0 1; }}
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear_log", "Clear log"),
    ]

    def compose(self) -> ComposeResult:
        """Build the widget tree — this is the 'view'."""
        yield Static(BANNER, id="banner")
        yield Input(placeholder="target, e.g. example.com   (enter to scan)", id="target")
        with Horizontal(id="body"):
            with Vertical(id="left"):
                yield Static("ACTIVITY", classes="section")
                yield RichLog(id="log", highlight=False, markup=True)
            with Vertical(id="right"):
                yield Static("HOSTS", classes="section")
                yield DataTable(id="hosts")
        yield ProgressBar(id="prog", total=100, show_eta=False)
        yield Footer()
 
    def on_mount(self) -> None:
        table = self.query_one("#hosts", DataTable)
        table.add_columns("HOST", "ADDRESS", "CODE", "TECH")
        self.query_one("#log", RichLog).write(
            f"[{SECONDARY}]Reconix ready.[/] Type a target and press enter."
        )
        self.query_one("#target", Input).focus()
 
    # --- Input handler: enter launches the worker ---
    def on_input_submitted(self, event: Input.Submitted) -> None:
        target = event.value.strip()
        if target:
            # run_exclusive cancels any in-flight scan before starting a new one
            self.run_scan(target)
 
    def action_clear_log(self) -> None:
        self.query_one("#log", RichLog).clear()
        self.query_one("#hosts", DataTable).clear()
 
    # --- The worker: runs OFF the event loop so the UI stays responsive -----
    # @work(exclusive=True) via the decorator below. It streams results back by
    # calling widget methods on the app (Textual marshals these safely).
    from textual import work  # local import keeps the skeleton self-contained
 
    @work(exclusive=True)
    async def run_scan(self, target: str) -> None:
        log = self.query_one("#log", RichLog)
        table = self.query_one("#hosts", DataTable)
        prog = self.query_one("#prog", ProgressBar)
 
        table.clear()
        prog.update(total=100, progress=0)
        log.write(f"[{PRIMARY}][*][/] scanning [b]{target}[/] ...")
 
        # ===================================================================
        # SIMULATED scan. Replace everything below with real phases:
        #   dns -> subdomains -> port scan -> fingerprint, each streaming
        #   results back via log.write(...) and table.add_row(...).
        # Bound concurrency with an asyncio.Semaphore and add timeouts/cancel.
        # ===================================================================
        fake_hosts = [
            ("www", "93.184.215.14", "200", "nginx"),
            ("api", "93.184.215.20", "200", "express · node"),
            ("dev", "10.0.4.12", "403", "internal host"),
            ("mail", "93.184.215.31", "200", "postfix"),
            ("staging", "93.184.215.44", "301", "→ /login"),
        ]
        for i, (sub, addr, code, tech) in enumerate(fake_hosts, start=1):
            await asyncio.sleep(random.uniform(0.3, 0.8))  # pretend work
            host = f"{sub}.{target}"
            colour = PRIMARY if code == "200" else SECONDARY
            log.write(f"[{PRIMARY}][+][/] {host:<28} [{colour}]{code}[/]  {tech}")
            table.add_row(host, addr, code, tech)
            prog.update(progress=int(i / len(fake_hosts) * 100))
 
        log.write(f"[{PRIMARY}][✓][/] scan complete — {len(fake_hosts)} hosts")
 
 
def main():
    ReconixApp().run()