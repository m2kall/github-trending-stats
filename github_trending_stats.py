import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

class GitHubTrendingStats:
    def __init__(self):
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}'
        }
        self.base_url = 'https://api.github.com'
        self.output_dir = Path('stats')
        self.output_dir.mkdir(exist_ok=True)
        self.all_stats = {}

    def get_trending_repositories(self, since='weekly'):
        """获取GitHub trending repositories"""
        url = f'https://api.github.com/search/repositories'
        
        # 计算时间范围
        now = datetime.now()
        if since == 'weekly':
            date_from = now - timedelta(days=7)
            limit = 10
        elif since == 'monthly':
            date_from = now - timedelta(days=30)
            limit = 10  # 修改月度榜单的限制为10个
        elif since == 'quarterly':
            date_from = now - timedelta(days=90)
            limit = 10
        elif since == 'yearly':
            date_from = now - timedelta(days=365)
            limit = 3
        else:
            date_from = now - timedelta(days=1)
            limit = 10

        date_query = date_from.strftime('%Y-%m-%d')
        
        # 构建查询参数，移除特定类别的限制
        query = f'created:>{date_query}'
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': limit
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            repos = response.json()['items']
            
            # 过滤掉私有仓库
            public_repos = [repo for repo in repos if not repo['private']]
            
            # 获取每个仓库的社交预览图
            for repo in public_repos:
                try:
                    # 获取仓库详细信息，包括社交预览图
                    repo_url = f"{self.base_url}/repos/{repo['full_name']}"
                    repo_response = requests.get(repo_url, headers=self.headers)
                    repo_response.raise_for_status()
                    repo_data = repo_response.json()
                    
                    # 添加社交预览图 URL
                    repo['social_preview_url'] = f"https://opengraph.githubassets.com/1/{repo['full_name']}"
                except Exception as e:
                    print(f"Error fetching social preview for {repo['full_name']}: {e}")
                    repo['social_preview_url'] = None
            
            return public_repos
        except Exception as e:
            print(f"Error fetching trending repositories: {e}")
            return []

    def save_stats(self, repos, period):
        """保存统计结果到JSON"""
        stats = []
        for repo in repos:
            stats.append({
                'name': repo['full_name'],
                'description': repo['description'],
                'stars': repo['stargazers_count'],
                'language': repo['language'],
                'url': repo['html_url'],
                'created_at': repo['created_at'],
                'owner': {
                    'login': repo['owner']['login'],
                    'url': repo['owner']['html_url'],
                    'avatar_url': repo['owner']['avatar_url']
                },
                'forks': repo['forks_count'],
                'issues': repo['open_issues_count'],
                'social_preview_url': repo.get('social_preview_url')
            })

        # 保存JSON文件
        timestamp = datetime.now().strftime('%Y%m%d')
        json_filename = self.output_dir / f'{period}_trending_{timestamp}.json'
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        # 保存到内存中用于更新README
        self.all_stats[period] = stats
        
        print(f"Saved {period} stats to {json_filename}")

    def update_readme(self):
        """更新README.md文件，显示所有时期的数据"""
        content = "# GitHub 热门项目统计\n\n"
        content += "## 项目简介\n\n"
        content += "这是一个自动追踪 GitHub 热门项目的统计工具，每周自动更新。统计维度包括：\n\n"
        content += "- 📊 **周榜**：过去7天内创建的最受欢迎项目（TOP 10）\n"
        content += "- 📈 **月榜**：过去30天内创建的最受欢迎项目（TOP 10）\n"
        content += "- 📉 **季榜**：过去90天内创建的最受欢迎项目（TOP 10）\n"
        content += "- 🏆 **年榜**：过去365天内创建的最受欢迎项目（TOP 3）\n\n"
        
        # 添加最后更新时间
        content += f"🕒 **最后更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "---\n\n"
        
        # 按时间维度顺序显示
        periods = ['weekly', 'monthly', 'quarterly', 'yearly']
        period_names = {
            'weekly': '周榜 (过去7天)',
            'monthly': '月榜 (过去30天)',
            'quarterly': '季榜 (过去90天)',
            'yearly': '年榜 (过去365天)'
        }
        
        for period in periods:
            if period in self.all_stats:
                content += f"# 📊 {period_names[period]}\n\n"
                
                for idx, repo in enumerate(self.all_stats[period], 1):
                    content += f"## {idx}. [{repo['name']}]({repo['url']})\n\n"
                    
                    # 添加项目预览图
                    if repo.get('social_preview_url'):
                        content += f"![项目预览图]({repo['social_preview_url']})\n\n"
                    
                    if repo['description']:
                        content += f"📝 **项目描述**: {repo['description']}\n\n"
                    
                    content += f"⭐ **获得 Star**: {repo['stars']:,}\n\n"
                    
                    if repo['language']:
                        content += f"💻 **主要编程语言**: {repo['language']}\n\n"
                    
                    content += f"📅 **创建时间**: {repo['created_at'][:10]}\n\n"
                    content += f"👤 **作者**: [{repo['owner']['login']}]({repo['owner']['url']})\n\n"
                    content += f"🔄 **Fork 数量**: {repo['forks']:,}\n\n"
                    content += f"⚠️ **未解决 Issues**: {repo['issues']:,}\n\n"
                    content += "---\n\n"
        
        # 添加项目信息
        content += "# ℹ️ 关于本项目\n\n"
        content += "## 🔄 自动更新机制\n\n"
        content += "- 🤖 本项目由 GitHub Actions 自动运行\n"
        content += "- ⏰ 每周日早上8点（北京时间）自动更新数据\n"
        content += "- 📊 统计数据分为：周榜、月榜、季榜、年榜\n"
        content += "- 💾 历史数据以 JSON 格式存储在 [stats](./stats) 目录\n\n"
        
        content += "## 📋 统计规则\n\n"
        content += "1. **数据来源**：GitHub API\n"
        content += "2. **排序依据**：按照 Star 数量降序排序\n"
        content += "3. **统计范围**：\n"
        content += "   - 周榜：采集过去7天内创建的项目，展示前10名\n"
        content += "   - 月榜：采集过去30天内创建的项目，展示前10名\n"
        content += "   - 季榜：采集过去90天内创建的项目，展示前10名\n"
        content += "   - 年榜：采集过去365天内创建的项目，展示前3名\n"
        content += "4. **更新频率**：每周自动更新一次\n\n"
        
        content += "## 🤝 贡献指南\n\n"

        content += "欢迎提交 Issue 或 Pull Request 来改进这个项目！\n\n"
        content += "如果这个项目对你有帮助，欢迎给它一个 Star ⭐\n"
        
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(content)

    def run(self):
        """运行统计任务"""
        periods = {
            'weekly': 'weekly',
            'monthly': 'monthly',
            'quarterly': 'quarterly',
            'yearly': 'yearly'
        }

        for period_name, period_value in periods.items():
            print(f"Fetching {period_name} trending repositories...")
            repos = self.get_trending_repositories(period_value)
            self.save_stats(repos, period_name)
        
        # 更新README
        self.update_readme()

if __name__ == '__main__':
    stats = GitHubTrendingStats()
    stats.run()
