"use client";

import { useState } from "react";
import { MapPin, Calendar, User, DollarSign, Heart } from "lucide-react";

interface TravelFormProps {
  onSubmit: (data: any) => void;
  loading?: boolean;
}

export default function TravelForm({
  onSubmit,
  loading = false,
}: TravelFormProps) {
  const [formData, setFormData] = useState({
    destination: "",
    startDate: "",
    endDate: "",
    xiaohongshuAccount: "",
    budget: "medium",
    travelStyle: "cultural",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.destination || !formData.startDate || !formData.endDate) {
      alert("请填写必要信息");
      return;
    }

    const submitData = {
      destination: formData.destination,
      travel_dates: {
        start: formData.startDate,
        end: formData.endDate,
      },
      xiaohongshu_account: formData.xiaohongshuAccount || undefined,
      preferences: {
        budget: formData.budget,
        travel_style: formData.travelStyle,
      },
    };

    onSubmit(submitData);
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 目的地 */}
      <div>
        <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
          <MapPin className="w-4 h-4 mr-2" />
          旅游目的地 *
        </label>
        <input
          type="text"
          name="destination"
          value={formData.destination}
          onChange={handleInputChange}
          placeholder="例如：日本东京、泰国曼谷、法国巴黎"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
      </div>

      {/* 旅行日期 */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Calendar className="w-4 h-4 mr-2" />
            出发日期 *
          </label>
          <input
            type="date"
            name="startDate"
            value={formData.startDate}
            onChange={handleInputChange}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
        <div>
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Calendar className="w-4 h-4 mr-2" />
            返回日期 *
          </label>
          <input
            type="date"
            name="endDate"
            value={formData.endDate}
            onChange={handleInputChange}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
      </div>

      {/* 小红书账号 */}
      <div>
        <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
          <User className="w-4 h-4 mr-2" />
          小红书账号 (可选)
        </label>
        <input
          type="text"
          name="xiaohongshuAccount"
          value={formData.xiaohongshuAccount}
          onChange={handleInputChange}
          placeholder="输入您的小红书用户名，获取个性化推荐"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">
          我们将分析您的偏好，提供更精准的推荐
        </p>
      </div>

      {/* 预算范围 */}
      <div>
        <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
          <DollarSign className="w-4 h-4 mr-2" />
          预算范围
        </label>
        <select
          name="budget"
          value={formData.budget}
          onChange={handleInputChange}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="low">经济型 (节约预算)</option>
          <option value="medium">中等 (平衡性价比)</option>
          <option value="high">豪华型 (追求品质)</option>
        </select>
      </div>

      {/* 旅行风格 */}
      <div>
        <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
          <Heart className="w-4 h-4 mr-2" />
          旅行风格
        </label>
        <select
          name="travelStyle"
          value={formData.travelStyle}
          onChange={handleInputChange}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="cultural">文化体验</option>
          <option value="adventure">冒险探索</option>
          <option value="relaxation">休闲度假</option>
          <option value="food">美食之旅</option>
          <option value="photography">摄影打卡</option>
          <option value="shopping">购物天堂</option>
        </select>
      </div>

      {/* 提交按钮 */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center"
      >
        {loading ? (
          <>
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
            AI团队正在分析，请等待5到10分钟...
          </>
        ) : (
          "获取AI推荐"
        )}
      </button>
    </form>
  );
}
