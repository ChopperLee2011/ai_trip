
import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    print("/health:", resp.json())

def test_recommend():
    payload = {
        "destination": "东京",
        "travel_dates": {"start": "2025-09-01", "end": "2025-09-07"},
        "xiaohongshu_account": "test_account",
        "preferences": {"budget": "中等", "travel_style": "文化体验"}
    }
    resp = client.post("/api/recommend", json=payload)
    assert resp.status_code == 202
    task_id = resp.json()["task_id"]
    print("/api/recommend task_id:", task_id)
    # 轮询结果
    for _ in range(20):
        result_resp = client.get(f"/api/result/{task_id}")
        assert result_resp.status_code == 200
        data = result_resp.json()
        print("/api/result status:", data["status"])
        if data["status"] == "SUCCESS":
            print("推荐结果:", data["result"])
            break
        elif data["status"] == "FAILURE":
            print("任务失败:", data["result"])
            break
        time.sleep(1)
    else:
        print("任务超时未完成")

# def test_analyze_xiaohongshu():
#     resp = client.post("/api/analyze-xiaohongshu", json="test_account")
#     print(f"resp: {resp}")
#     assert resp.status_code == 200
#     print("/api/analyze-xiaohongshu:", resp.json())

if __name__ == "__main__":
    test_health()
    test_recommend()
    # test_analyze_xiaohongshu()
