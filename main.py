from fasthtml.common import *
from core import *

app, rt = fast_app(hdrs=(MarkdownJS(),))


@rt('/update')
def get():
    return Titled("Releases added", 
        Div(*[Release(o) for o in fetch_github_releases()]),
        P(A("Back", href="/"))
    )


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
        Div(hx_boost="true")(
            Projects(),
            Div(*[Release(o) for o in releasesdb(order_by='published_at desc')]),
            P(A("Github repo", href="https://github.com/pydanny/releases"))
        )
    )

@rt("/{owner:str}/{repo:str}")
def releases(session, owner: str, repo: str):
    Projects(),    
    return Titled(f"Releases for {owner}/{repo}",
        Div(hx_boost="true")(                  
            Projects(),                  
            Div(Release(o) for o in releasesdb(where=f"repo='{repo}'", order_by='published_at desc')),
            P(A("Github repo", href="https://github.com/pydanny/releases"))
        )
    )
    


serve()