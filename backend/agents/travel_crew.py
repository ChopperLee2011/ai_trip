import os
import time
import logging
from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from typing import Dict, Any, Optional
import json
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@CrewBase
class TravelRecommendationCrew:
    def __init__(self):
        # self.llm = LLM(
        #     model="openrouter/deepseek/deepseek-r1:free",
        #     base_url="https://openrouter.ai/api/v1",
        #     api_key=os.getenv("OPENROUTER_API_KEY")
        # )
        self.llm = LLM(
            model=os.getenv("DEEPSEEK_MODEL"),
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
            api_key=os.getenv("DEEPSEEK_API_KEY")
        )
        self.travel_input = None

    def _task_callback(self, task_output):
        """任务完成回调函数"""
        task_name = getattr(task_output, 'description', 'Unknown Task')[:50]
        current_time = time.localtime()
        logging.info(f"✅ 任务完成: {task_name}")
        logging.info(f"⏰ 完成时间: {current_time}")
        logging.info(f"📝 输出长度: {len(str(task_output))} 字符")
        logging.info("-" * 50)
        return task_output
    
    @agent    
    def destination_expert(self) -> Agent:
        """目的地专家 - 负责收集目的地信息"""
        return Agent(
            role="目的地旅游专家",
            goal="提供详细的目的地信息，包括景点、美食、文化、交通等",
            backstory="""你是一位经验丰富的旅游专家，对世界各地的旅游目的地都有深入了解。
            你擅长分析目的地的特色、最佳旅游时间、必去景点、当地美食和文化体验。""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def itinerary_planner(self) -> Agent:
        """行程规划师 - 负责制定详细行程"""
        return Agent(
            role="专业行程规划师",
            goal="根据旅行时间和偏好制定合理的日程安排",
            backstory="""你是一位专业的行程规划师，擅长根据旅行者的时间、预算和偏好
            制定高效且有趣的旅行行程。你考虑交通便利性、时间安排的合理性。""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def preference_analyzer(self) -> Agent:
        """偏好分析师 - 分析用户偏好"""
        return Agent(
            role="用户偏好分析师",
            # goal="分析用户的旅行偏好和小红书账号信息，提供个性化建议",
            goal="分析用户的旅行偏好，提供个性化建议",
            backstory="""你是一位数据分析专家，擅长从用户的社交媒体活动中分析其旅行偏好、
            兴趣爱好和生活方式，为其提供个性化的旅行建议。""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def coordinator(self) -> Agent:
        """协调员 - 整合所有信息"""
        return Agent(
            role="旅行推荐协调员",
            goal="整合所有专家的建议，生成最终的个性化旅行推荐",
            backstory="""你是团队的协调员，负责整合目的地专家、行程规划师和偏好分析师的建议，
            生成一份完整、个性化且实用的旅行推荐报告。""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
    # 任务1：目的地分析
   
    @task
    def destination_task(self) -> Task:
        travel_input = self.travel_input
        return Task(
            description=f"""分析目的地 {travel_input['destination']} 的详细信息：
            1. 主要景点和必去地点
            2. 当地特色美食和推荐餐厅
            3. 文化体验和活动
            4. 交通方式和注意事项
            5. 最佳游览时间和季节特色
            
            旅行时间：{travel_input['start_date']} 到 {travel_input['end_date']}
            """,
            agent=self.destination_expert(),
            expected_output="详细的目的地信息报告，包含景点、美食、文化、交通等信息",
            callback=self._task_callback
        )
    
    # 任务2：偏好分析
    @task
    def preference_task(self) -> Task:
        travel_input = self.travel_input
        return Task(
            description=f"""分析用户偏好：
            # 小红书账号：{travel_input.get('xiaohongshu_account', '未提供')}
            用户偏好：{travel_input.get('preferences', {})}
            
            根据提供的信息，总结用户的旅行风格、兴趣和预算。""",
            agent=self.preference_analyzer(),
            expected_output="用户偏好分析报告，包含旅行风格、兴趣和预算分析",
            callback=self._task_callback
        )
    
    # 任务3：行程规划
    @task
    def itinerary_task(self) -> Task:
        travel_input = self.travel_input
        return Task(
            description=f"""基于目的地信息和用户偏好，制定详细行程：
            目的地：{travel_input['destination']}
            开始日期：{travel_input['start_date']}
            结束日期：{travel_input['end_date']}
            
            制定包含以下内容的行程：
            1. 每日详细安排
            2. 景点游览顺序
            3. 餐厅推荐
            4. 交通安排
            5. 住宿建议
            输出格式要求: JSON格式 包含:
            - date: 日期
            - schedule: 每日行程数组，包含：
                - time: 时间
                - activity: 活动
            """,
            agent=self.itinerary_planner(),
            expected_output="详细的日程安排，包含每日行程、餐厅、交通和住宿建议",
            context=[self.destination_task(), self.preference_task()],
            callback=self._task_callback
        )

    # 任务4：最终整合
    @task
    def coordination_task(self) -> Task:
        return Task(
            description="""整合所有专家的建议，生成最终推荐报告：
            1. 综合分析用户偏好和目的地特色
            2. 优化行程安排
            3. 提供个性化建议
            4. 生成结构化的推荐结果
            
            输出格式要求：JSON格式，包含：
            - itinerary: 日程安排数组
            - restaurants: 推荐餐厅数组  
            - attractions: 推荐景点数组
            - accommodations: 住宿建议数组
            - tips: 旅行小贴士数组
            """,
            agent=self.coordinator(),
            expected_output="完整的JSON格式旅行推荐报告",
            context=[self.destination_task(), self.preference_task(), self.itinerary_task()],
            callback=self._task_callback
        )

    @crew
    def crew(self) -> Crew:
        # 创建团队并执行，添加超时设置
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            # 添加任务超时设置（单位：秒）
            task_timeout=600  # 10分钟超时
        )

    def _run_crew_with_logging(self):
        """包装CrewAI执行，添加详细日志"""
        try:
            logging.info("🤖 创建Crew实例...")
            crew_instance = self.crew()

            logging.info("🎯 开始执行kickoff()...")
            result = crew_instance.kickoff()

            logging.info("✅ CrewAI执行完成!")
            return result

        except Exception as e:
            logging.error(f"❌ CrewAI执行失败: {str(e)}")
            import traceback
            logging.error(f"详细错误: {traceback.format_exc()}")
            raise

    async def generate_recommendations(self, travel_input: Dict[str, Any]) -> Dict[str, Any]:
        """生成旅行推荐"""
        logging.info(f"🚀 开始处理目的地: {travel_input['destination']}")
        self.travel_input = travel_input

        try:
            # 记录开始执行时间
            start_time = time.time()
            logging.info("📋 开始执行Crew任务...")

            # 在线程池中执行同步的crew.kickoff()，避免阻塞事件循环
            import asyncio
            loop = asyncio.get_running_loop()

            logging.info("🔄 开始执行CrewAI任务...")
            result = await loop.run_in_executor(
                None,  # 使用默认线程池
                self._run_crew_with_logging  # 包装方法，添加日志
            )
            
            # 记录执行完成信息
            execution_time = time.time() - start_time
            logging.info(f"任务执行完成，耗时: {execution_time:.2f}秒")
            logging.info(f"Task 执行结果类型: {type(result)}")
            logging.debug(f"Raw result: {result}")
        except Exception as e:
            import traceback
            logging.error(f"Crew kickoff 失败: {str(e)}")
            logging.error(f"异常详情: {traceback.format_exc()}")
            
            # 返回错误信息
            return {
                "recommendations": {
                    "error": f"执行失败: {str(e)}",
                    "details": traceback.format_exc(),
                    "itinerary": [],
                    "restaurants": [],
                    "attractions": [],
                    "accommodations": []
                },
                "analysis": "执行过程中发生错误，请检查日志获取详细信息。"
            }

        # 获取最后一个任务的输出（coordination_task的结果）
        task_output = str(result.tasks_output[-1])
        
        # 解析结果
        try:
            # 处理可能包含markdown格式的JSON字符串
            if isinstance(task_output, str):
                # 尝试从markdown代码块中提取JSON
                json_match = re.search(r'```(?:json)?\s*\n([\s\S]*?)\n```', task_output)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    # 如果没有markdown代码块，尝试直接提取JSON对象
                    json_match = re.search(r'(\{[\s\S]*\})', task_output)
                    if json_match:
                        json_str = json_match.group(1).strip()
                    else:
                        raise json.JSONDecodeError("No JSON object found in string", task_output, 0)
                
                # 尝试解析JSON
                try:
                    recommendations = json.loads(json_str)
                except json.JSONDecodeError as e:
                    logging.error(f"JSON解析错误: {str(e)}")
                    logging.error(f"尝试解析的字符串: {json_str[:100]}...")
                    raise
            else:
                # 如果不是字符串，假设它已经是一个字典/对象
                recommendations = task_output
                
            # 确保recommendations包含所有必要的字段
            if isinstance(recommendations, dict):
                for key in ["itinerary", "restaurants", "attractions", "accommodations", "tips"]:
                    if key not in recommendations:
                        recommendations[key] = []
            
            return {
                "recommendations": recommendations,
                "analysis": "基于您的偏好和目的地特色，我们的AI团队为您精心制定了这份个性化旅行推荐。",
                "status": "success"
            }
        except json.JSONDecodeError as e:
            # 如果JSON解析失败，记录错误并返回更详细的错误信息
            logging.error(f"JSON解析错误: {str(e)}")
            logging.error(f"原始输出: {task_output[:200]}...")  # 只打印前200个字符避免日志过长
            
            # 尝试提取有用信息
            summary = "无法解析AI生成的推荐内容"
            if len(task_output) > 100:
                summary = task_output[:500] + "..." if len(task_output) > 500 else task_output
            
            return {
                "recommendations": {
                    "error": f"JSON解析失败: {str(e)}",
                    "summary": summary,
                    "itinerary": [],
                    "restaurants": [],
                    "attractions": [],
                    "accommodations": [],
                    "tips": []
                },
                "analysis": "推荐已生成，但格式需要进一步处理。请联系技术支持。"
            }
