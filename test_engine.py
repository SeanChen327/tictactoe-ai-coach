# test_engine.py
from ai_battle_engine import GomokuSimulator
import json

def test_simulation():
    print("🚀 Starting AI vs AI Offline Battle Simulation...")
    simulator = GomokuSimulator()
    
    # 执行对局
    history, result = simulator.run_match()
    
    print(f"🏁 Match Finished! Result: {result}")
    print(f"📊 Total Steps: {len(history)}")
    
    # 验证数据结构是否符合前端 的要求
    first_move = history[0]
    required_keys = ["step", "player", "index", "evaluation_label", "comment"]
    
    for key in required_keys:
        assert key in first_move, f"Missing key: {key}"
    
    # 打印前两步看看
    print("\n--- Sample Move Data ---")
    print(json.dumps(history[:2], indent=2))
    print("------------------------")
    print("✅ Engine Test Passed!")

if __name__ == "__main__":
    test_simulation()