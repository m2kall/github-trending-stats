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
            limit = 30
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
        
        # 构建查询参数
        query = f'created:>{date_query} sort:stars'
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': limit
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()['items']
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
                'issues': repo['open_issues_count']
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
        content = "# GitHub Trending Statistics\n\n"
        content += "自动统计GitHub趋势项目的数据分析工具。该工具会定期收集不同时间维度的热门项目信息。\n\n"
        
        # 添加最后更新时间
        content += f"最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 按时间维度顺序显示
        periods = ['weekly', 'monthly', 'quarterly', 'yearly']
        period_names = {
            'weekly': '周榜',
            'monthly': '月榜',
            'quarterly': '季榜',
            'yearly': '年榜'
        }
        
        for period in periods:
            if period in self.all_stats:
                content += f"## {period_names[period]}\n\n"
                
                for repo in self.all_stats[period]:
                    content += f"### [{repo['name']}]({repo['url']})\n\n"
                    
                    if repo['description']:
                        content += f"📝 **描述**: {repo['description']}\n\n"
                    
                    content += f"⭐ **Stars**: {repo['stars']:,}\n\n"
                    
                    if repo['language']:
                        content += f"📊 **主要语言**: {repo['language']}\n\n"
                    
                    content += f"📅 **创建时间**: {repo['created_at'][:10]}\n\n"
                    content += f"👤 **作者**: [{repo['owner']['login']}]({repo['owner']['url']})\n\n"
                    content += f"![作者头像]({repo['owner']['avatar_url']})\n\n"
                    content += f"🔄 **Forks**: {repo['forks']:,}\n\n"
                    content += f"⚠️ **Issues**: {repo['issues']:,}\n\n"
                    content += "---\n\n"
        
        # 添加项目信息
        content += "## 关于本项目\n\n"
        content += "- 本项目由 GitHub Actions 自动运行\n"
        content += "- 每周日自动更新一次数据\n"
        content += "- 统计数据包括：周榜、月榜、季榜、年榜\n"
        content += "- 详细数据存储在 [stats](./stats) 目录下的 JSON 文件中\n"
        
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
