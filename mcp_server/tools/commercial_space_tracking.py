"""
商业航天全网追踪工具

提供商业航天相关新闻的优先级追踪、检索和提醒功能。
"""

import re
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from ..services.data_service import DataService
from ..services.parser_service import ParserService
from ..utils.errors import MCPError, InvalidParameterError


class CommercialSpaceTracking:
    """商业航天追踪工具类"""

    def __init__(self, project_root: str = None):
        """
        初始化商业航天追踪工具

        Args:
            project_root: 项目根目录
        """
        self.parser = ParserService(project_root)
        self.data_service = DataService(project_root)
        self.config = self._load_tracking_config()

    def _load_tracking_config(self) -> Dict:
        """
        加载商业航天追踪配置

        Returns:
            配置字典
        """
        config_file = self.parser.project_root / "config" / "commercial_space_tracking.yaml"

        if not config_file.exists():
            return {
                "enabled": False,
                "error": "配置文件不存在"
            }

        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            return {
                "enabled": False,
                "error": f"配置文件加载失败: {str(e)}"
            }

    def get_tracking_config(self) -> Dict:
        """
        获取商业航天追踪配置

        Returns:
            配置字典
        """
        if not self.config.get("enabled", False):
            return {
                "success": False,
                "error": {
                    "code": "TRACKING_DISABLED",
                    "message": "商业航天追踪功能未启用"
                }
            }

        return {
            "success": True,
            "config": {
                "tracking_name": self.config.get("tracking_name", ""),
                "tracking_description": self.config.get("tracking_description", ""),
                "reminder_schedule": self.config.get("reminder_schedule", []),
                "source_priorities": self._format_source_priorities(),
                "keyword_priorities": self._format_keyword_priorities(),
                "spacex_focus": self.config.get("spacex_focus", {}),
                "execution_rules": self.config.get("execution_rules", {})
            }
        }

    def _format_source_priorities(self) -> Dict:
        """格式化信源优先级"""
        result = {}
        for tier_key in ["tier1", "tier2", "tier3", "tier4"]:
            tier_data = self.config.get("source_priorities", {}).get(tier_key, {})
            if tier_data:
                result[tier_key] = {
                    "name": tier_data.get("name", ""),
                    "priority": tier_data.get("priority", 0),
                    "source_count": len(tier_data.get("sources", [])),
                    "sources": [s.get("name") for s in tier_data.get("sources", [])]
                }
        return result

    def _format_keyword_priorities(self) -> Dict:
        """格式化关键词优先级"""
        result = {}
        for key in ["core_keywords", "extended_keywords"]:
            keyword_data = self.config.get("keyword_priorities", {}).get(key, {})
            if keyword_data:
                result[key] = {
                    "name": keyword_data.get("name", ""),
                    "priority": keyword_data.get("priority", 0),
                    "keywords": keyword_data.get("keywords", [])
                }
        return result

    def search_commercial_space_news(
        self,
        date_range: Optional[Dict[str, str]] = None,
        limit: int = 50,
        include_url: bool = False
    ) -> Dict:
        """
        搜索商业航天相关新闻

        Args:
            date_range: 日期范围，格式: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
            limit: 返回条数限制，默认50
            include_url: 是否包含URL链接，默认False

        Returns:
            搜索结果字典
        """
        if not self.config.get("enabled", False):
            return {
                "success": False,
                "error": {
                    "code": "TRACKING_DISABLED",
                    "message": "商业航天追踪功能未启用"
                }
            }

        try:
            # 获取所有关键词
            core_keywords = self.config.get("keyword_priorities", {}).get("core_keywords", {}).get("keywords", [])
            extended_keywords = self.config.get("keyword_priorities", {}).get("extended_keywords", {}).get("keywords", [])
            all_keywords = core_keywords + extended_keywords

            if not all_keywords:
                return {
                    "success": False,
                    "error": {
                        "code": "NO_KEYWORDS",
                        "message": "未配置追踪关键词"
                    }
                }

            # 处理日期范围
            if date_range:
                from ..utils.validators import validate_date_range
                start_date, end_date = validate_date_range(date_range)
            else:
                # 默认使用今天
                earliest, latest = self.data_service.get_available_date_range()
                if latest is None:
                    return {
                        "success": False,
                        "error": {
                            "code": "NO_DATA_AVAILABLE",
                            "message": "没有可用的新闻数据"
                        }
                    }
                start_date = end_date = latest

            # 收集所有匹配的新闻
            all_matches = []
            current_date = start_date

            while current_date <= end_date:
                try:
                    all_titles, id_to_name, _ = self.data_service.parser.read_all_titles_for_date(
                        date=current_date
                    )

                    for platform_id, titles in all_titles.items():
                        platform_name = id_to_name.get(platform_id, platform_id)

                        for title, info in titles.items():
                            # 检查是否匹配任何关键词
                            match_result = self._check_keyword_match(title, all_keywords, core_keywords)

                            if match_result["matched"]:
                                news_item = {
                                    "title": title,
                                    "platform": platform_id,
                                    "platform_name": platform_name,
                                    "date": current_date.strftime("%Y-%m-%d"),
                                    "matched_keywords": match_result["matched_keywords"],
                                    "priority": match_result["priority"],
                                    "ranks": info.get("ranks", []),
                                    "count": len(info.get("ranks", [])),
                                    "rank": info["ranks"][0] if info["ranks"] else 999
                                }

                                # 条件性添加 URL 字段
                                if include_url:
                                    news_item["url"] = info.get("url", "")
                                    news_item["mobileUrl"] = info.get("mobileUrl", "")

                                all_matches.append(news_item)

                except Exception:
                    # 该日期没有数据，继续下一天
                    pass

                current_date += timedelta(days=1)

            if not all_matches:
                return {
                    "success": True,
                    "results": [],
                    "total": 0,
                    "message": "未找到匹配的商业航天新闻"
                }

            # 按优先级和排名排序
            all_matches.sort(key=lambda x: (x.get("priority", 99), x.get("rank", 999)))

            # 限制返回数量
            results = all_matches[:limit]

            # 统计信息
            keyword_stats = {}
            for item in all_matches:
                for keyword in item.get("matched_keywords", []):
                    if keyword not in keyword_stats:
                        keyword_stats[keyword] = 0
                    keyword_stats[keyword] += 1

            # 构建时间范围描述
            if start_date.date() == datetime.now().date() and start_date == end_date:
                time_range_desc = "今天"
            elif start_date == end_date:
                time_range_desc = start_date.strftime("%Y-%m-%d")
            else:
                time_range_desc = f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"

            return {
                "success": True,
                "summary": {
                    "total_found": len(all_matches),
                    "returned_count": len(results),
                    "time_range": time_range_desc,
                    "keyword_statistics": keyword_stats
                },
                "results": results
            }

        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }

    def _check_keyword_match(
        self,
        title: str,
        all_keywords: List[str],
        core_keywords: List[str]
    ) -> Dict:
        """
        检查标题是否匹配关键词

        Args:
            title: 新闻标题
            all_keywords: 所有关键词列表
            core_keywords: 核心关键词列表

        Returns:
            匹配结果字典
        """
        title_lower = title.lower()
        matched_keywords = []
        priority = 99  # 默认低优先级

        for keyword in all_keywords:
            if keyword.lower() in title_lower:
                matched_keywords.append(keyword)
                # 核心关键词优先级更高
                if keyword in core_keywords:
                    priority = min(priority, 1)
                else:
                    priority = min(priority, 2)

        return {
            "matched": len(matched_keywords) > 0,
            "matched_keywords": matched_keywords,
            "priority": priority
        }

    def get_spacex_highlights(
        self,
        date_range: Optional[Dict[str, str]] = None,
        limit: int = 20
    ) -> Dict:
        """
        获取SpaceX/马斯克相关重点内容

        Args:
            date_range: 日期范围
            limit: 返回条数限制

        Returns:
            SpaceX重点内容字典
        """
        if not self.config.get("enabled", False):
            return {
                "success": False,
                "error": {
                    "code": "TRACKING_DISABLED",
                    "message": "商业航天追踪功能未启用"
                }
            }

        spacex_config = self.config.get("spacex_focus", {})
        if not spacex_config.get("enabled", False):
            return {
                "success": False,
                "error": {
                    "code": "SPACEX_FOCUS_DISABLED",
                    "message": "SpaceX重点追踪未启用"
                }
            }

        # SpaceX相关关键词
        spacex_keywords = [
            "SpaceX", "马斯克", "Elon Musk", "星舰", "Starship",
            "星链", "Starlink", "火星", "Mars", "发射", "可重复使用"
        ]

        # 搜索相关新闻
        search_result = self.search_commercial_space_news(
            date_range=date_range,
            limit=limit * 2,  # 多搜索一些，然后筛选
            include_url=True
        )

        if not search_result.get("success"):
            return search_result

        # 筛选SpaceX相关内容
        spacex_news = []
        for item in search_result.get("results", []):
            title = item.get("title", "")
            keywords = item.get("matched_keywords", [])

            # 检查是否包含SpaceX相关关键词
            if any(kw in spacex_keywords for kw in keywords):
                spacex_news.append(item)

        # 按优先级排序
        spacex_news.sort(key=lambda x: (x.get("priority", 99), x.get("rank", 999)))

        # 限制返回数量
        results = spacex_news[:limit]

        # 按关注领域分类
        focus_areas = spacex_config.get("focus_areas", [])
        categorized_results = {}
        for area in focus_areas:
            area_name = area.get("name", "")
            area_keywords = area.get("keywords", [])
            categorized_results[area_name] = []

        for item in results:
            title = item.get("title", "")
            for area in focus_areas:
                area_name = area.get("name", "")
                area_keywords = area.get("keywords", [])
                if any(kw in title for kw in area_keywords):
                    categorized_results[area_name].append(item)

        return {
            "success": True,
            "summary": {
                "total_found": len(spacex_news),
                "returned_count": len(results),
                "focus_areas": [area.get("name") for area in focus_areas]
            },
            "results": results,
            "categorized_by_focus": categorized_results
        }

    def check_reminder_time(self, current_time: datetime = None) -> Dict:
        """
        检查当前是否为提醒时间

        Args:
            current_time: 当前时间，默认使用系统时间

        Returns:
            提醒检查结果
        """
        if not self.config.get("enabled", False):
            return {
                "success": False,
                "error": {
                    "code": "TRACKING_DISABLED",
                    "message": "商业航天追踪功能未启用"
                }
            }

        if current_time is None:
            current_time = datetime.now()

        # 检查是否为工作日
        if current_time.weekday() >= 5:  # 周六(5)和周日(6)
            return {
                "success": True,
                "is_reminder_time": False,
                "reason": "非工作日"
            }

        # 检查是否在提醒时段
        reminder_schedule = self.config.get("reminder_schedule", [])
        current_time_only = current_time.time()

        for reminder in reminder_schedule:
            reminder_time_str = reminder.get("time", "")
            try:
                reminder_time = datetime.strptime(reminder_time_str, "%H:%M").time()

                # 允许前后5分钟的误差
                time_diff = abs(
                    (current_time.hour * 60 + current_time.minute) -
                    (reminder_time.hour * 60 + reminder_time.minute)
                )

                if time_diff <= 5:
                    return {
                        "success": True,
                        "is_reminder_time": True,
                        "reminder": reminder,
                        "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S")
                    }

            except Exception:
                continue

        return {
            "success": True,
            "is_reminder_time": False,
            "reason": "不在提醒时段",
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_quick_reference(self) -> Dict:
        """
        获取商业航天追踪快速参考清单

        Returns:
            快速参考字典
        """
        if not self.config.get("enabled", False):
            return {
                "success": False,
                "error": {
                    "code": "TRACKING_DISABLED",
                    "message": "商业航天追踪功能未启用"
                }
            }

        return {
            "success": True,
            "quick_reference": {
                "core_targets": [
                    "钱塘号",
                    "箭元科技",
                    "SpaceX",
                    "马斯克"
                ],
                "core_keywords": self.config.get("keyword_priorities", {}).get("core_keywords", {}).get("keywords", []),
                "tier1_sources": [
                    "杭州市政府官网",
                    "钱塘区政府产业园区公告",
                    "箭元科技官方网站/公众号",
                    "钱塘发布官方公众号",
                    "SpaceX官方网站/X/YouTube",
                    "埃隆·马斯克个人X账号",
                    "杭萧钢构、航天电子等上市公司公告"
                ],
                "spacex_focus_areas": [
                    "与中国商业航天的竞争格局",
                    "技术路线对比分析",
                    "全球发射市场份额变化",
                    "星舰发射进展",
                    "星链部署进展",
                    "马斯克核心言论"
                ],
                "reminder_schedule": self.config.get("reminder_schedule", [])
            }
        }
