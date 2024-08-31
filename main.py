import asyncio
from fasthtml.common import *
from core import *
from sse_starlette.sse import EventSourceResponse

sselink = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")

app, rt = fast_app(hdrs=(MarkdownJS(), sselink))


@rt('/update')
def get():
    return Titled("Releases added", 
        Div(hx_ext="sse", sse_connect="/update-fragment",
            hx_swap="beforeend show:bottom", sse_swap="VersionUpdate", id="message-container",),
        P(A("Back", href="/"))
    )

async def version_generator():
    while True:
        async for release in fetch_github_releases():
            yield {"data": to_xml(Release(release)), "event": "VersionUpdate"}
            await asyncio.sleep(1)
        await asyncio.sleep(1)
        yield {"data": "", "event": "VersionUpdate"}

@rt('/update-fragment')
async def get():
    return EventSourceResponse(version_generator(), media_type="text/event-stream")


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
            P(
                A("Github repo", href="https://github.com/pydanny/releases"),
                A("Update", href='/update'),
            ),
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