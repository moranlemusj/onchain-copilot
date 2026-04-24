from langchain_core.messages import AIMessage

from .agent import build_agent


def main() -> None:
    agent = build_agent()
    print("On-chain copilot. Ask about any Ethereum wallet. Ctrl+C to exit.\n")
    history: list = []
    while True:
        try:
            q = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nbye")
            return
        if not q:
            continue

        history.append({"role": "user", "content": q})
        result = agent.invoke({"messages": history})
        history = result["messages"]

        last = history[-1]
        content = last.content if isinstance(last, AIMessage) else str(last)
        print(f"\n{content}\n")


if __name__ == "__main__":
    main()
