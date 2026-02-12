import time
from planner import decide_next_action
from controller import execute

GOAL = "click resume"
def main():
    print("🧠 AI Desktop Agent Running")
    print("🎯 Goal:", GOAL)

    action = decide_next_action(GOAL, [])

    # ✅ HANDLE PLAN-BASED EXECUTION
    if action.get("action") == "execute_plan":
        print("📋 Executing plan...")
        for step_action in action["plan"]:
            print("➡️", step_action)
            execute(step_action)
            time.sleep(0.3)

        print("✅ Plan finished")
        return

    # ✅ FALLBACK
    if action.get("action") == "done":
        print("✅ Nothing to do")
        return

    print("❌ Unexpected action:", action)

if __name__ == "__main__":
    main()
