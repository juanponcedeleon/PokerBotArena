"""Find bots. A bot is a directory holding `agent.py`; its label is the directory name.

Resolution order for a name given on the command line:

1. An existing directory (absolute, or relative to the current directory or the repo root).
2. `bots/<name>` in the repo.
3. `starter-kit/examples/<name>` (the sparring partners `check_or_fold`, `min_raiser`).
4. `bot` (the repo's submission folder) when the name is `bot`.

`label=path` gives an explicit label; two bots with the same directory name get `name@2`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POOL_DIR = REPO / "bots"
EXAMPLES_DIR = REPO / "starter-kit" / "examples"
SUBMISSION_DIR = REPO / "bot"


@dataclass(frozen=True, slots=True)
class BotRef:
    label: str
    path: Path  # Directory holding agent.py.

    @property
    def agent_file(self) -> Path:
        return self.path / "agent.py"

    def fingerprint(self) -> str:
        """SHA-256 of every regular file in the directory, so a result can always be tied to
        the exact code that produced it."""
        digest = hashlib.sha256()
        for file in sorted(p for p in self.path.rglob("*") if p.is_file()):
            if "__pycache__" in file.parts:
                continue
            digest.update(str(file.relative_to(self.path)).encode())
            digest.update(file.read_bytes())
        return digest.hexdigest()[:16]


def is_bot_dir(path: Path) -> bool:
    return path.is_dir() and (path / "agent.py").is_file()


def resolve(name: str) -> BotRef:
    label, _, target = name.partition("=")
    if not target:
        label, target = "", name
    candidates = [Path(target), REPO / target, POOL_DIR / target, EXAMPLES_DIR / target]
    if target == "bot":
        candidates.append(SUBMISSION_DIR)
    for candidate in candidates:
        if is_bot_dir(candidate):
            path = candidate.resolve()
            return BotRef(label or path.name, path)
    known = ", ".join(p.label for p in pool(examples=True))
    raise FileNotFoundError(
        f"No bot named {target!r}: give a directory with agent.py, a name under bots/, "
        f"or one of: {known}."
    )


def pool(*, examples: bool = False) -> list[BotRef]:
    """Every bot in bots/, optionally plus the starter kit's examples."""
    found = []
    if POOL_DIR.is_dir():
        found += [BotRef(p.name, p.resolve()) for p in sorted(POOL_DIR.iterdir()) if is_bot_dir(p)]
    if examples and EXAMPLES_DIR.is_dir():
        found += [
            BotRef(p.name, p.resolve()) for p in sorted(EXAMPLES_DIR.iterdir()) if is_bot_dir(p)
        ]
    return found


def unique_labels(refs: list[BotRef]) -> list[BotRef]:
    """Distinct labels: a second bot with the same directory name becomes `name@2`."""
    seen: dict[str, int] = {}
    out = []
    for ref in refs:
        count = seen.get(ref.label, 0) + 1
        seen[ref.label] = count
        out.append(ref if count == 1 else BotRef(f"{ref.label}@{count}", ref.path))
    return out


def resolve_many(
    names: list[str], *, all_pool: bool = False, examples: bool = False
) -> list[BotRef]:
    """Named bots first, then (with `all_pool`) the rest of bots/ and optionally the examples.
    One entry per directory: seat counts are the plan's business, not the pool's."""
    refs = [resolve(name) for name in names]
    if all_pool:
        have = {ref.path for ref in refs}
        refs += [ref for ref in pool(examples=examples) if ref.path not in have]
    distinct: list[BotRef] = []
    for ref in refs:
        if ref.path not in {d.path for d in distinct}:
            distinct.append(ref)
    return unique_labels(distinct)
