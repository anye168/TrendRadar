#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商业航天追踪功能测试脚本

用于测试商业航天追踪工具的各项功能。
"""

import sys
import os
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server.tools.commercial_space_tracking import CommercialSpaceTracking
from datetime import datetime


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_get_tracking_config():
    """测试获取追踪配置"""
    print_section("测试1: 获取追踪配置")

    tracker = CommercialSpaceTracking()
    result = tracker.get_tracking_config()

    if result.get("success"):
        print("[OK] 配置加载成功")
        config = result.get("config", {})

        print(f"\n追踪名称: {config.get('tracking_name', 'N/A')}")
        print(f"追踪描述: {config.get('tracking_description', 'N/A')}")

        # 显示提醒时段
        print("\n提醒时段:")
        for reminder in config.get("reminder_schedule", []):
            print(f"  - {reminder.get('time')}: {reminder.get('description')}")

        # 显示信源优先级
        print("\n信源优先级:")
        for tier_key, tier_data in config.get("source_priorities", {}).items():
            print(f"  {tier_key}: {tier_data.get('name')} ({tier_data.get('source_count')}个信源)")

        # 显示关键词优先级
        print("\n关键词优先级:")
        for key, keyword_data in config.get("keyword_priorities", {}).items():
            keywords = keyword_data.get("keywords", [])
            print(f"  {key}: {keyword_data.get('name')} ({len(keywords)}个关键词)")
            print(f"    示例: {', '.join(keywords[:5])}")

    else:
        print("[ERROR] 配置加载失败")
        print(f"错误: {result.get('error', {})}")


def test_search_commercial_space_news():
    """测试搜索商业航天新闻"""
    print_section("测试2: 搜索商业航天新闻")

    tracker = CommercialSpaceTracking()
    result = tracker.search_commercial_space_news(limit=10, include_url=True)

    if result.get("success"):
        print("[OK] 搜索成功")

        summary = result.get("summary", {})
        print(f"\n找到新闻总数: {summary.get('total_found', 0)}")
        print(f"返回新闻数量: {summary.get('returned_count', 0)}")
        print(f"时间范围: {summary.get('time_range', 'N/A')}")

        # 显示关键词统计
        keyword_stats = summary.get("keyword_statistics", {})
        if keyword_stats:
            print("\n关键词统计:")
            for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {keyword}: {count}次")

        # 显示新闻列表
        results = result.get("results", [])
        if results:
            print("\n新闻列表 (前5条):")
            for i, news in enumerate(results[:5], 1):
                print(f"\n  {i}. {news.get('title')}")
                print(f"     平台: {news.get('platform_name')} | 优先级: {news.get('priority')} | 排名: {news.get('rank')}")
                print(f"     匹配关键词: {', '.join(news.get('matched_keywords', []))}")
                if news.get('url'):
                    print(f"     链接: {news.get('url')}")
        else:
            print("\n未找到匹配的新闻")

    else:
        print("[ERROR] 搜索失败")
        print(f"错误: {result.get('error', {})}")


def test_get_spacex_highlights():
    """测试获取SpaceX重点内容"""
    print_section("测试3: 获取SpaceX重点内容")

    tracker = CommercialSpaceTracking()
    result = tracker.get_spacex_highlights(limit=10)

    if result.get("success"):
        print("[OK] SpaceX重点内容获取成功")

        summary = result.get("summary", {})
        print(f"\n找到SpaceX相关新闻总数: {summary.get('total_found', 0)}")
        print(f"返回新闻数量: {summary.get('returned_count', 0)}")
        print(f"关注领域: {', '.join(summary.get('focus_areas', []))}")

        # 按关注领域分类显示
        categorized = result.get("categorized_by_focus", {})
        if categorized:
            print("\n按关注领域分类:")
            for area, news_list in categorized.items():
                if news_list:
                    print(f"\n  {area} ({len(news_list)}条):")
                    for news in news_list[:3]:
                        print(f"    - {news.get('title')}")

        # 显示新闻列表
        results = result.get("results", [])
        if results:
            print("\nSpaceX新闻列表 (前5条):")
            for i, news in enumerate(results[:5], 1):
                print(f"\n  {i}. {news.get('title')}")
                print(f"     平台: {news.get('platform_name')} | 优先级: {news.get('priority')}")
                print(f"     匹配关键词: {', '.join(news.get('matched_keywords', []))}")
        else:
            print("\n未找到SpaceX相关新闻")

    else:
        print("[ERROR] SpaceX重点内容获取失败")
        print(f"错误: {result.get('error', {})}")


def test_check_reminder_time():
    """测试检查提醒时间"""
    print_section("测试4: 检查提醒时间")

    tracker = CommercialSpaceTracking()

    # 测试当前时间
    print("\n当前时间检查:")
    result = tracker.check_reminder_time()

    if result.get("success"):
        is_reminder = result.get("is_reminder_time", False)
        print(f"  当前时间: {result.get('current_time', 'N/A')}")
        print(f"  是否为提醒时间: {'是' if is_reminder else '否'}")

        if is_reminder:
            reminder = result.get("reminder", {})
            print(f"  提醒时段: {reminder.get('time')} - {reminder.get('description')}")
        else:
            print(f"  原因: {result.get('reason', 'N/A')}")
    else:
        print("✗ 检查失败")
        print(f"错误: {result.get('error', {})}")

    # 测试提醒时间段
    print("\n测试提醒时间段:")
    test_times = ["09:00", "14:00", "18:00"]
    for time_str in test_times:
        test_time = datetime.strptime(f"2025-01-08 {time_str}", "%Y-%m-%d %H:%M")
        result = tracker.check_reminder_time(current_time=test_time)

        if result.get("success") and result.get("is_reminder_time"):
            print(f"  [OK] {time_str} - 是提醒时间")
        else:
            print(f"  [SKIP] {time_str} - 不是提醒时间")


def test_get_quick_reference():
    """测试获取快速参考清单"""
    print_section("测试5: 获取快速参考清单")

    tracker = CommercialSpaceTracking()
    result = tracker.get_quick_reference()

    if result.get("success"):
        print("[OK] 快速参考清单获取成功")

        ref = result.get("quick_reference", {})

        print("\n核心标的:")
        for target in ref.get("core_targets", []):
            print(f"  - {target}")

        print("\n核心关键词:")
        for keyword in ref.get("core_keywords", []):
            print(f"  - {keyword}")

        print("\n第一梯队信源:")
        for source in ref.get("tier1_sources", []):
            print(f"  - {source}")

        print("\nSpaceX关注领域:")
        for area in ref.get("spacex_focus_areas", []):
            print(f"  - {area}")

        print("\n提醒时段:")
        for reminder in ref.get("reminder_schedule", []):
            print(f"  - {reminder.get('time')}: {reminder.get('description')}")

    else:
        print("[ERROR] 快速参考清单获取失败")
        print(f"错误: {result.get('error', {})}")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  商业航天追踪功能测试")
    print("=" * 60)

    try:
        # 运行所有测试
        test_get_tracking_config()
        test_search_commercial_space_news()
        test_get_spacex_highlights()
        test_check_reminder_time()
        test_get_quick_reference()

        print("\n" + "=" * 60)
        print("  测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
