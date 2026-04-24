import os
import sys
import traceback

os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
os.environ.setdefault("GLOG_minloglevel", "2")

import readline  # noqa: F401  keeps input() line-editing sane on macOS

from langchain_core.messages import AIMessage, ToolMessage

from .agent import build_agent


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(p for p in parts if p)
    return str(content)


def _render_step(messages: list) -> None:
    last = messages[-1]
    if isinstance(last, AIMessage):
        if getattr(last, "tool_calls", None):
            for call in last.tool_calls:
                args = ", ".join(f"{k}={v!r}" for k, v in call["args"].items())
                print(f"  -> calling {call['name']}({args})", flush=True)
        else:
            text = _text_of(last.content)
            if text:
                print(f"\n{text}\n", flush=True)
    elif isinstance(last, ToolMessage):
        preview = str(last.content)
        if len(preview) > 400:
            preview = preview[:400] + "…"
        print(f"  <- {last.name}: {preview}", flush=True)


def main() -> None:
    print("booting agent…", flush=True)
    agent = build_agent()
    print("On-chain copilot. Ask about any Ethereum wallet. Ctrl+D to exit.\n", flush=True)
    history: list = []
    while True:
        try:
            sys.stdout.write("> ")
            sys.stdout.flush()
            q = sys.stdin.readline()
            if not q:
                print("\nbye")
                return
            q = q.strip()
        except (KeyboardInterrupt, EOFError):
            print("\nbye")
            return
        if not q:
            continue
        if q.lower() in {"exit", "quit", ":q"}:
            print("bye")
            return

        history.append({"role": "user", "content": q})
        print("thinking…", flush=True)
        try:
            for state in agent.stream({"messages": history}, stream_mode="values"):
                _render_step(state["messages"])
            history = state["messages"]
        except Exception as e:
            print(f"\n[error] {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()


if __name__ == "__main__":
    main()
