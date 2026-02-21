#!/usr/bin/env python3
"""Team Fortress 2 themed OS simulator (CLI)."""

from __future__ import annotations

import random
import textwrap
from dataclasses import dataclass, field


@dataclass
class SystemState:
    health: int = 100
    ammo: int = 120
    metal: int = 200
    enemy_wave: int = 1
    logs: list[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        self.logs.append(message)
        if len(self.logs) > 8:
            self.logs.pop(0)


CLASSES = {
    "Scout": "Fast process scheduler. Boosts thread speed, low armor.",
    "Soldier": "Heavy service launcher. High impact, moderate startup time.",
    "Pyro": "Firewall sanitizer. Burns suspicious packets.",
    "Demoman": "Exploit detonator. Great area denial against malware.",
    "Heavy": "Resource tank. High stability, lower mobility.",
    "Engineer": "Kernel builder. Repairs turrets and allocates metal.",
    "Medic": "Recovery daemon. Restores health over time.",
    "Sniper": "Precision debugger. Eliminates remote threats.",
    "Spy": "Stealth intrusion tester. Backstabs hidden vulnerabilities.",
}


def banner() -> str:
    return textwrap.dedent(
        """
         ================================================
            TEAM FORTRESS 2 :: OS SIMULATOR v1.0
         ================================================
        """
    ).strip("\n")


def print_status(state: SystemState) -> None:
    print("\n--- CORE STATUS ---")
    print(f"Integrity (HP): {state.health}%")
    print(f"Ammo Cache:     {state.ammo}")
    print(f"Metal Pool:     {state.metal}")
    print(f"Threat Wave:    {state.enemy_wave}")
    if state.logs:
        print("\nRecent Logs:")
        for line in state.logs:
            print(f" - {line}")


def deploy_class(state: SystemState) -> None:
    print("\nSelect a class module:")
    for idx, (name, desc) in enumerate(CLASSES.items(), start=1):
        print(f" {idx}. {name:<9} | {desc}")
    try:
        choice = int(input("Choice> ").strip())
        selected = list(CLASSES.keys())[choice - 1]
    except (ValueError, IndexError):
        print("Invalid module index.")
        state.log("Operator entered invalid class selection.")
        return

    if selected == "Engineer":
        gain = random.randint(20, 60)
        state.metal += gain
        state.log(f"Engineer optimized pipelines (+{gain} metal).")
    elif selected == "Medic":
        heal = random.randint(10, 25)
        state.health = min(100, state.health + heal)
        state.log(f"Medic restored system integrity (+{heal} HP).")
    elif selected == "Heavy":
        cost = 30
        if state.ammo >= cost:
            state.ammo -= cost
            state.log("Heavy suppressed malware barrage (-30 ammo).")
            state.enemy_wave += 1
        else:
            state.log("Heavy deployment failed: not enough ammo.")
    else:
        damage = random.randint(8, 20)
        ammo_spent = random.randint(10, 25)
        state.enemy_wave += 1
        state.ammo = max(0, state.ammo - ammo_spent)
        state.log(
            f"{selected} neutralized threats (+1 wave, -{ammo_spent} ammo, {damage} impact)."
        )


def defend_wave(state: SystemState) -> None:
    hit = random.randint(5, 18)
    if state.metal >= 25:
        state.metal -= 25
        reduced = max(0, hit - random.randint(4, 10))
        state.health = max(0, state.health - reduced)
        state.log(f"Sentry absorbed incoming wave. Integrity -{reduced}%.")
    else:
        state.health = max(0, state.health - hit)
        state.log(f"Insufficient metal: breach caused -{hit}% integrity.")


def system_tick(state: SystemState) -> None:
    if random.random() < 0.35:
        ammo_gain = random.randint(5, 15)
        state.ammo += ammo_gain
        state.log(f"Supply crate opened (+{ammo_gain} ammo).")


def main() -> None:
    state = SystemState()
    print(banner())

    while state.health > 0:
        print(
            "\nCommands: [status] [deploy] [defend] [tick] [help] [exit]"
        )
        cmd = input("tf2-os> ").strip().lower()

        if cmd == "status":
            print_status(state)
        elif cmd == "deploy":
            deploy_class(state)
        elif cmd == "defend":
            defend_wave(state)
        elif cmd == "tick":
            system_tick(state)
            print("Background services advanced by one cycle.")
        elif cmd == "help":
            print("Use deploy to activate classes, defend to survive waves.")
        elif cmd == "exit":
            print("Shutting down simulator. Thanks, mercenary.")
            return
        else:
            print("Unknown command. Type 'help'.")

    print("\nSYSTEM FAILURE: RED base has fallen.")


if __name__ == "__main__":
    main()
