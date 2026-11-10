"""Genomes: a value per tunable of a template, and how to breed and render them.

The GA operators (mutation per gene with probability `rate`, Gaussian step scaled to the gene's
range and decaying by generation, uniform crossover, repair into bounds) follow the user's
evol.py. Rendering differs: instead of `ast.unparse` (which drops every comment) the rendered
agent.py is the template's text with only the tunables' literals spliced, located by AST
positions, so a promoted bot still reads like the parent.
"""

from __future__ import annotations

import ast
import hashlib
import json
import random
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Genome = dict[str, float]


@dataclass(frozen=True)
class GeneSpec:
    name: str
    default: float
    low: float
    high: float
    int_valued: bool


@dataclass
class Template:
    dir: Path
    family: str
    parent: str  # "bots/<name>"
    strategy: str
    genes: dict[str, GeneSpec]
    constraints: list[tuple[str, str, str]]
    source: str
    spans: dict[str, tuple[int, int]]  # gene -> (start, end) character offsets of its literal

    @staticmethod
    def load(template_dir: Path) -> Template:
        spec = json.loads((template_dir / "evolve.json").read_text(encoding="utf-8"))
        source = (template_dir / "agent.py").read_text(encoding="utf-8")
        genes = {
            name: GeneSpec(name, float(p["default"]), float(p["min"]), float(p["max"]), bool(p.get("int", False)))
            for name, p in spec["parameters"].items()
        }
        spans = literal_spans(source, set(genes))
        for name, gene in genes.items():
            start, end = spans[name]
            literal = ast.literal_eval(source[start:end])
            if abs(float(literal) - gene.default) > 1e-9:
                raise ValueError(f"{template_dir}: {name} = {literal!r} in agent.py but default {gene.default} in evolve.json.")
        return Template(
            template_dir, spec["family"], spec["parent"], spec.get("strategy", ""), genes,
            [tuple(c) for c in spec.get("constraints", [])], source, spans,
        )

    def defaults(self) -> Genome:
        return {name: g.default for name, g in self.genes.items()}

    # -- GA operators ---------------------------------------------------------------------------

    def repair(self, genome: Genome) -> Genome:
        out: Genome = {}
        for name, g in self.genes.items():
            value = max(g.low, min(g.high, float(genome[name])))
            out[name] = float(int(round(value))) if g.int_valued else round(value, 6)
        for a, op, b in self.constraints:
            if op == ">=" and out[a] < out[b]:
                out[a] = out[b]
            elif op == "<=" and out[a] > out[b]:
                out[a] = out[b]
        return out

    def mutate(self, parent: Genome, rng: random.Random, scale: float, rate: float) -> Genome:
        child = dict(parent)
        changed = False
        for name, g in self.genes.items():
            if rng.random() < rate:
                child[name] += rng.gauss(0.0, scale * (g.high - g.low))
                changed = True
        if not changed:
            name = rng.choice(list(self.genes))
            g = self.genes[name]
            child[name] += rng.gauss(0.0, scale * (g.high - g.low))
        return self.repair(child)

    def crossover(self, left: Genome, right: Genome, rng: random.Random) -> Genome:
        return self.repair({name: left[name] if rng.random() < 0.5 else right[name] for name in self.genes})

    def changed_genes(self, genome: Genome) -> dict[str, tuple[float, float]]:
        return {n: (g.default, genome[n]) for n, g in self.genes.items() if abs(genome[n] - g.default) > 1e-9}

    # -- rendering ------------------------------------------------------------------------------

    def render(self, genome: Genome) -> str:
        pieces = []
        cursor = 0
        for name, (start, end) in sorted(self.spans.items(), key=lambda kv: kv[1][0]):
            g = self.genes[name]
            value = genome[name]
            literal = str(int(round(value))) if g.int_valued else repr(float(value))
            pieces.append(self.source[cursor:start])
            pieces.append(literal)
            cursor = end
        pieces.append(self.source[cursor:])
        text = "".join(pieces)
        compile(text, f"<{self.family} candidate>", "exec")
        return text

    def materialize(self, genome: Genome, folder: Path, *, note: str = "") -> Path:
        """Write a complete bot directory: the template's data files plus the rendered agent.py and
        parameters.json. Idempotent for the same genome."""
        if folder.exists():
            return folder
        folder.mkdir(parents=True)
        for item in self.dir.iterdir():
            if item.name in ("agent.py", "evolve.json", "__pycache__"):
                continue
            if item.is_dir():
                shutil.copytree(item, folder / item.name, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copy2(item, folder / item.name)
        text = self.render(genome)
        if note:
            text = text.replace("Parent docstring follows.\n", note.rstrip("\n") + "\n\nParent docstring follows.\n", 1)
        (folder / "agent.py").write_text(text, encoding="utf-8", newline="\n")
        (folder / "parameters.json").write_text(
            json.dumps({"family": self.family, "parent": self.parent, "genome_id": genome_id(genome), "parameters": genome}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return folder


def literal_spans(source: str, names: set[str]) -> dict[str, tuple[int, int]]:
    """Character offsets of the RHS literal of each module-level `NAME = <number>`."""
    tree = ast.parse(source)
    offsets = _line_offsets(source)
    spans: dict[str, tuple[int, int]] = {}
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
            continue
        name = node.targets[0].id
        if name not in names:
            continue
        value = node.value
        if isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub) and isinstance(value.operand, ast.Constant):
            pass
        elif not (isinstance(value, ast.Constant) and isinstance(value.value, int | float) and not isinstance(value.value, bool)):
            raise ValueError(f"{name} is not assigned a numeric literal at module level.")
        if name in spans:
            raise ValueError(f"{name} is assigned more than once at module level.")
        start = offsets[value.lineno - 1] + value.col_offset
        end = offsets[value.end_lineno - 1] + value.end_col_offset
        spans[name] = (start, end)
    missing = names - set(spans)
    if missing:
        raise ValueError(f"Tunables without a module-level literal: {', '.join(sorted(missing))}")
    return spans


def _line_offsets(source: str) -> list[int]:
    offsets = [0]
    for line in source.split("\n")[:-1]:
        offsets.append(offsets[-1] + len(line) + 1)
    return offsets


def genome_id(genome: Genome) -> str:
    encoded = json.dumps(genome, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:12]


def make_population(template: Template, elites: list[Genome], size: int, rng: random.Random, generation: int, *, rate: float) -> list[Genome]:
    """Elites survive unchanged; the rest are crossover + mutation children, distinct by id.
    Mutation scale decays 0.16 -> 0.05 of each gene's range over the generations (evol.py)."""
    population = [dict(g) for g in elites]
    seen = {genome_id(g) for g in population}
    scale = max(0.05, 0.16 * (0.88 ** generation))
    attempts = 0
    while len(population) < size and attempts < 1000:
        attempts += 1
        child = template.crossover(rng.choice(elites), rng.choice(elites), rng)
        child = template.mutate(child, rng, scale, rate)
        cid = genome_id(child)
        if cid not in seen:
            population.append(child)
            seen.add(cid)
    return population


def save_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
