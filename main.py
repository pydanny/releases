import asyncio
from fasthtml.common import *
from core import *

sselink = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")

app, rt = fast_app(hdrs=(MarkdownJS(), sselink))


@rt('/update')
def get():
    return Titled("Releases added", 
        Div(hx_ext="sse", sse_connect="/update-fragment",
            hx_swap="beforeend show:bottom",
            sse_swap="message", id="message-container",),
        P(A("Back", href="/"))
    )

shutdown_event = signal_shutdown()

async def version_generator():
    # while not shutdown_event.is_set():
    async for release in fetch_github_releases():
        yield sse_message(Release(release))
        await asyncio.sleep(1)

@rt('/update-fragment')
async def get():
    return EventStream(version_generator())


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