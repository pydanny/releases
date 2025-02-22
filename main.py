import asyncio
from fasthtml.common import *
from core import *
from monsterui.all import *

sselink = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")
hdrs = [MarkdownJS(), sselink] + Theme.blue.headers()

app, rt = fast_app(hdrs=hdrs, pico=False)


@rt('/update')
def get():
    return (
        Container(
            H1("Releases added"),            
            Grid(hx_ext="sse", sse_connect="/update-fragment",
                hx_swap="beforeend show:bottom",
                sse_swap="message", id="message-container",
                cls=('gap-x-5 gap-y-5 lg:grid-cols-3 md:grid-cols-2'),
                cols=1,
                uk_grid="masonry: next"
            ),
            UkIconLink('chevrons-left', href=index),
        )
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
    return Card(
        Div(render_md(release.body)),
        header=Div(
            Div(
                H2(A(f"{release.owner}/{release.repo} {release.tag_name}", href=release.url )),
                P(release.published_at),
                P(A(f"All releases for {release.repo}", href=f"/{release.owner}/{release.repo}", cls=AT.muted))
            ),
        ),

    )  

def S(e):
    return Span(e, ' ')

def Releases(releases):
    return Grid(
            *[Release(r) for r in releases],
            cls=('gap-x-5 gap-y-5 lg:grid-cols-3 md:grid-cols-2'),
            cols=1
    )

@rt('/')
def index():
    releases = []
    for _, repo in PROJECTS:
        # Only append if there's releases listed for something
        try: releases.append(releasesdb(where=f"repo='{repo}'", order_by='published_at desc')[0])
        except IndexError: continue
    releases = sorted(releases, key=lambda r: r.published_at, reverse=True)
    return (
        Container(
            H1("Releases @ answer.ai & fast.ai"),
            Div(
                Releases(releases),
                P(
                    S(A("Github repo", href="https://github.com/pydanny/releases")),
                    A("Update", href='/update'),
                ),
            ),
            # cls=[ContainerT.xlarge, 'space-y-5 mb-20']
        )

    )

@rt("/{owner:str}/{repo:str}")
def releases(owner: str, repo: str):
    releases = releasesdb(where=f"repo='{repo}'", order_by='published_at desc')
    return (
        Container(                  
            H1(f"Releases for {owner}/{repo}"),              
            Releases(releases),
            LAlignedDiv(UkIconLink('chevrons-left', href=index), A("Github repo", href="https://github.com/pydanny/releases")),
            cls=[ContainerT.xlarge, 'space-y-5 mb-20']
        )
    )
    


serve()