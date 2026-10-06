#!/usr/bin/env python3
"""Score an eval arm against rubric.md, or measure a control area.

    ./score.py <dir> --profile library|product [--label "..."] [--json out.json]
    ./score.py <dir> --control --label "CONTROL: <product> <area>"

Emits a verdict for all 28 rubric checks plus D1-D5.

  PASS / FAIL  decided mechanically
  REVIEW       needs a human or model to read the diff and decide
  NA           not applicable to this profile, drops out of the denominator

Roughly half the rubric cannot be grepped. Those come back REVIEW with the
evidence gathered, so a scorer records a deliberate verdict instead of guessing.
A run is not scored until every REVIEW has been resolved.

--control prints raw counts with no verdicts: what an agent imitating the
existing code would produce. Measure this per product before running task 02.
"""
import argparse, json, os, re, sys

LIBRARY_NA = {18, 19, 20}
PRODUCT_NA = {14, 15, 16, 17}

def collect(root):
    src, patches = [], []
    for base, _, files in os.walk(root):
        for f in files:
            p = os.path.join(base, f)
            if f.endswith(".cs"):
                src.append(p)
            elif f.endswith(".patch.md"):
                patches.append(p)
    return src, patches

def read(paths):
    out = {}
    for p in paths:
        try:
            out[p] = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            pass
    return out

def n(texts, pattern):
    rx = re.compile(pattern)
    return sum(len(rx.findall(t)) for t in texts.values())

def files_matching(texts, pattern):
    rx = re.compile(pattern)
    return [p for p, t in texts.items() if rx.search(t)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--profile", choices=["library", "product"])
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--label", default="")
    ap.add_argument("--json")
    a = ap.parse_args()

    if not a.control and not a.profile:
        ap.error("--profile is required unless --control")

    src_paths, patch_paths = collect(a.directory)
    if not src_paths and not patch_paths:
        print(f"no .cs or .patch.md files under {a.directory}")
        return 1
    src = read(src_paths)
    patches = read(patch_paths)
    # Authored code only. A .patch.md shows surrounding EXISTING lines for context,
    # so counting it would both inflate the endpoint count and attribute sibling
    # code's violations to this arm. Patches are used only for check 13.
    allt = src

    handlers = {p: t for p, t in src.items()
                if "Handlers.cs" in p or re.search(r"Endpoints\.cs$", p)}
    if not handlers:
        handlers = src

    endpoints = n(allt, r"\.Map(Get|Post|Put|Delete|Patch)\(")
    label = a.label or a.directory

    if a.control:
        print(f"=== {label} ===")
        print(f"  files: {len(src_paths)}   endpoints: {endpoints}")
        for name, pat in [
            ("untyped Results.*",            r"[^d]Results\.(Ok|NotFound|BadRequest|NoContent)"),
            ("IResult / IActionResult",      r"Task<IResult>|IActionResult|ActionResult<"),
            ("Results<..> unions",           r"Results<"),
            ("ResultSet<T>",                 r"ResultSet<"),
            ("bare Ok<List<..>>",            r"Ok<(List|IEnumerable|IReadOnlyCollection)<"),
            ("[AsParameters]",               r"\[AsParameters\]"),
            ("WithName(nameof(..))",         r"WithName\(nameof"),
            ('WithName("literal")',          r'WithName\("'),
            ("WithSummary",                  r"WithSummary"),
            ("inline lambda in Map*",        r"Map(Get|Post|Put|Delete|Patch)\([^,]*,\s*(async )?\("),
            ("raw AddEndpointFilter",        r"AddEndpointFilter"),
            ("DbContext in endpoint files",  r"DbContext"),
            ("AbstractValidator",            r"AbstractValidator<"),
            ("DataAnnotations",              r"\[(Required|MaxLength|StringLength|Range|EmailAddress)"),
        ]:
            print(f"  {name:<34} {n(allt, pat)}")
        print("\n  Read these as raw counts. An existing area 'fails' exactly where it has")
        print("  drifted, and that is the measurement. Record beside your results; controls")
        print("  do not transfer between products.")
        return 0

    na = LIBRARY_NA if a.profile == "library" else PRODUCT_NA
    R = {}

    def put(num, status, detail=""):
        R[num] = (status, detail)

    def auto(num, ok, detail=""):
        put(num, "PASS" if ok else "FAIL", detail)

    # --- Return types
    c = n(allt, r"[^d]Results\.(Ok|NotFound|BadRequest|NoContent)")
    auto(1, c == 0, f"{c} untyped Results.*")
    c = n(allt, r"Task<IResult>|IActionResult|ActionResult<")
    auto(2, c == 0, f"{c} occurrences")
    put(3, "REVIEW", f"{n(allt, r'Results<')} Results<..> unions found; confirm every "
                     f"multi-exit handler is annotated")
    created = n(allt, r"TypedResults\.Created\(")
    car = n(allt, r"CreatedAtRoute")
    if created == 0 and car == 0:
        put(4, "NA", "no create endpoint")
    else:
        auto(4, car > 0 and n(allt, r"TypedResults\.Created\(\s*[\$\"]") == 0,
             f"CreatedAtRoute={car}, hand-built={n(allt, r'TypedResults.Created\(\s*[\$\"]')}")
    lo, rs = n(allt, r"ListOptions"), n(allt, r"Ok<ResultSet<")
    put(5, "REVIEW", f"ListOptions={lo}, Ok<ResultSet<..>>={rs}; confirm the list endpoint "
                     f"binding ListOptions returns ResultSet<T>")
    bare = n(allt, r"Ok<(List|IEnumerable|IReadOnlyCollection)<")
    put(6, "REVIEW", f"{bare} bare collection returns; NA if the task has no bounded "
                     f"sub-collection, otherwise confirm it is not wrapped")
    if lo == 0:
        put(7, "NA", "no paging/filter parameters")
    else:
        auto(7, n(allt, r"\[AsParameters\]") > 0, f"{n(allt, r'\[AsParameters\]')} bindings")

    # --- Structure
    c = n(allt, r"Map(Get|Post|Put|Delete|Patch)\([^,]*,\s*(async )?\(")
    auto(8, c == 0, f"{c} inline lambdas")
    dbc = n(handlers, r"DbContext")
    linq = n(handlers, r"\.Where\(|\.FirstOrDefaultAsync\(|\.Select\(x =>")
    if dbc:
        put(9, "FAIL", f"DbContext appears {dbc}x in handler files")
    else:
        put(9, "REVIEW", f"no DbContext; {linq} LINQ-ish calls. Read the handlers for "
                         f"business logic")
    put(10, "REVIEW", "confirm logic sits in a service the handler calls")
    ints = n(src, r"internal static class")
    pubs = n(src, r"public static class [A-Za-z]*(Api|Handlers|Endpoints)")
    auto(11, pubs == 0 and ints > 0, f"internal={ints}, public={pubs}")
    api = [p for p in src_paths if p.endswith("Api.cs")]
    hnd = [p for p in src_paths if p.endswith("Handlers.cs")]
    single = [p for p in src_paths if p.endswith("Endpoints.cs")]
    shape = ("split" if api and hnd else "single-file" if single else "other")
    put(12, "REVIEW", f"detected {shape}. New file must split; one endpoint added to an "
                      f"existing single-file group matches that file. See D1")
    agg = [p for p, t in patches.items()
           if re.search(r"Map[A-Za-z]*\(\)|Map[A-Za-z]+\(this\b|\.Map[A-Za-z]+\(\);", t)]
    put(13, "REVIEW", f"{len(patch_paths)} patch file(s), {len(agg)} showing a Map* "
                      f"registration: {', '.join(os.path.basename(p) for p in agg) or 'none'}")

    # --- Feature library only
    iop = n(allt, r"GetRequiredService<IOptions<")
    lit = n(allt, r'MapGroup\("[/a-zA-Z]')
    auto(14, iop > 0 and lit == 0, f"IOptions={iop}, literal MapGroup={lit}")
    auto(15, n(src, r"namespace Microsoft\.AspNetCore\.Routing") > 0, "")
    auto(16, bool(api and hnd), f"Api.cs={len(api)}, Handlers.cs={len(hnd)}")
    c = n(allt, r"AddEndpointFilter")
    auto(17, c == 0, f"{c} raw AddEndpointFilter")

    # --- Product API only
    auto(18, iop == 0, f"{iop} invented IOptions lookups")
    put(19, "REVIEW", "confirm the product's permission helper is applied as sibling routes apply it")
    be = n(allt, r"throw new BusinessException")
    whe = n(allt, r"WithHandledException")
    if be == 0:
        put(20, "PASS", "no BusinessException thrown")
    else:
        put(20, "REVIEW", f"{be} throws, {whe} WithHandledException in output. Check the "
                          f"TARGET GROUP in the repo, not just this diff")

    # --- Metadata and validation
    c = n(allt, r'WithName\("')
    auto(21, c == 0 and n(allt, r"WithName\(nameof") > 0, f"{c} string literals")
    ws = n(allt, r"WithSummary")
    auto(22, endpoints > 0 and ws >= endpoints, f"{ws} summaries / {endpoints} endpoints")
    if n(allt, r"MapGroup\(") == 0:
        put(23, "NA", "joins an existing group; group metadata is inherited, not in this diff")
    else:
        grp = all(n(allt, p) > 0 for p in [r"WithGroupName", r"WithTags", r"ProducesProblem"])
        auto(23, grp, f"GroupName={n(allt, r'WithGroupName')}, Tags={n(allt, r'WithTags')}, "
                      f"ProducesProblem={n(allt, r'ProducesProblem')}")
    wpv = n(allt, r"WithParameterValidation")
    prt = n(allt, r"ProducesResponseType\(\s*StatusCodes\.Status400")
    if wpv == 0:
        put(24, "NA", "no WithParameterValidation")
    else:
        auto(24, prt == 0, f"{prt} redundant ProducesResponseType(400)")
    av = n(allt, r"AbstractValidator<")
    da = n(allt, r"\[(Required|MaxLength|StringLength|Range|EmailAddress)")
    if av and da:
        put(25, "REVIEW", f"BOTH present: AbstractValidator={av}, DataAnnotations={da}. "
                          f"Confirm they are not stacked on the same request")
    else:
        put(25, "PASS", f"single mechanism (AbstractValidator={av}, DataAnnotations={da})")
    c = n(allt, r"ConfigureHttpJsonOptions|AddCors\(|AddProblemDetails\(")
    auto(26, c == 0, f"{c} host-default reconfigurations")

    # --- Routing
    routes = re.findall(r'Map(?:Get|Post|Put|Delete|Patch|Group)\("([^"]*)"', "".join(allt.values()))
    # Route parameters are {camelCaseId} by C# convention and are exempt; only the
    # literal segments between them are subject to the kebab-case rule.
    literal_segs = [seg for r in routes for seg in r.split("/")
                    if seg and not seg.startswith("{")]
    bad = sorted({s for s in literal_segs if re.search(r"[a-z][A-Z]", s) or "_" in s})
    auto(27, not bad, f"non-kebab segments: {bad}" if bad
         else f"{len(literal_segs)} literal segments, all kebab-case")
    put(28, "REVIEW", f"route literals: {routes[:6]}{'...' if len(routes) > 6 else ''}")

    for k in na:
        R[k] = ("NA", "not applicable to this profile")

    drift = {
        "D1": f"file shape detected: {shape}",
        "D2": f"result-object unpacking: {n(allt, r'ServiceResult|\.Success')} signals, "
              f"problem factory: {n(allt, r'ProblemHttpResultFactory')}",
        "D3": f"raw AddEndpointFilter: {n(allt, r'AddEndpointFilter')}",
        "D4": f"bare collection returns: {bare}",
        "D5": f"AbstractValidator={av}, DataAnnotations={da}",
    }

    print(f"=== {label} ===")
    print(f"profile: {a.profile}   files: {len(src_paths)} src + {len(patch_paths)} patch"
          f"   endpoints: {endpoints}\n")
    for i in range(1, 29):
        st, det = R[i]
        print(f"  {i:>2}  {st:<7} {det}")
    print("\n  drift (score followed-Platform / copied-drift / n/a by hand):")
    for k, v in drift.items():
        print(f"  {k}  REVIEW  {v}")

    applicable = [i for i in range(1, 29) if R[i][0] != "NA"]
    decided = [i for i in applicable if R[i][0] in ("PASS", "FAIL")]
    passed = [i for i in applicable if R[i][0] == "PASS"]
    pending = [i for i in applicable if R[i][0] == "REVIEW"]
    print(f"\n  applicable: {len(applicable)}   auto-decided: {len(decided)} "
          f"({len(passed)} pass)   pending review: {len(pending)} -> {pending}")
    print(f"  NOT A FINAL SCORE until the {len(pending)} REVIEW checks are resolved.")
    print(f"  Report as: <passed>/{len(applicable)} (rubric.md, profile={a.profile})")

    if a.json:
        json.dump({"label": label, "profile": a.profile, "directory": a.directory,
                   "endpoints": endpoints,
                   "checks": {str(k): {"status": v[0], "detail": v[1]} for k, v in sorted(R.items())},
                   "drift": drift,
                   "applicable": len(applicable), "auto_passed": len(passed),
                   "pending_review": pending},
                  open(a.json, "w"), indent=2)
        print(f"  wrote {a.json}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
