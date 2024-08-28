from fasthtml.common import *
from dataclasses import dataclass
import pathlib
from ghapi.all import GhApi
from os import getenv


GITHUB_TOKEN = getenv("RELEASES_GH_TOKEN")

app, rt = fast_app(hdrs=(MarkdownJS(),))

setup_toasts(app)

db = Database('data/releases.db')

PROJECTS = (
    ('answerdotai', 'fasthtml'),
    ('answerdotai', 'fastlite'),
)

@dataclass
class Release: id: int; url: str; tag_name: str; published_at: str; body: str; owner: str; repo: str

releasesdb = db.create(Release)


def get_github_releases(session) -> list:
    for project in PROJECTS:
        owner, repo = project
        for release in GhApi(owner=owner, repo=repo, token=GITHUB_TOKEN).repos.list_releases():
            if release['id'] not in releasesdb:
                releasesdb.insert(Release(
                    id = release['id'],
                    url = release['html_url'],
                    tag_name = release['tag_name'],
                    published_at = release['published_at'],
                    body = release['body'],
                    owner = owner,
                    repo = repo
                ))
                add_toast(session, f"Release {release['tag_name']} for {owner}/{repo}", "info")

@rt('/update')
def get(session):
    # TODO: replace with webhook receiver
    get_github_releases(session)
    return RedirectResponse("/")


def Release(release):
    return Article(
        H2(A(f"{release.owner}/{release.repo} {release.tag_name}", href=release.url)),
        P(Strong(release.published_at)),
        Div(cls='marked')(release.body)
    )  

def Projects():
    # TODO: replace with HTMX-powered fetching
    return P(A("all", href="/"), *[A(f"{owner}/{repo}", href=f"/{owner}/{repo}") for owner, repo in PROJECTS])


@rt('/')
def index(session):
    return Titled("Releases @ answer.ai & fast.ai",
            Projects(),
            Div(*[Release(o) for o in releasesdb(order_by='published_at desc')])
    )

@rt("/{owner:str}/{repo:str}")
def releases(session, owner: str, repo: str):
    # TODO turn into HTMX fragment
    Projects(),    
    return Titled(f"Releases for {owner}/{repo}",
            Projects(),                  
            Div(Release(o) for o in releasesdb(where=f"repo='{repo}'", order_by='published_at desc'))
    )
    


serve()