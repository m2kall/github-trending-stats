import requests
import datetime

def fetch_trending_repos(since, limit=10):
   url = f"https://api.github.com/search/repositories?q=created:>{since}&sort=stars&order=desc&per_page={limit}"
   response = requests.get(url)
   return response.json()['items']

def save_to_readme(repos, period, detailed=False):
   filename = "README.md"
   with open(filename, 'w', encoding='utf-8') as f:
       f.write(f"# GitHub Trending Repositories ({period.capitalize()})\n\n")
       for repo in repos:
           f.write(f"## [{repo['name']}]({repo['html_url']})\n")
           f.write(f"**Description**: {repo['description']}\n\n")
           f.write(f"**Stars**: {repo['stargazers_count']}\n\n")
           f.write(f"**Created At**: {repo['created_at']}\n\n")
           f.write(f"**Owner**: [{repo['owner']['login']}]({repo['owner']['html_url']})\n\n")
           if 'html_url' in repo['owner']:
               f.write(f"![Owner's Avatar]({repo['owner']['avatar_url']})\n\n")
           if detailed:
               f.write(f"**Language**: {repo['language']}\n\n")
               f.write(f"**Forks**: {repo['forks_count']}\n\n")
               f.write(f"**Issues**: {repo['open_issues_count']}\n\n")

if __name__ == "__main__":
   today = datetime.datetime.now().date()
   periods = {
       "weekly": (today - datetime.timedelta(days=7)).isoformat(),
       "monthly": (today - datetime.timedelta(days=30)).isoformat(),
       "quarterly": (today - datetime.timedelta(days=90)).isoformat(),
       "yearly": (today - datetime.timedelta(days=365)).isoformat(),
   }

   for period, date in periods.items():
       if period == "weekly":
           limit = 10
       elif period == "monthly":
           limit = 30
       elif period == "yearly":
           limit = 3
       else:
           limit = 10

       repos = fetch_trending_repos(date, limit)
       save_to_readme(repos, period, detailed=(period == "yearly"))
 
