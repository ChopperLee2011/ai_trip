"use client";

import { useState } from "react";
import {
  MapPin,
  Clock,
  Utensils,
  Bed,
  Lightbulb,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface RecommendationResultProps {
  data: {
    recommendations: any;
    analysis: string;
    success: boolean;
  };
}

export default function RecommendationResult({
  data,
}: RecommendationResultProps) {
  const [activeTab, setActiveTab] = useState("itinerary");
  const [expandedDay, setExpandedDay] = useState<number | null>(null);

  if (!data.recommendations) {
    return (
      <div className="text-center text-red-500 p-8">
        <p>推荐生成失败，请稍后重试</p>
      </div>
    );
  }

  const { recommendations, analysis } = data;

  // 处理不同格式的推荐数据
  const getRecommendationData = () => {
    if (typeof recommendations === "string") {
      return {
        summary: recommendations,
        itinerary: [],
        restaurants: [],
        attractions: [],
        accommodations: [],
        tips: [],
      };
    }

    return {
      summary: recommendations.summary || "",
      itinerary: recommendations.itinerary || [],
      restaurants: recommendations.restaurants || [],
      attractions: recommendations.attractions || [],
      accommodations: recommendations.accommodations || [],
      tips: recommendations.tips || [],
    };
  };

  const recData = getRecommendationData();

  const tabs = [
    { id: "itinerary", label: "行程安排", icon: Clock },
    { id: "attractions", label: "推荐景点", icon: MapPin },
    { id: "restaurants", label: "美食推荐", icon: Utensils },
    { id: "accommodations", label: "住宿建议", icon: Bed },
    { id: "tips", label: "旅行贴士", icon: Lightbulb },
  ];

  const renderItinerary = () => {
    if (!recData.itinerary.length) {
      return (
        <div className="text-gray-500 text-center py-8">
          <p>暂无详细行程安排</p>
          {recData.summary && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg text-left">
              <p className="whitespace-pre-wrap">{recData.summary}</p>
            </div>
          )}
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {recData.itinerary.map((day: any, index: number) => (
          <div key={index} className="border border-gray-200 rounded-lg">
            <button
              onClick={() =>
                setExpandedDay(expandedDay === index ? null : index)
              }
              className="w-full p-4 text-left flex items-center justify-between hover:bg-gray-50"
            >
              <div>
                <h3 className="font-semibold text-lg">第 {index + 1} 天</h3>
                <p className="text-gray-600">{day.date}</p>
              </div>
              {expandedDay === index ? <ChevronUp /> : <ChevronDown />}
            </button>

            {expandedDay === index && (
              <div className="px-4 pb-4 border-t border-gray-100">
                <div className="space-y-3 mt-3">
                  {day.activities?.map((activity: any, actIndex: number) => (
                    <div key={actIndex} className="flex items-start space-x-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      <div>
                        <p className="font-medium">
                          {activity.name || `活动 ${actIndex + 1}`}
                        </p>
                        <p className="text-gray-600">{activity.description}</p>
                      </div>
                    </div>
                  )) || (
                    <p className="text-gray-600">{day.description || day}</p>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderList = (items: any[], emptyMessage: string) => {
    if (!items.length) {
      return <p className="text-gray-500 text-center py-8">{emptyMessage}</p>;
    }

    return (
      <div className="grid gap-4">
        {items.map((item: any, index: number) => (
          <div
            key={index}
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <h3 className="font-semibold text-lg mb-2">
              {item.name || item.title || `项目 ${index + 1}`}
            </h3>
            {item.description && (
              <p className="text-gray-600 mb-2">{item.description}</p>
            )}
            {item.address && (
              <p className="text-sm text-gray-500">📍 {item.address}</p>
            )}
            {item.price && (
              <p className="text-sm text-green-600">💰 {item.price}</p>
            )}
            {item.rating && (
              <p className="text-sm text-yellow-600">⭐ {item.rating}</p>
            )}
            {typeof item === "string" && (
              <p className="text-gray-600">{item}</p>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "itinerary":
        return renderItinerary();
      case "attractions":
        return renderList(recData.attractions, "暂无景点推荐");
      case "restaurants":
        return renderList(recData.restaurants, "暂无餐厅推荐");
      case "accommodations":
        return renderList(recData.accommodations, "暂无住宿建议");
      case "tips":
        return renderList(recData.tips, "暂无旅行贴士");
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* AI分析 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-800 mb-2">AI分析</h3>
        <p className="text-blue-700">{analysis}</p>
      </div>

      {/* 标签页 */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* 标签页内容 */}
      <div className="min-h-[300px]">{renderTabContent()}</div>
    </div>
  );
}
