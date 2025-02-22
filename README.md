# Releases

An easy-to-follow release system for an org or project. Deployed [here](https://releases-production-5471.up.railway.app).

## Installation

In a virtual environment, install packages in `requirements.txt`:

```
pip install -r requirements.txt
```

## Usage

Set the PROJECTS structure to what you want to observe. Then run:

```
python main.py
```

## New model

@dataclass
class Item:
    id: int
    url: str
    tag_name: str
    published_at: str
    body: str
    owner: str
    repo: str