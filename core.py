from fasthtml.common import *
from dataclasses import dataclass
from ghapi.all import GhApi
from os import getenv

__all__ = ['fetch_github_releases', 'Release', 'PROJECTS', 'releasesdb']

PROJECTS = (
    ('answerdotai', 'fasthtml'),
    ('answerdotai', 'fastlite'),
    ('answerdotai', 'fa6-icons'),
    ('answerdotai', 'sqlite-minutils'),
    ('answerdotai', 'surreal'),
    ('fastai', 'fastai'),
    ('fastai', 'fastcore'),
    ('fastai', 'nbdev'),
)

db = Database('data/releases.db')

GITHUB_TOKEN = getenv("RELEASES_GH_TOKEN")

@dataclass
class Release: id: int; url: str; tag_name: str; published_at: str; body: str; owner: str; repo: str

releasesdb = db.create(Release)

def fetch_github_releases() -> list[dict]:
    for project in PROJECTS:
        owner, repo = project
        for release in GhApi(owner=owner, repo=repo, token=GITHUB_TOKEN).repos.list_releases():
            if release['id'] not in releasesdb:
                rel = dict(
                    id = release['id'],
                    url = release['html_url'],
                    tag_name = release['tag_name'],
                    published_at = release['published_at'],
                    body = release['body'],
                    owner = owner,
                    repo = repo
                )
                releasesdb.insert(**rel)
                yield rel

if __name__ == '__main__':
    for release in fetch_github_releases():
        print(f"Release {release['id']} for {release['owner']}/{release['repo']} added")