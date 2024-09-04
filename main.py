import requests
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 깃허브 스타수 혹은 포크수로 정렬된 크레이트 목록을 100개 가져오기
def get_repositories(sort_by, page):
    # GitHub API 엔드포인트
    search_url = "https://api.github.com/search/repositories"

    params = {"q": "language:rust", "order": "desc", "per_page": 100, "page": page, "sort": sort_by}

    headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(search_url, params=params, headers=headers)
    return response.json()

# crates.io 다운로드수로 정렬된 크레이트 목록을 100개 가져오기
def get_crates(page):
    # crates.io 엔드포인트
    crates_url = "https://crates.io/api/v1/crates"
    params = {
        "sort": "downloads",
        "per_page": 100,
        "page": page
    }

    response = requests.get(crates_url, params=params)
    return response.json()


# 깃허브 스타수, 포크수, 크레이트 다운로드수로 정렬된 크레이트에서 공통된 크레이트를 찾는 함수, repository와 html_url이 같으면 공통된 것
def get_common_crates():
    common_crates = []
    repositories = {}
    crates = []
    for i in range(1, 11): # 10페이지까지 크레이트를 가져옴
        for repo in get_repositories("stars", i)["items"]:
            repositories[repo["html_url"]] = repo
        for repo in get_repositories("forks", i)["items"]:
            repositories[repo["html_url"]] = repo
        crates += get_crates(i)["crates"]

    for repository in repositories.values():
        for crate in crates:
            if repository["html_url"] == crate["repository"]:
                common_crates.append({
                    "name": crate["name"],
                    "downloads": crate["downloads"],
                    "repository": crate["repository"],
                    "stars": repository["stargazers_count"],
                    "forks": repository["forks"]
                })

    return common_crates

common_crates = get_common_crates()

df = pd.DataFrame(common_crates)
df.to_excel("crates.xlsx", index=False)