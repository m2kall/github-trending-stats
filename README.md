# GitHub Trending Stats

自动统计GitHub趋势项目的数据分析工具。该工具会定期收集不同时间维度（周、月、季度、年）的热门项目信息。

## 功能特点

- 自动收集GitHub趋势项目数据
- 支持多个时间维度的统计：
  - 每周热门项目
  - 每月热门项目
  - 每季度热门项目
  - 每年热门项目
- 数据以JSON格式保存，方便后续分析
- 使用GitHub Actions自动运行

## 项目结构

```
.
├── .github/workflows/   # GitHub Actions工作流配置
├── stats/              # 统计数据输出目录
├── github_trending_stats.py  # 主程序
└── requirements.txt    # 依赖包列表
```

## 使用方法

1. Fork 本仓库
2. 在仓库设置中添加 GITHUB_TOKEN secret
3. 启用 GitHub Actions

数据会自动保存在 `stats` 目录下，每个时间维度的数据都会单独保存在对应的JSON文件中。

## 数据格式

每个项目的统计数据包含以下信息：
- 项目名称
- 项目描述
- Star数量
- 主要编程语言
- 项目URL
- 创建时间

## 依赖

- Python 3.x
- requests
- pandas

## 自动运行

该工具通过GitHub Actions自动运行：
- 每周日自动运行收集数据
- 支持手动触发运行

## License

MIT
