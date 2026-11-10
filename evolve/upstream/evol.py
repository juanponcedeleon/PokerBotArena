import argparse
import ast
import copy
import hashlib
import json
import random
import shutil
import statistics
import subprocess
from pathlib import Path


# name: (default, minimum, maximum)
PARAMETERS = {
    "selection_temperature": (0.18, 0.10, 0.40),
    "selection_randomness": (0.25, 0.10, 0.65),
    "preflop_floor": (0.47, 0.38, 0.62),
    "preflop_price_weight": (0.50, 0.20, 0.90),
    "preflop_raise_threshold": (0.86, 0.75, 0.98),
    "call_margin_scale": (1.00, 0.40, 2.50),
    "value_raise_threshold": (0.72, 0.62, 0.90),
    "value_bet_threshold": (0.62, 0.50, 0.82),
    "bet_size_scale": (1.00, 0.50, 1.80),
    "disclosure_scale": (1.00, 0.00, 2.50),
}

BAD_FITNESS = -1_000_000.0


def save_json(path, value):
    Path(path).write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def expression(text):
    return ast.parse(text, mode="eval").body


def parameter(name):
    return expression(f"_EVOLUTION_PARAMS[{name!r}]")


def require_count(label, actual, expected=1):
    if actual != expected:
        raise ValueError(
            f"Unsupported agent structure for {label}: "
            f"expected {expected} match(es), found {actual}. "
            "This tuner targets the version-2 agent from the conversation."
        )


def replace_assignment(function, target_name, replacement):
    """
    Replace the RHS of a simple assignment inside a specific function.

    replacement receives the original RHS AST.
    """
    count = 0

    class Transformer(ast.NodeTransformer):
        def visit_Assign(self, node):
            nonlocal count

            node = self.generic_visit(node)

            if (
                len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == target_name
            ):
                count += 1
                node.value = replacement(node.value)

            return node

    Transformer().visit(function)
    require_count(
        f"{function.name}.{target_name}",
        count,
    )


def replace_float(function, old_value, replacement):
    count = 0

    class Transformer(ast.NodeTransformer):
        def visit_Constant(self, node):
            nonlocal count

            if (
                isinstance(node.value, float)
                and node.value == old_value
            ):
                count += 1
                return ast.copy_location(
                    copy.deepcopy(replacement),
                    node,
                )

            return node

    Transformer().visit(function)
    require_count(
        f"{function.name}: literal {old_value}",
        count,
    )


def multiplied(original, name):
    return ast.BinOp(
        left=original,
        op=ast.Mult(),
        right=parameter(name),
    )


def build_template(source):
    """
    Convert selected hard-coded strategy constants into references to a
    fixed parameter dictionary.

    The dictionary is configuration, not persistent gameplay state.
    """
    tree = ast.parse(source)

    if any(
        isinstance(node, ast.Name)
        and node.id == "_EVOLUTION_PARAMS"
        for node in ast.walk(tree)
    ):
        raise ValueError(
            "Use the original version-2 agent as --base, "
            "not an already generated evolutionary candidate."
        )

    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    required = {
        "_retention_weights",
        "preflop_action",
        "postflop_action",
        "disclosure_cost",
    }

    missing = required - functions.keys()
    if missing:
        raise ValueError(
            "Missing required version-2 functions: "
            + ", ".join(sorted(missing))
        )

    # Opponent selection model.
    retention = functions["_retention_weights"]

    replace_assignment(
        retention,
        "temperature",
        lambda old: parameter("selection_temperature"),
    )

    replace_float(
        retention,
        0.25,
        parameter("selection_randomness"),
    )

    replace_float(
        retention,
        0.75,
        expression(
            "1.0 - _EVOLUTION_PARAMS['selection_randomness']"
        ),
    )

    # Preflop calling threshold.
    preflop = functions["preflop_action"]

    replace_assignment(
        preflop,
        "threshold",
        lambda old: expression(
            "_EVOLUTION_PARAMS['preflop_floor']"
            " + _EVOLUTION_PARAMS['preflop_price_weight'] * price"
        ),
    )

    replace_float(
        preflop,
        0.86,
        parameter("preflop_raise_threshold"),
    )

    # Postflop calling caution.
    postflop = functions["postflop_action"]

    replace_assignment(
        postflop,
        "margin",
        lambda old: multiplied(old, "call_margin_scale"),
    )

    # Value-bet / value-raise thresholds.
    replace_assignment(
        postflop,
        "value_threshold",
        lambda old: expression(
            "_EVOLUTION_PARAMS['value_raise_threshold']"
            " if call > 0 else "
            "_EVOLUTION_PARAMS['value_bet_threshold']"
        ),
    )

    # Scale the increment above the minimum legal raise.
    replace_assignment(
        postflop,
        "extra",
        lambda old: multiplied(old, "bet_size_scale"),
    )

    # Exposure/disclosure penalty.
    disclosure = functions["disclosure_cost"]
    return_count = 0

    for node in ast.walk(disclosure):
        if (
            isinstance(node, ast.Return)
            and isinstance(node.value, ast.Name)
            and node.value.id == "cost"
        ):
            node.value = multiplied(
                node.value,
                "disclosure_scale",
            )
            return_count += 1

    require_count("disclosure_cost return", return_count)

    # During optimization, expose internal exceptions rather than allowing
    # the agent's broad exception handler to hide them as legal fallbacks.
    debug_count = 0

    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "STRICT_DEBUG"
        ):
            node.value = ast.Constant(value=True)
            debug_count += 1

    require_count("STRICT_DEBUG", debug_count)

    return ast.fix_missing_locations(tree)


def render_agent(template, genome):
    tree = copy.deepcopy(template)

    config = ast.parse(
        "_EVOLUTION_PARAMS = " + repr(dict(genome))
    ).body[0]

    # Preserve module docstring and any future imports.
    insertion = 0

    if (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        insertion = 1

    while (
        insertion < len(tree.body)
        and isinstance(tree.body[insertion], ast.ImportFrom)
        and tree.body[insertion].module == "__future__"
    ):
        insertion += 1

    tree.body.insert(insertion, config)
    ast.fix_missing_locations(tree)

    text = ast.unparse(tree) + "\n"
    compile(text, "<evolved-agent>", "exec")
    return text


def defaults():
    return {
        name: spec[0]
        for name, spec in PARAMETERS.items()
    }


def repair(genome):
    result = {}

    for name, (_, low, high) in PARAMETERS.items():
        value = max(low, min(high, float(genome[name])))
        result[name] = round(value, 6)

    # Facing a bet should not use a lower base raising threshold than
    # betting into an unchecked pot.
    result["value_raise_threshold"] = max(
        result["value_raise_threshold"],
        result["value_bet_threshold"],
    )

    return result


def genome_id(genome):
    encoded = json.dumps(
        genome, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()[:12]


def mutate(parent, rng, scale):
    child = dict(parent)
    changed = False

    for name, (_, low, high) in PARAMETERS.items():
        if rng.random() < 0.40:
            child[name] += rng.gauss(0.0, scale * (high - low))
            changed = True

    if not changed:
        name = rng.choice(list(PARAMETERS))
        _, low, high = PARAMETERS[name]
        child[name] += rng.gauss(0.0, scale * (high - low))

    return repair(child)


def crossover(left, right, rng):
    return repair({
        name: left[name] if rng.random() < 0.5 else right[name]
        for name in PARAMETERS
    })


def extract_match_json(stdout):
    """
    Find the CLI match-result object even if stdout also contains
    other JSON objects or status text.
    """
    decoder = json.JSONDecoder()
    found = None

    for index, character in enumerate(stdout):
        if character != "{":
            continue

        try:
            value, _ = decoder.raw_decode(stdout, index)
        except json.JSONDecodeError:
            continue

        if (
            isinstance(value, dict)
            and isinstance(value.get("bots"), dict)
            and "tables" in value
        ):
            found = value

    if found is None:
        raise ValueError("No match-results JSON found in CLI output")

    return found


class Evaluator:
    def __init__(self, args, template, opponents):
        self.args = args
        self.template = template
        self.opponents = opponents
        self.cache = {}
        self.candidates = {}
        self.match_number = 0

    def candidate_folder(self, genome):
        identifier = genome_id(genome)

        if identifier not in self.candidates:
            folder = self.args.work / "candidates" / identifier
            folder.mkdir(parents=True)

            (folder / "agent.py").write_text(
                render_agent(self.template, genome),
                encoding="utf-8",
            )
            save_json(folder / "parameters.json", genome)
            self.candidates[identifier] = folder

        return self.candidates[identifier]

    def match(self, genome, seed, tables):
        identifier = genome_id(genome)
        key = (identifier, str(seed), tables)

        if key in self.cache:
            return self.cache[key]

        folder = self.candidate_folder(genome)
        self.match_number += 1

        prefix = self.args.work / "matches" / (
            f"{self.match_number:05d}_{identifier}"
        )

        command = [
            self.args.cli,
            "play",
            str(folder),
            *[str(path) for path in self.opponents],
            "--tables",
            str(tables),
            "--seed",
            str(seed),
            "--no-history",
        ]

        stdout = ""
        stderr = ""

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.args.timeout,
            )
            stdout = completed.stdout
            stderr = completed.stderr

            if completed.returncode != 0:
                raise RuntimeError(
                    f"CLI exited with code {completed.returncode}"
                )

            result = extract_match_json(stdout)

            # Candidate is always the first entry.
            entries = [
                value
                for name, value in result["bots"].items()
                if name.endswith("#0")
            ]

            if len(entries) != 1:
                raise ValueError(
                    "Cannot identify first bot in match results"
                )

            candidate = entries[0]

            record = {
                "candidate": identifier,
                "seed": str(seed),
                "tables": tables,
                "average_points": float(candidate["average_points"]),
                "failed_decisions": int(
                    candidate["failed_decisions"]
                ),
                "places": candidate.get("places", {}),
                "error": None,
            }

        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""

            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")

            record = {
                "candidate": identifier,
                "seed": str(seed),
                "tables": tables,
                "average_points": None,
                "failed_decisions": None,
                "places": {},
                "error": f"Match exceeded {self.args.timeout} seconds",
            }

        except Exception as exc:
            record = {
                "candidate": identifier,
                "seed": str(seed),
                "tables": tables,
                "average_points": None,
                "failed_decisions": None,
                "places": {},
                "error": str(exc),
            }

        prefix.with_suffix(".stdout.txt").write_text(
            stdout, encoding="utf-8"
        )
        prefix.with_suffix(".stderr.txt").write_text(
            stderr, encoding="utf-8"
        )
        save_json(prefix.with_suffix(".json"), record)

        self.cache[key] = record
        return record

    def evaluate(self, genome, seeds, tables):
        records = [
            self.match(genome, seed, tables)
            for seed in seeds
        ]

        healthy = all(
            record["error"] is None
            and record["failed_decisions"] == 0
            for record in records
        )

        if healthy:
            values = [
                record["average_points"]
                for record in records
            ]
            fitness = statistics.mean(values)
            seed_sd = (
                statistics.stdev(values)
                if len(values) > 1 else None
            )
        else:
            fitness = BAD_FITNESS
            seed_sd = None

        return {
            "candidate": genome_id(genome),
            "parameters": genome,
            "healthy": healthy,
            "fitness": fitness,
            "seed_mean_sd": seed_sd,
            "matches": records,
        }


def make_population(elites, size, rng, generation):
    population = [dict(genome) for genome in elites]
    seen = {genome_id(genome) for genome in population}

    scale = max(0.05, 0.16 * (0.88 ** generation))

    while len(population) < size:
        left = rng.choice(elites)
        right = rng.choice(elites)

        child = crossover(left, right, rng)
        child = mutate(child, rng, scale)
        identifier = genome_id(child)

        if identifier not in seen:
            population.append(child)
            seen.add(identifier)

    return population


def parse_args():
    parser = argparse.ArgumentParser(
        description="Offline evolutionary tuning for Bay Area agent v2"
    )

    parser.add_argument("--base", type=Path, default=Path("agent.py"))
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("base_agent.py"),
    )
    parser.add_argument(
        "--work",
        type=Path,
        default=Path("evolution_run"),
    )
    parser.add_argument("--cli", default="poker-agent")

    parser.add_argument("--population", type=int, default=6)
    parser.add_argument("--generations", type=int, default=4)

    parser.add_argument("--tables", type=int, default=25)
    parser.add_argument("--train-seeds", type=int, default=2)

    parser.add_argument("--validation-tables", type=int, default=100)
    parser.add_argument("--validation-seeds", type=int, default=2)

    parser.add_argument("--test-tables", type=int, default=200)
    parser.add_argument("--test-seeds", type=int, default=2)

    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--timeout", type=float, default=900.0)

    parser.add_argument(
        "--opponents",
        nargs="+",
        type=Path,
        help=(
            "Explicit opponent folders, one per seat. "
            "Repeat folders for repeated seats. "
            "Default: three frozen baselines, three min_raisers, "
            "and one check_or_fold."
        ),
    )

    args = parser.parse_args()

    if args.population < 3:
        parser.error("--population must be at least 3")

    for name in (
        "generations",
        "tables",
        "train_seeds",
        "validation_tables",
        "validation_seeds",
        "test_tables",
        "test_seeds",
    ):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be positive")

    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    return args


def main():
    args = parse_args()

    args.base = args.base.resolve()
    args.baseline = args.baseline.resolve()
    args.work = args.work.resolve()

    if shutil.which(args.cli) is None:
        raise SystemExit(
            f"Cannot find {args.cli!r}. Activate the starter-kit environment."
        )

    if not args.base.is_file():
        raise SystemExit(f"Missing starting agent: {args.base}")

    if not args.baseline.is_file():
        raise SystemExit(f"Missing baseline agent: {args.baseline}")

    if args.work.exists():
        raise SystemExit(
            f"Output folder already exists: {args.work}\n"
            "Choose a new --work folder so previous results are preserved."
        )

    source = args.base.read_text(encoding="utf-8")
    template = build_template(source)

    # Validate opponent locations before creating the experiment.
    if args.opponents:
        opponents = [path.resolve() for path in args.opponents]

        if not 1 <= len(opponents) <= 9:
            raise SystemExit("Supply between 1 and 9 opponent seats")

        for path in opponents:
            if not (path / "agent.py").is_file():
                raise SystemExit(
                    f"Opponent folder has no agent.py: {path}"
                )
    else:
        min_raiser = Path("examples/min_raiser").resolve()
        check_fold = Path("examples/check_or_fold").resolve()

        for path in (min_raiser, check_fold):
            if not (path / "agent.py").is_file():
                raise SystemExit(
                    f"Missing opponent folder: {path}\n"
                    "Run from the starter-kit root or supply --opponents."
                )

    args.work.mkdir(parents=True)
    (args.work / "matches").mkdir()
    (args.work / "candidates").mkdir()

    frozen_baseline = args.work / "frozen_baseline"
    frozen_baseline.mkdir()
    shutil.copy2(
        args.baseline,
        frozen_baseline / "agent.py",
    )

    (args.work / "starting_agent.py").write_text(
        source,
        encoding="utf-8",
    )

    if not args.opponents:
        opponents = [
            frozen_baseline,
            frozen_baseline,
            frozen_baseline,
            min_raiser,
            min_raiser,
            min_raiser,
            check_fold,
        ]

    save_json(args.work / "experiment.json", {
        "base": str(args.base),
        "baseline": str(args.baseline),
        "seed": args.seed,
        "population": args.population,
        "generations": args.generations,
        "training_tables_per_seed": args.tables,
        "training_seeds_per_generation": args.train_seeds,
        "validation_tables_per_seed": args.validation_tables,
        "validation_seed_count": args.validation_seeds,
        "test_tables_per_seed": args.test_tables,
        "test_seed_count": args.test_seeds,
        "opponents": [
            {
                "folder": str(path),
                "agent_sha256": hashlib.sha256(
                    (path / "agent.py").read_bytes()
                ).hexdigest(),
            }
            for path in opponents
        ],
        "parameter_bounds": PARAMETERS,
    })

    rng = random.Random(args.seed)
    evaluator = Evaluator(args, template, opponents)
    original = defaults()

    # Check the generated interface before expensive evaluations.
    original_folder = evaluator.candidate_folder(original)

    check = subprocess.run(
        [args.cli, "check", str(original_folder / "agent.py")],
        capture_output=True,
        text=True,
        timeout=args.timeout,
    )

    (args.work / "check.stdout.txt").write_text(
        check.stdout, encoding="utf-8"
    )
    (args.work / "check.stderr.txt").write_text(
        check.stderr, encoding="utf-8"
    )

    if check.returncode != 0:
        raise SystemExit(
            "Generated agent failed poker-agent check. "
            f"See {args.work}/check.*.txt"
        )

    # A diagnostic match catches swallowed strategy errors because
    # generated agents have STRICT_DEBUG=True.
    smoke = evaluator.evaluate(
        original,
        [f"{args.seed}:smoke"],
        min(5, args.tables),
    )

    if not smoke["healthy"]:
        save_json(args.work / "smoke_failure.json", smoke)
        raise SystemExit(
            "Starting agent failed the strict diagnostic match. "
            "Inspect matches/*.stderr.txt before tuning."
        )

    population = make_population(
        [original],
        args.population,
        rng,
        generation=0,
    )

    # Each generation's winner becomes a validation finalist.
    # Always include the unchanged starting parameters.
    finalists = {genome_id(original): original}
    training_history = []

    for generation in range(args.generations):
        seeds = [
            f"{args.seed}:train:{generation}:{index}"
            for index in range(args.train_seeds)
        ]

        print(
            f"\nGeneration {generation + 1}/{args.generations}",
            flush=True,
        )

        ranked = []

        for index, genome in enumerate(population):
            result = evaluator.evaluate(
                genome,
                seeds,
                args.tables,
            )
            ranked.append(result)

            status = (
                f"{result['fitness']:.3f} points"
                if result["healthy"] else "REJECTED: failure"
            )

            print(
                f"  {index + 1}/{len(population)} "
                f"{result['candidate']}  {status}",
                flush=True,
            )

        ranked.sort(
            key=lambda result: result["fitness"],
            reverse=True,
        )

        healthy = [
            result for result in ranked
            if result["healthy"]
        ]

        if not healthy:
            save_json(
                args.work / f"generation_{generation + 1}.json",
                ranked,
            )
            raise SystemExit(
                "All candidates failed. Inspect the match logs."
            )

        winner = healthy[0]
        finalists[winner["candidate"]] = winner["parameters"]

        training_history.append({
            "generation": generation + 1,
            "seeds": seeds,
            "results": ranked,
        })

        save_json(
            args.work / f"generation_{generation + 1}.json",
            training_history[-1],
        )

        print(
            f"  Winner: {winner['candidate']} "
            f"({winner['fitness']:.3f})",
            flush=True,
        )

        elite_count = min(2, len(healthy))
        elites = [
            result["parameters"]
            for result in healthy[:elite_count]
        ]

        population = make_population(
            elites,
            args.population,
            rng,
            generation + 1,
        )

    # Validation seeds are never used during mutation/selection.
    validation_seeds = [
        f"{args.seed}:validation:{index}"
        for index in range(args.validation_seeds)
    ]

    print("\nValidating finalists...", flush=True)
    validation = []

    for genome in finalists.values():
        result = evaluator.evaluate(
            genome,
            validation_seeds,
            args.validation_tables,
        )
        validation.append(result)

        print(
            f"  {result['candidate']} "
            f"{result['fitness']:.3f}"
            f"{'' if result['healthy'] else ' REJECTED'}",
            flush=True,
        )

    validation.sort(
        key=lambda result: result["fitness"],
        reverse=True,
    )

    viable = [
        result for result in validation
        if result["healthy"]
    ]

    if not viable:
        save_json(args.work / "validation_failure.json", validation)
        raise SystemExit("No finalist passed validation reliably.")

    selected = viable[0]
    best_genome = selected["parameters"]

    # Test seeds are used only after the candidate has been selected.
    # Do not select a different candidate based on these results.
    test_seeds = [
        f"{args.seed}:test:{index}"
        for index in range(args.test_seeds)
    ]

    print("\nFinal held-out test...", flush=True)

    original_test = evaluator.evaluate(
        original,
        test_seeds,
        args.test_tables,
    )
    selected_test = evaluator.evaluate(
        best_genome,
        test_seeds,
        args.test_tables,
    )

    delta = None

    if original_test["healthy"] and selected_test["healthy"]:
        delta = (
            selected_test["fitness"]
            - original_test["fitness"]
        )

    best_folder = args.work / "best"
    best_folder.mkdir()

    shutil.copy2(
        evaluator.candidate_folder(best_genome) / "agent.py",
        best_folder / "agent.py",
    )
    save_json(
        best_folder / "parameters.json",
        best_genome,
    )

    report = {
        "selected_candidate": selected["candidate"],
        "selected_parameters": best_genome,
        "validation": validation,
        "original_test": original_test,
        "selected_test": selected_test,
        "held_out_point_difference": delta,
        "match_processes_run": evaluator.match_number,
        "notes": [
            "Selection used validation results, not final test results.",
            "Any reported failed decision rejects a candidate.",
            "Generated agents use STRICT_DEBUG=True.",
            "seed_mean_sd is descriptive variation across seed batches, "
            "not a table-level confidence interval.",
            "Improvement against this lineup does not establish strength "
            "against unseen opponents.",
        ],
    }

    save_json(args.work / "report.json", report)

    print(f"\nCandidate saved: {best_folder / 'agent.py'}")
    print(f"Report saved:    {args.work / 'report.json'}")

    if delta is None:
        print(
            "Final test encountered failures. "
            "Do not promote this candidate without investigation."
        )
    else:
        print(
            f"Starting bot: {original_test['fitness']:.3f} points"
        )
        print(
            f"Selected bot: {selected_test['fitness']:.3f} points"
        )
        print(
            f"Held-out difference: {delta:+.3f} points per table"
        )

        if delta <= 0:
            print(
                "No positive held-out improvement in this run. "
                "Keep your current bot unless broader testing supports "
                "the candidate."
            )
        else:
            print(
                "Positive held-out result. Test against additional "
                "opponent lineups before replacing your current bot."
            )


if __name__ == "__main__":
    main()