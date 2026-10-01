#!/usr/bin/env python3
"""
Minimal agent harness skeleton — no API keys required.

Replace FakeModel.propose with a real model call when you are ready.
External tools require a hash-bound approval or the harness HOLDs.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def payload_hash(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()[:16]


@dataclass
class Tool:
    name: str
    fn: Callable[..., str]
    external: bool = False  # True => requires Gate approval
    description: str = ""


@dataclass
class Approval:
    """Recorded authorization bound to an exact action payload."""

    proposal_hash: str
    approved: bool
    note: str = ""


@dataclass
class Harness:
    tools: dict[str, Tool] = field(default_factory=dict)
    transcript: list[dict[str, Any]] = field(default_factory=list)
    max_steps: int = 8
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    approvals: dict[str, Approval] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def log(self, role: str, content: Any) -> None:
        self.transcript.append({"role": role, "content": content})

    def approve(self, action: dict[str, Any], note: str = "human") -> str:
        h = payload_hash(action)
        self.approvals[h] = Approval(proposal_hash=h, approved=True, note=note)
        self.log("gate", {"outcome": "AUTHORIZED", "proposal_hash": h, "note": note})
        return h

    def hold(self, action: dict[str, Any], reason: str) -> None:
        h = payload_hash(action)
        self.log("gate", {"outcome": "HOLD", "proposal_hash": h, "reason": reason})

    def run_tool(self, name: str, args: dict[str, Any]) -> str:
        if name not in self.tools:
            return f"error: unknown tool {name!r}"
        tool = self.tools[name]
        action = {"tool": name, "args": args}
        h = payload_hash(action)

        if tool.external:
            appr = self.approvals.get(h)
            if not appr or not appr.approved:
                self.hold(action, "no recorded AUTHORIZED for this payload")
                return "HOLD: capability is not authority"

        try:
            result = tool.fn(**args)
        except Exception as e:
            result = f"error: {e}"
        self.log("tool", {"tool": name, "args": args, "result": result, "hash": h})
        return result


class FakeModel:
    """Deterministic stand-in: plans a safe tool then an external one."""

    def __init__(self) -> None:
        self.i = 0

    def propose(self, transcript: list[dict[str, Any]]) -> dict[str, Any]:
        self.i += 1
        if self.i == 1:
            return {"type": "tool", "name": "echo", "args": {"text": "scout says hello"}}
        if self.i == 2:
            return {
                "type": "tool",
                "name": "post_message",
                "args": {"channel": "public", "text": "this would leave the machine"},
            }
        return {"type": "done", "reply": "loop finished"}


def main() -> None:
    h = Harness(max_steps=6)

    h.register(Tool("echo", lambda text: f"echo:{text}", external=False))
    h.register(
        Tool(
            "post_message",
            lambda channel, text: f"POSTED[{channel}]:{text}",
            external=True,
            description="leaves the machine",
        )
    )

    model = FakeModel()
    h.log("user", "demo run")

    for step in range(h.max_steps):
        proposal = model.propose(h.transcript)
        h.log("model", proposal)

        if proposal.get("type") == "done":
            print("DONE:", proposal.get("reply"))
            break

        if proposal.get("type") == "tool":
            name = proposal["name"]
            args = proposal.get("args") or {}
            # Demo: auto-approve nothing external — shows HOLD.
            # Uncomment to seal the post:
            # if name == "post_message":
            #     h.approve({"tool": name, "args": args}, note="demo")
            result = h.run_tool(name, args)
            print(f"step {step}: {name} -> {result}")
            if result.startswith("HOLD"):
                print("  (gate held — no AUTHORIZED token)")

    print("\n--- transcript ---")
    print(json.dumps(h.transcript, indent=2))


if __name__ == "__main__":
    main()
