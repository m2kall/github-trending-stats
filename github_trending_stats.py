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
        """保存统计结果到JSON和README"""
        # 保存JSON统计数据
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
        
        # 更新README.md
        self.update_readme(stats, period)
        
        print(f"Saved {period} stats to {json_filename}")

    def update_readme(self, stats, period):
        """更新README.md文件"""
        detailed = (period == "yearly")
        content = f"# GitHub Trending Repositories ({period.capitalize()})\n\n"
        
        for repo in stats:
            content += f"## [{repo['name']}]({repo['url']})\n"
            content += f"**Description**: {repo['description']}\n\n"
            content += f"**Stars**: {repo['stars']}\n\n"
            content += f"**Created At**: {repo['created_at']}\n\n"
            content += f"**Owner**: [{repo['owner']['login']}]({repo['owner']['url']})\n\n"
            content += f"![Owner's Avatar]({repo['owner']['avatar_url']})\n\n"
            
            if detailed:
                content += f"**Language**: {repo['language']}\n\n"
                content += f"**Forks**: {repo['forks']}\n\n"
                content += f"**Issues**: {repo['issues']}\n\n"
        
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

if __name__ == '__main__':
    stats = GitHubTrendingStats()
    stats.run()
