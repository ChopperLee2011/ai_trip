from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv
import uuid
from enum import Enum
import hashlib
import redis
import json
import asyncio
import time
import logging

# 加载环境变量
load_dotenv()

from task_queue.tasks import process_travel_recommendation, get_queue_status, get_position
from task_queue.queue_config import redis_client

from agents.travel_crew import TravelRecommendationCrew

app = FastAPI(
    title="智能旅游推荐系统",
    description="基于CrewAI和DeepSeek的个性化旅游推荐API",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Redis 缓存设置 ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# --- Task Management ---
class TaskStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

tasks = {}

# --- Pydantic Models ---
class TravelRequest(BaseModel):
    destination: str
    travel_dates: Dict[str, str]
    xiaohongshu_account: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class TaskCreationResponse(BaseModel):
    task_id: str

class TaskResultResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None

class QueueStatusResponse(BaseModel):
    total: int
    position: int

# --- Crew AI Setup ---
travel_crew = TravelRecommendationCrew()

async def run_crew_in_background(task_id: str, travel_input: Dict[str, Any]):
    try:
        # 记录任务开始时间
        start_time = time.monotonic()
        logging.info(f"开始执行任务 {task_id}，目的地: {travel_input.get('destination')}")
        
        # 添加超时控制（10分钟）
        try:
            result = await asyncio.wait_for(
                travel_crew.generate_recommendations(travel_input),
                timeout=600.0  # 10分钟超时
            )
            
            # 记录执行时间
            elapsed = time.monotonic() - start_time
            logging.info(f"任务 {task_id} 成功完成，耗时: {elapsed:.2f}秒")
            if result and result.get("status") == "success":
                tasks[task_id] = {"status": TaskStatus.SUCCESS, "result": result}
                # 写入 Redis
                redis_client.hset(f"travel:task:{task_id}", mapping={
                    "status": TaskStatus.SUCCESS,
                    "result": json.dumps(result, ensure_ascii=False)
                })
            else:
                tasks[task_id] = {"status": TaskStatus.FAILURE, "result": result}
                redis_client.hset(f"travel:task:{task_id}", mapping={
                    "status": TaskStatus.FAILURE,
                    "result": json.dumps(result, ensure_ascii=False)
                })
        except asyncio.TimeoutError:
            # 处理超时情况
            elapsed = time.monotonic() - start_time
            logging.error(f"任务 {task_id} 执行超时，已耗时: {elapsed:.2f}秒")
            
            error_result = {"error": "任务执行超时，请稍后再试"}
            tasks[task_id] = {"status": TaskStatus.FAILURE, "result": error_result}
            
            # 使用线程池执行同步Redis操作
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: redis_client.hset(f"travel:task:{task_id}", mapping={
                    "status": TaskStatus.FAILURE,
                    "result": json.dumps(error_result, ensure_ascii=False)
                })
            )
    except Exception as e:
        import traceback
        elapsed = time.monotonic() - start_time if 'start_time' in locals() else 0
        logging.error(f"任务 {task_id} 执行失败，耗时: {elapsed:.2f}秒，错误: {str(e)}")
        logging.error(f"异常详情: {traceback.format_exc()}")
        
        tasks[task_id] = {"status": TaskStatus.FAILURE, "result": {"error": str(e)}}
        redis_client.hset(f"travel:task:{task_id}", mapping={
            "status": TaskStatus.FAILURE,
            "result": json.dumps({"error": str(e)}, ensure_ascii=False)
        })

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "智能旅游推荐系统 API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "travel-recommendation-api"}

@app.post("/api/recommend", response_model=TaskCreationResponse, status_code=202)
async def get_travel_recommendations(request: TravelRequest):
    # 1. 生成请求参数的唯一哈希
    travel_input = {
        "destination": request.destination,
        "start_date": request.travel_dates.get("start"),
        "end_date": request.travel_dates.get("end"),
        "xiaohongshu_account": request.xiaohongshu_account,
        "preferences": request.preferences or {}
    }
    input_str = json.dumps(travel_input, sort_keys=True, ensure_ascii=False)
    input_hash = hashlib.md5(input_str.encode("utf-8")).hexdigest()

    # 2. 查 Redis 缓存 - 使用线程池执行同步Redis操作
    loop = asyncio.get_running_loop()
    cached_task_id = await loop.run_in_executor(
        None,
        lambda: redis_client.get(f"travel:input:{input_hash}:task_id")
    )
    
    if cached_task_id:
        # 检查任务状态 - 同样使用线程池
        task_data = await loop.run_in_executor(
            None,
            lambda: redis_client.hgetall(f"travel:task:{cached_task_id}")
        )
        
        if task_data and task_data.get("status") == TaskStatus.SUCCESS:
            return TaskCreationResponse(task_id=cached_task_id)

    # 3. 没有缓存，正常生成
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": TaskStatus.PENDING, "result": None}

    # 写入 Redis 映射
    redis_client.set(f"travel:input:{input_hash}:task_id", task_id, ex=120*3600)  # 120小时过期
    redis_client.hset(f"travel:task:{task_id}", mapping={"status": TaskStatus.PENDING, "result": ""})
    
    process_travel_recommendation(task_id, travel_input)
    logging.info(f"任务 {task_id} 已提交到后台执行")
    return TaskCreationResponse(task_id=task_id)


@app.get("/api/queue/position/{task_id}", response_model=QueueStatusResponse)
async def get_queue_position(task_id: str):
    try:
        queue_status = get_queue_status()
        position = get_position(task_id)
        # TODO: fix this work around
        if position is None:
            position = 1
        status = {
            "total": queue_status["total"],
            "position": position 
        }
        print(f"queue_status: {queue_status}")
        print(f"position: {position}")
        return QueueStatusResponse(**status)
    except Exception as e:
        logging.error(f"获取队列状态错误: {str(e)}") 

@app.get("/api/result/{task_id}", response_model=TaskResultResponse)
async def get_task_result(task_id: str):
    # 获取事件循环
    loop = asyncio.get_running_loop()
    
    # 优先查 Redis - 使用线程池执行同步Redis操作
    try:
        # 将同步Redis操作移到线程池中执行
        task_data = await loop.run_in_executor(
            None, 
            lambda: redis_client.hgetall(f"travel:task:{task_id}")
        )
        
        if task_data:
            status = task_data.get("status", TaskStatus.PENDING)
            result = None
            if status == TaskStatus.SUCCESS:
                try:
                    # 将JSON解析也移到线程池中执行
                    result_str = task_data["result"]
                    if result_str:
                        result = await loop.run_in_executor(
                            None,
                            lambda: json.loads(result_str)
                        )
                except Exception as e:
                    logging.error(f"JSON解析错误: {str(e)}")
                    result = task_data["result"]
            return TaskResultResponse(task_id=task_id, status=status, result=result)
    except Exception as e:
        logging.error(f"Redis查询错误: {str(e)}")
    
    # 回退到内存 - 同样使用线程池
    try:
        task = await loop.run_in_executor(None, lambda: tasks.get(task_id))
        if task:
            return TaskResultResponse(task_id=task_id, status=task["status"], result=task["result"])
    except Exception as e:
        logging.error(f"内存查询错误: {str(e)}")
    
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/api/analyze-xiaohongshu")
async def analyze_xiaohongshu_account(account: str):
    """
    分析小红书账号偏好（模拟功能）
    """
    try:
        # 这里可以集成真实的小红书数据分析
        # 目前返回模拟数据
        mock_analysis = {
            "travel_style": "文艺小清新",
            "preferred_destinations": ["日本", "韩国", "台湾"],
            # "budget_range": "中等",
            "interests": ["美食", "摄影", "文化体验"],
            "activity_preferences": ["博物馆", "咖啡厅", "当地市场"]
        }
        
        return {
            "account": account,
            "analysis": mock_analysis,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"账号分析失败: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
