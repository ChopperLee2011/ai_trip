"use client";

import { useState } from "react";
import TravelForm from "@/components/TravelForm";
import RecommendationResult from "@/components/RecommendationResult";
import { MapPin, Calendar, User, Sparkles } from "lucide-react";

interface TravelData {
  destination: string;
  travel_dates: {
    start: string;
    end: string;
  };
  xiaohongshu_account?: string;
  preferences?: {
    budget: string;
    travel_style: string;
  };
}

interface RecommendationData {
  recommendations: any;
  analysis: string;
  success: boolean;
}

interface QueuePosition {
  total: number;
  position: number;
}

export default function Home() {
  const [recommendations, setRecommendations] =
    useState<RecommendationData | null>(null);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);
  const [queuePosition, setQueuePosition] = useState<QueuePosition | null>(
    null
  );

  const fetchQueuePosition = async (taskId: string) => {
    try {
      const response = await fetch(`/api/queue/position/${taskId}`);
      if (!response.ok) {
        throw new Error("队列状态查询失败");
      }
      const data = await response.json();
      setQueuePosition(data.position);
      return data.position;
    } catch (error) {
      console.error("获取队列状态失败:", error);
    }
  };

  const pollForResult = async (taskId: string) => {
    setPolling(true);
    setStatusMsg("结果生成中...");
    let timeoutId: NodeJS.Timeout | null = null;
    const poll = async () => {
      try {
        const position = await fetchQueuePosition(taskId);
        if (position && position > 1) {
          setStatusMsg(
            `您的请求正在队列中，当前位置: 第 ${position} 位，大概需要等待 ${
              position * 5
            } 分钟，请勿关闭页面。`
          );
          timeoutId = setTimeout(poll, 10000); // 10s后再次请求
        } else if (position == 1) {
          setStatusMsg("预计等待5分钟，请勿关闭页面，您的请求正在处理中...");
          setQueuePosition(null);
          const response = await fetch(`/api/result/${taskId}`);
          if (!response.ok) {
            if (response.status === 404) {
              // 任务还未创建，继续等待
              return;
            }
            throw new Error("结果查询失败");
          }
          const data = await response.json();
          if (data.status === "SUCCESS") {
            setRecommendations(data.result);
            setStatusMsg(null);
            setPolling(false);
          } else if (data.status === "FAILURE") {
            setStatusMsg("推荐生成失败，请稍后重试");
            setPolling(false);
          } else {
            // 继续等待
            timeoutId = setTimeout(poll, 10000); // 10s后再次请求
          }
        }
      } catch (error) {
        setStatusMsg("查询结果时出错，请稍后重试");
        setPolling(false);
        setQueuePosition(null);
      }
    };
    poll();
    // 最长等待15分钟
    setTimeout(() => {
      if (polling) {
        setStatusMsg("请求超时，请稍后重试。");
        setPolling(false);
        if (timeoutId) clearTimeout(timeoutId);
      }
    }, 9000000);
  };

  const handleFormSubmit = async (data: TravelData) => {
    setRecommendations(null);
    setStatusMsg("结果生成中...");
    try {
      const response = await fetch("/api/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (response.status !== 202) {
        throw new Error("无法启动推荐任务");
      }
      const result = await response.json();
      pollForResult(result.task_id);
    } catch (error) {
      setStatusMsg("推荐生成失败，请稍后重试");
    }
  };

  return (
    <main className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center mb-4">
          <Sparkles className="w-8 h-8 text-blue-600 mr-2" />
          <h1 className="text-4xl font-bold text-gray-800">智能旅游推荐系统</h1>
        </div>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          基于AI多智能体协作，为您量身定制个性化旅游推荐
        </p>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <div className="bg-white rounded-lg p-6 shadow-md">
          <MapPin className="w-8 h-8 text-blue-600 mb-3" />
          <h3 className="text-lg font-semibold mb-2">目的地专家</h3>
          <p className="text-gray-600">
            深度分析目的地特色，提供最全面的旅游信息
          </p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-md">
          <Calendar className="w-8 h-8 text-green-600 mb-3" />
          <h3 className="text-lg font-semibold mb-2">智能行程规划</h3>
          <p className="text-gray-600">根据时间和偏好，制定最优化的旅行路线</p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-md">
          <User className="w-8 h-8 text-purple-600 mb-3" />
          <h3 className="text-lg font-semibold mb-2">个性化分析</h3>
          <p className="text-gray-600">结合小红书偏好，提供专属旅游建议</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Form Section */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            开始您的旅程
          </h2>
          <TravelForm onSubmit={handleFormSubmit} loading={polling} />
        </div>

        {/* Results Section */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">AI推荐结果</h2>
          {statusMsg ? (
            <div className="flex items-center justify-center h-64">
              <span className="ml-3 text-gray-600">{statusMsg}</span>
            </div>
          ) : recommendations ? (
            <RecommendationResult data={recommendations} />
          ) : (
            <div className="text-center text-gray-500 h-64 flex items-center justify-center">
              <div>
                <Sparkles className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p>填写左侧表单，获取AI个性化推荐</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
