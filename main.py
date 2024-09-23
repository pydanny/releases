import asyncio
from fasthtml.common import *
from core import *
# from fa6_icons import svgs as icons

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
        Header(
            Span(style="float: right;")(Small(A("(all releases)", href=f"/{release.owner}/{release.repo}"))),            
            H2(A(f"{release.owner}/{release.repo} {release.tag_name}", href=release.url )),
            P(Strong(release.published_at)),
            
        ),
        Div(cls='marked')(release.body)
    )  

def S(e):
    return Span(e, ' ')

def Projects():
    return P(S(A("all", href="/")), *[S(A(f"{owner}/{repo}", href=f"/{owner}/{repo}")) for owner, repo in PROJECTS])

def _gridify_releases(releases):
    grids = []
    for pair in chunked(releases, chunk_sz=2):
        grids.append(Div(cls='grid')(
            *[Div(cls='cell')(Release(o)) for o in pair]
        ))
    return grids

@rt('/')
def index():
    releases = []
    for _, repo in PROJECTS:
        releases.append(releasesdb(where=f"repo='{repo}'", order_by='published_at desc')[0])
    releases = sorted(releases, key=lambda r: r.published_at, reverse=True)


    return Titled("Releases @ answer.ai & fast.ai",
        Div(hx_boost="true")(
            Projects(),
            P("Latest releases:"),
            *_gridify_releases(releases),
            P(
                S(A("Github repo", href="https://github.com/pydanny/releases")),
                A("Update", href='/update'),
            ),
        )
    )

@rt("/{owner:str}/{repo:str}")
def releases(owner: str, repo: str):
    Projects(),    
    releases = releasesdb(where=f"repo='{repo}'", order_by='published_at desc')
    return Titled(f"Releases for {owner}/{repo}",
        Div(hx_boost="true")(                  
            Projects(),                  
            *_gridify_releases(releases),
            P(A("Github repo", href="https://github.com/pydanny/releases"))
        )
    )
    


serve()