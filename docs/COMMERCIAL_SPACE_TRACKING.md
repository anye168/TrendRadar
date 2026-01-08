# 商业航天全网追踪功能使用说明

## 功能概述

商业航天全网追踪功能为TrendRadar新增了针对商业航天领域的专项追踪能力，包括SpaceX、马斯克、钱塘号、箭元科技等核心标的的优先级追踪。

## 核心特性

### 1. 信源检索优先级

系统按照四个梯队进行信源检索：

#### 第一梯队（核心权威信源，必查）
- 杭州市政府官网
- 钱塘区政府产业园区公告
- 箭元科技官方网站/公众号
- 钱塘发布官方公众号
- SpaceX官方网站/X/YouTube
- 埃隆·马斯克个人X账号
- 杭萧钢构、航天电子等上市公司公告

#### 第二梯队（权威媒体信源，重点查）
- 新华社
- 科技日报
- 科创板日报
- 杭州新闻
- 潮新闻

#### 第三梯队（行业垂直信源，补充查）
- 航天爱好者网
- 商业航天观察
- 产业链配套企业官方账号

#### 第四梯队（社交媒体信源，筛选查）
- 微博热搜
- 知乎话题
- 抖音企业官方账号

### 2. 关键词检索优先级

#### 核心绑定关键词（精准匹配，优先触发提醒）
- 钱塘号
- 箭元科技
- 商业航天
- 超级工厂
- 火箭回收
- 箭体结构件
- SpaceX
- 马斯克
- Elon Musk
- 星舰
- Starship

#### 拓展关联关键词（补充匹配，丰富信息维度）
- 重大项目开工
- 产业签约
- 航天产业链
- 高端装备制造
- 新材料供应
- 临海产业基地
- 星链
- Starlink
- 可重复使用火箭
- Gigafactory
- IPO计划
- 火星计划
- Mars Mission

### 3. SpaceX/马斯克特别关注

系统特别关注以下领域：
- 与中国商业航天的竞争格局
- 技术路线对比分析
- 全球发射市场份额变化
- 星舰发射进展
- 星链部署进展
- 马斯克核心言论

### 4. 工作日提醒机制

系统在工作日的三个时段进行提醒：
- 09:00 - 早间提醒
- 14:00 - 下午提醒
- 18:00 - 晚间提醒

## 配置文件说明

### 配置文件位置

```
TrendRadar/config/commercial_space_tracking.yaml
```

### 主要配置项

#### 启用/禁用追踪

```yaml
enabled: true  # 设置为false可禁用追踪功能
```

#### 修改提醒时段

```yaml
reminder_schedule:
  - time: "09:00"
    description: "早间提醒"
  - time: "14:00"
    description: "下午提醒"
  - time: "18:00"
    description: "晚间提醒"
```

#### 添加自定义信源

```yaml
source_priorities:
  tier1:
    sources:
      - name: "新信源名称"
        url: "https://example.com"
        type: "company_official"
        description: "信源描述"
```

#### 添加自定义关键词

```yaml
keyword_priorities:
  core_keywords:
    keywords:
      - "新关键词1"
      - "新关键词2"
```

## 使用方法

### 方法1：通过Python代码使用

```python
from TrendRadar.mcp_server.tools.commercial_space_tracking import CommercialSpaceTracking

# 初始化追踪工具
tracker = CommercialSpaceTracking()

# 获取追踪配置
config = tracker.get_tracking_config()

# 搜索商业航天新闻
results = tracker.search_commercial_space_news(
    date_range={"start": "2025-01-01", "end": "2025-01-07"},
    limit=50,
    include_url=True
)

# 获取SpaceX重点内容
spacex_highlights = tracker.get_spacex_highlights(
    date_range={"start": "2025-01-01", "end": "2025-01-07"},
    limit=20
)

# 检查是否为提醒时间
reminder_check = tracker.check_reminder_time()

# 获取快速参考清单
quick_ref = tracker.get_quick_reference()
```

### 方法2：通过MCP服务器使用

如果已配置MCP服务器，可以通过以下方式调用：

```bash
# 搜索商业航天新闻
mcp call search_commercial_space_news --date-range '{"start":"2025-01-01","end":"2025-01-07"}' --limit 50

# 获取SpaceX重点内容
mcp call get_spacex_highlights --date-range '{"start":"2025-01-01","end":"2025-01-07"}' --limit 20

# 检查提醒时间
mcp call check_reminder_time

# 获取快速参考
mcp call get_quick_reference
```

### 方法3：集成到现有爬虫流程

在现有爬虫流程中添加商业航天追踪：

```python
# 在爬虫主流程中添加
from TrendRadar.mcp_server.tools.commercial_space_tracking import CommercialSpaceTracking

# 初始化
tracker = CommercialSpaceTracking()

# 每次爬取后检查
if tracker.check_reminder_time()["is_reminder_time"]:
    # 获取最新商业航天新闻
    results = tracker.search_commercial_space_news(limit=50)
    
    # 如果有匹配内容，发送通知
    if results["results"]:
        # 发送通知逻辑
        send_notification(results)
```

## 执行规则

### 检索顺序
1. 先按信源优先级检索
2. 再按关键词优先级匹配

### 去重规则
- 相同信息以第一梯队信源为准
- 自动剔除重复内容

### 内容过滤
- 仅保留与商业航天产业、核心标的相关的有效信息
- 排除不相关内容

### 提醒触发条件
- **第一梯队**：匹配任何关键词即触发
- **第二梯队**：需要核心关键词
- **第三梯队**：需要多个关键词匹配
- **第四梯队**：需要交叉验证

## 输出格式

### 搜索结果示例

```json
{
  "success": true,
  "summary": {
    "total_found": 15,
    "returned_count": 10,
    "time_range": "今天",
    "keyword_statistics": {
      "SpaceX": 8,
      "马斯克": 5,
      "商业航天": 3
    }
  },
  "results": [
    {
      "title": "SpaceX星舰成功完成第7次试飞",
      "platform": "weibo",
      "platform_name": "微博",
      "date": "2025-01-08",
      "matched_keywords": ["SpaceX", "星舰"],
      "priority": 1,
      "ranks": [1],
      "count": 1,
      "rank": 1
    }
  ]
}
```

### SpaceX重点内容示例

```json
{
  "success": true,
  "summary": {
    "total_found": 8,
    "returned_count": 5,
    "focus_areas": [
      "与中国商业航天的竞争格局",
      "技术路线对比分析",
      "全球发射市场份额变化"
    ]
  },
  "results": [...],
  "categorized_by_focus": {
    "与中国商业航天的竞争格局": [...],
    "技术路线对比分析": [...]
  }
}
```

## 快速参考清单

### 核心标的
- 钱塘号
- 箭元科技
- SpaceX
- 马斯克

### 核心关键词
- 钱塘号
- 箭元科技
- 商业航天
- 超级工厂
- 火箭回收
- 箭体结构件
- SpaceX
- 马斯克
- Elon Musk
- 星舰
- Starship

### 第一梯队信源
- 杭州市政府官网
- 钱塘区政府产业园区公告
- 箭元科技官方网站/公众号
- 钱塘发布官方公众号
- SpaceX官方网站/X/YouTube
- 埃隆·马斯克个人X账号
- 杭萧钢构、航天电子等上市公司公告

### SpaceX关注领域
- 与中国商业航天的竞争格局
- 技术路线对比分析
- 全球发射市场份额变化
- 星舰发射进展
- 星链部署进展
- 马斯克核心言论

## 故障排除

### 功能未启用

如果收到"商业航天追踪功能未启用"错误：

1. 检查配置文件是否存在
2. 确认配置文件中`enabled`设置为`true`
3. 检查配置文件格式是否正确

### 无关键词配置

如果收到"未配置追踪关键词"错误：

1. 检查配置文件中的`keyword_priorities`部分
2. 确保至少有一个关键词列表不为空

### 无可用数据

如果收到"没有可用的新闻数据"错误：

1. 确保爬虫已运行并生成了数据
2. 检查`output`目录下是否有数据文件
3. 确认日期范围是否正确

## 扩展开发

### 添加新的追踪主题

1. 创建新的配置文件（如`config/new_tracking.yaml`）
2. 复制`commercial_space_tracking.py`并修改类名
3. 更新关键词配置文件
4. 在MCP服务器中注册新工具

### 自定义通知渠道

在配置文件的`notification`部分添加自定义渠道：

```yaml
notification:
  channels:
    - "feishu"
    - "dingtalk"
    - "custom_channel"  # 自定义渠道
```

## 技术支持

如有问题或建议，请通过以下方式联系：

- GitHub Issues
- 项目文档
- 技术支持邮箱

## 更新日志

### v1.0.0 (2025-01-08)
- 初始版本发布
- 支持商业航天全网追踪
- 支持SpaceX/马斯克特别关注
- 支持工作日提醒机制
- 支持信源和关键词优先级管理
