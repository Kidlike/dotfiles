#!/usr/bin/env python3
"""Generate an interactive HTML report of git contribution statistics.

A more advanced sibling of ``git-stats.py``. Instead of a terminal table it
writes a single self-contained ``git-stats-YYYY-MM-DD.html`` file that pairs the
per-author metrics table with an interactive multi-level pie (sunburst) chart of
the top three directory levels, sized by lines added. Clicking a slice rescopes
the table to that directory, exactly as ``git-stats.py --dir <slice>`` would.

Accepts the same CLI arguments as ``git-stats.py``. The ``--color`` flag is
accepted for compatibility but ignored (coloring lives in the HTML/CSS).

    python git-stats.py --help
"""

import argparse
import calendar
import json
import subprocess
import sys
from datetime import datetime, timezone

# Selectable metric columns, in their default display order. The "Author"
# column is always present as the row label and is not listed here.
ALL_COLUMNS = ("commits", "added", "removed", "churn", "tenancy", "survived")
COLUMN_HEADERS = {
    "commits": "Commits",
    "added": "Lines Added",
    "removed": "Lines Removed",
    "churn": "Churn",
    "tenancy": "Tenancy (months)",
    "survived": "Survived Lines",
}
# Columns whose TOTAL row is a meaningful sum (tenancy is per-author, so it is
# left blank instead).
SUMMABLE_COLUMNS = frozenset({"commits", "added", "removed", "churn", "survived"})

# How many directory levels the sunburst shows below the chart root.
MAX_LEVELS = 3


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="git-stats-html.py",
        description="Generate an interactive HTML git contribution report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Columns:\n"
            "  commits    number of (non-merge) commits\n"
            "  added      lines added\n"
            "  removed    lines removed\n"
            "  churn      lines added minus lines removed\n"
            "  tenancy    whole calendar months from first to last commit (rounded up)\n"
            "  survived   lines still attributed to the author at HEAD (via git blame)\n"
            "\n"
            "Writes git-stats-YYYY-MM-DD.html to the current directory and prints\n"
            "its path. The report shows the top 3 directory levels as an interactive\n"
            "sunburst (sized by lines added); click a slice to rescope the table.\n"
            "Click a table header to sort by that column (click again to reverse);\n"
            "the chosen sort is kept as you move between slices. Hover a row's\n"
            "Lines Added value to see the top 3 files/folders behind it.\n"
            "\n"
            "Examples:\n"
            "  %(prog)s                              # all columns, current repo\n"
            "  %(prog)s -c added,removed .\n"
            "  %(prog)s -d services/spring/content -c commits,added\n"
        ),
    )
    parser.add_argument(
        "-c",
        "--columns",
        metavar="COL[,COL...]",
        default=None,
        help="Comma-separated list of columns to compute and display "
        f"(default: all). Choose from: {', '.join(ALL_COLUMNS)}.",
    )
    parser.add_argument(
        "-m",
        "--merge",
        action="append",
        default=[],
        metavar="CANONICAL,ALIAS[,ALIAS...]",
        help="Merge a comma-separated list of authors into the first name. "
        "May be passed multiple times.",
    )
    parser.add_argument(
        "-r",
        "--repo",
        default=".",
        help="Path to the git repository (default: current directory).",
    )
    parser.add_argument(
        "-d",
        "--dir",
        default=None,
        metavar="PATH",
        help="Restrict all metrics to files under this path (relative to the "
        "repo root). The sunburst's 3 levels are then relative to this subtree.",
    )
    parser.add_argument(
        "--since",
        default=None,
        metavar="YYYY-MM-DD",
        help="Only count contributions on or after this date. Applies to every "
        "metric (including survived lines).",
    )
    parser.add_argument(
        "--filter",
        default=None,
        metavar=".EXT[,.EXT...]",
        help="Only include files with these extensions, e.g. '.java,.js,.ts'. "
        "The leading dot is optional. By default no files are filtered out.",
    )
    parser.add_argument(
        "-t",
        "--trends",
        action="store_true",
        help="Show a panel above the table with a per-author mini-graph (added "
        "in green, removed in red, monthly over the analysis period) for the top "
        "6 authors by lines added in the selected slice. Off by default.",
    )
    parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help="Accepted for compatibility with git-stats.py; ignored (the HTML "
        "report is always colored via CSS).",
    )
    parser.add_argument(
        "rev_range",
        nargs="?",
        default=None,
        help="Optional git revision range to limit the stats (e.g. main..HEAD).",
    )
    return parser.parse_args(argv)


def parse_columns(spec):
    """Resolve the --columns value into an ordered list of metric column keys."""
    if spec is None:
        return list(ALL_COLUMNS)
    cols = []
    for raw in spec.split(","):
        name = raw.strip().lower()
        if not name or name == "author":
            continue
        if name not in COLUMN_HEADERS:
            sys.exit(
                f"error: unknown column '{name}'. "
                f"Choose from: {', '.join(ALL_COLUMNS)}"
            )
        if name not in cols:
            cols.append(name)
    if not cols:
        sys.exit("error: --columns selected no displayable columns")
    return cols


def build_alias_map(merges):
    """Map every alias (lowercased) to its canonical display name."""
    alias_map = {}
    for spec in merges:
        names = [n.strip() for n in spec.split(",") if n.strip()]
        if not names:
            continue
        canonical = names[0]
        for name in names:
            alias_map[name.lower()] = canonical
    return alias_map


def canonical_for(author, alias_map):
    return alias_map.get(author.lower(), author)


def _add_months(dt, n):
    """Return dt shifted forward by n whole calendar months (clamping day)."""
    month_index = dt.month - 1 + n
    year = dt.year + month_index // 12
    month = month_index % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def tenancy_months(first_ts, last_ts):
    """Whole calendar months between first and last commit, rounded up."""
    first = datetime.fromtimestamp(first_ts, tz=timezone.utc)
    last = datetime.fromtimestamp(last_ts, tz=timezone.utc)

    months = (last.year - first.year) * 12 + (last.month - first.month)
    if _add_months(first, months) > last:
        months -= 1
    if _add_months(first, months) < last:
        months += 1
    return months


def metric_value(key, name, data, survived):
    """Compute a single metric for one author from their raw stats tuple."""
    commits, added, removed, first_ts, last_ts = data
    if key == "commits":
        return commits
    if key == "added":
        return added
    if key == "removed":
        return removed
    if key == "churn":
        return added - removed
    if key == "tenancy":
        return tenancy_months(first_ts, last_ts)
    if key == "survived":
        return survived.get(name, 0)
    raise ValueError(f"unknown metric: {key}")


def sort_key(item, by, survived):
    name, data = item
    if by == "author":
        return (name.lower(),)
    return (-metric_value(by, name, data, survived), name.lower())


def normalize_root(dir_arg):
    """Normalize the --dir value into a repo-relative slice id ('' for root).

    Paths are matched against git output (relative to the repo root, with no
    leading ``./``), so a leading ``./`` is stripped and ``.`` (or ``./``) means
    the repo root -- the same "current dir = repo root" convention git-stats.py
    uses with ``-d .``.
    """
    if not dir_arg:
        return ""
    norm = dir_arg.strip()
    while norm.startswith("./"):
        norm = norm[2:]
    norm = norm.strip("/")
    return "" if norm == "." else norm


def parse_since(value):
    """Validate a --since date, returning (date_str, unix_ts) or (None, None).

    date_str is passed to ``git log --since``; unix_ts (local midnight of that
    day) is used to filter the git-blame pass so survived lines honour --since
    too.
    """
    if value is None:
        return None, None
    text = value.strip()
    try:
        dt = datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        sys.exit(f"error: --since must be a date in YYYY-MM-DD format, got '{value}'")
    return text, dt.timestamp()


def parse_filter(spec):
    """Parse a comma-separated extension list into a normalized set, or None.

    Accepts extensions with or without a leading dot, case-insensitively:
    ``.java,js, .TS`` -> {'.java', '.js', '.ts'}. None means no filtering.
    """
    if not spec:
        return None
    exts = set()
    for raw in spec.split(","):
        ext = raw.strip().lower()
        if not ext:
            continue
        exts.add(ext if ext.startswith(".") else "." + ext)
    return exts or None


def path_matches_filter(path, exts):
    """True if the file's extension is in exts (always True when exts is None)."""
    if exts is None:
        return True
    dot = path.rfind(".")
    if dot <= path.rfind("/"):  # no dot in the basename -> no extension
        return False
    return path[dot:].lower() in exts


def resolve_numstat_path(raw):
    """Return the (new) file path from a --numstat path field.

    numstat renders renames either as ``old => new`` or, when there is a common
    prefix/suffix, as ``src/{old => new}/file.txt``. We only care about the
    destination path (the file as it exists after the commit).
    """
    if "=>" not in raw:
        return raw
    if "{" in raw and "}" in raw:
        pre, rest = raw.split("{", 1)
        mid, post = rest.split("}", 1)
        new = mid.split("=>", 1)[1].strip()
        return (pre + new + post).replace("//", "/")
    return raw.split("=>", 1)[1].strip()


def build_dir_tree(repo, root_id, ext_filter=None):
    """Build the current-tree directory hierarchy (full depth) below root_id.

    Returns {dir: [immediate child dirs, sorted]} keyed by full repo-relative
    paths, with root_id ('' for repo root) as the top. Only directories that
    exist at HEAD (are prefixes of a tracked file) appear. When ``ext_filter``
    is given, only files with those extensions contribute directories.
    """
    ls_cmd = ["git", "-C", repo, "ls-files", "-z"]
    if root_id:
        ls_cmd += ["--", root_id]
    try:
        out = subprocess.run(
            ls_cmd, capture_output=True, text=True, check=True
        ).stdout
    except subprocess.CalledProcessError as exc:
        sys.exit(f"error: git ls-files failed: {exc.stderr.strip() or exc}")

    children = {root_id: set()}
    for path in filter(None, out.split("\x00")):
        if not path_matches_filter(path, ext_filter):
            continue
        if root_id:
            if not path.startswith(root_id + "/"):
                continue
            rel = path[len(root_id) + 1:]
        else:
            rel = path
        parent = root_id
        for comp in rel.split("/")[:-1]:  # dir components (drop the filename)
            d = f"{parent}/{comp}" if parent else comp
            children.setdefault(parent, set()).add(d)
            children.setdefault(d, set())
            parent = d
    return {k: sorted(v) for k, v in children.items()}


def build_display_tree(children_map, root_id):
    """Compress single-child directory chains into one slice each.

    A directory with exactly one subdirectory adds no visual information (its
    child spans the same arc), so we collapse each maximal single-child chain
    into a single node. The node is placed where the chain *starts* (as a child
    of the nearest branching ancestor) but is identified/labelled by the chain's
    *deepest* directory -- e.g. the chain ``uat/src`` -> ``uat/src/test``
    becomes one level-2 slice labelled ``src/test``.

    Returns (display_meta, start_index):
      display_meta[endpoint] = {level, parent, label}   # endpoint = slice id
      start_index[node][seg] = endpoint                 # for fast file lookup
    where ``seg`` is the path component just below ``node`` that enters the
    chain. Only levels 1..MAX_LEVELS are produced.
    """
    display_meta = {}
    start_index = {}

    def spine_endpoint(start):
        cur = start
        while len(children_map.get(cur, [])) == 1:
            cur = children_map[cur][0]
        return cur

    def recurse(node, level):
        idx = {}
        start_index[node] = idx
        if level >= MAX_LEVELS:
            return
        prefix = node + "/" if node else ""
        for child in children_map.get(node, []):
            endpoint = spine_endpoint(child)
            display_meta[endpoint] = {
                "level": level + 1,
                "parent": node,
                "label": endpoint[len(prefix):],
            }
            idx[child[len(prefix):]] = endpoint
            recurse(endpoint, level + 1)

    recurse(root_id, 0)
    return display_meta, start_index


def display_slices_for_path(path, root_id, start_index):
    """(slice_id, child) pairs a file contributes to: root + ancestors (<=3).

    Walks the compressed tree from the root, following at each level the chain
    whose starting component matches the file's path. A file directly inside a
    compressed chain (not within a deeper child chain) stops at that chain's
    slice, exactly like a file directly in a directory.

    ``child`` is the file's immediate path component below that slice's own
    directory (its chain start), with a trailing ``/`` when it is a subfolder
    rather than a file directly in the slice -- used for the hover breakdown.
    """
    def child_of(base):
        rest = path[len(base) + 1:] if base else path
        head, sep, _ = rest.partition("/")
        return head + "/" if sep else head

    result = [(root_id, child_of(root_id))]
    node = root_id
    for _ in range(MAX_LEVELS):
        idx = start_index.get(node)
        if not idx:
            break
        prefix = node + "/" if node else ""
        if node and not path.startswith(prefix):
            break
        seg = path[len(prefix):].split("/", 1)[0]
        endpoint = idx.get(seg)
        if endpoint is None:
            break
        result.append((endpoint, child_of(prefix + seg)))
        node = endpoint
    return result


def collect_slice_stats(repo, rev_range, alias_map, root_id, start_index,
                        since=None, want_trends=False, ext_filter=None):
    """Run git log once and aggregate per-slice, per-author stats.

    Always uses --numstat: we need file paths to attribute work to directory
    slices and line counts to size the sunburst.

    ``since`` (a YYYY-MM-DD string) limits the log to commits on or after that
    date. When ``want_trends`` is set, a monthly added/removed time-series is
    also accumulated per slice/author for the activity mini-graphs.

    Returns (slice_stats, breakdown, trends, month_range):
      slice_stats[slice_id][author] = [commits, added, removed, first, last]
      breakdown[slice_id][author][child] = added lines  (for the hover popup)
      trends[slice_id][author][month_index] = [added, removed]  (or None)
      month_range = (min_month_index, max_month_index)  (or None)
    where month_index = year * 12 + (month - 1), in UTC.
    """
    sep = "\x00"
    fmt = "%x00%at%x00%aN"
    cmd = [
        "git", "-C", repo, "-c", "core.quotepath=false",
        "log", "--no-merges", f"--pretty=format:{fmt}", "--numstat",
    ]
    if since:
        cmd.append(f"--since={since}")
    if rev_range:
        cmd.append(rev_range)
    if root_id:
        cmd += ["--", root_id]

    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        ).stdout
    except FileNotFoundError:
        sys.exit("error: git executable not found on PATH")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"error: git failed: {exc.stderr.strip() or exc}")

    slice_stats = {}
    breakdown = {}
    trends = {} if want_trends else None
    month_bounds = [None, None]  # [min_month_index, max_month_index]

    def entry_for(slice_id, author):
        authors = slice_stats.setdefault(slice_id, {})
        return authors.setdefault(author, [0, 0, 0, current_ts, current_ts])

    def add_breakdown(slice_id, author, child, added):
        per_author = breakdown.setdefault(slice_id, {}).setdefault(author, {})
        per_author[child] = per_author.get(child, 0) + added

    def add_trend(slice_id, author, added, removed):
        cell = (trends.setdefault(slice_id, {}).setdefault(author, {})
                .setdefault(current_month, [0, 0]))
        cell[0] += added
        cell[1] += removed
        lo, hi = month_bounds
        month_bounds[0] = current_month if lo is None else min(lo, current_month)
        month_bounds[1] = current_month if hi is None else max(hi, current_month)

    current_author = None
    current_ts = None
    current_month = None
    touched = set()  # slices touched by the current commit (for commit counts)

    def flush_commit():
        for slice_id in touched:
            e = entry_for(slice_id, current_author)
            e[0] += 1
            e[3] = min(e[3], current_ts)
            e[4] = max(e[4], current_ts)

    for line in out.splitlines():
        if line.startswith(sep):
            if current_author is not None:
                flush_commit()
            ts_str, author = line[len(sep):].split(sep, 1)
            current_ts = int(ts_str)
            current_author = canonical_for(author, alias_map)
            if trends is not None:
                dt = datetime.fromtimestamp(current_ts, tz=timezone.utc)
                current_month = dt.year * 12 + (dt.month - 1)
            touched = set()
        elif line.strip() and current_author is not None:
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            added_s, removed_s, raw_path = parts[0], parts[1], parts[2]
            added = 0 if added_s == "-" else int(added_s)
            removed = 0 if removed_s == "-" else int(removed_s)
            path = resolve_numstat_path(raw_path)
            if not path_matches_filter(path, ext_filter):
                continue
            for slice_id, child in display_slices_for_path(
                    path, root_id, start_index):
                e = entry_for(slice_id, current_author)
                e[1] += added
                e[2] += removed
                touched.add(slice_id)
                if added:
                    add_breakdown(slice_id, current_author, child, added)
                if trends is not None and (added or removed):
                    add_trend(slice_id, current_author, added, removed)

    if current_author is not None:
        flush_commit()
    month_range = tuple(month_bounds) if month_bounds[0] is not None else None
    return slice_stats, breakdown, trends, month_range


def collect_slice_survived(repo, alias_map, root_id, start_index, since_ts=None,
                           ext_filter=None):
    """Count HEAD lines per slice per author with a single git-blame pass.

    Blames every tracked file once, then folds each file's per-author line
    counts into every compressed ancestor slice (root + levels 1..MAX_LEVELS).
    Cost is one blame pass regardless of how many slices exist.

    When ``since_ts`` (a unix timestamp) is given, only lines whose author-time
    is on or after it are counted, so survived honours --since like the rest.
    ``ext_filter`` restricts blaming to files with the given extensions.
    """
    ls_cmd = ["git", "-C", repo, "ls-files", "-z"]
    if root_id:
        ls_cmd += ["--", root_id]
    try:
        files_out = subprocess.run(
            ls_cmd, capture_output=True, text=True, check=True
        ).stdout
    except subprocess.CalledProcessError as exc:
        sys.exit(f"error: git ls-files failed: {exc.stderr.strip() or exc}")

    slice_survived = {}
    for path in filter(None, files_out.split("\x00")):
        if not path_matches_filter(path, ext_filter):
            continue
        blame = subprocess.run(
            ["git", "-C", repo, "blame", "--line-porcelain", "HEAD", "--", path],
            capture_output=True, text=True, errors="replace",
        )
        if blame.returncode != 0:
            continue  # binary or otherwise un-blameable file
        # --line-porcelain repeats the full header (author + author-time) for
        # every line, so we can count and date-filter each line individually.
        file_counts = {}
        cur_name = None
        for line in blame.stdout.splitlines():
            if line.startswith("author "):
                cur_name = canonical_for(line[len("author "):], alias_map)
            elif line.startswith("author-time ") and cur_name is not None:
                if since_ts is not None and int(line[len("author-time "):]) < since_ts:
                    continue
                file_counts[cur_name] = file_counts.get(cur_name, 0) + 1
        if not file_counts:
            continue
        for slice_id, _child in display_slices_for_path(
                path, root_id, start_index):
            authors = slice_survived.setdefault(slice_id, {})
            for name, cnt in file_counts.items():
                authors[name] = authors.get(name, 0) + cnt
    return slice_survived


SPARK_AUTHORS = 6  # mini-graphs shown per slice (top authors by lines added)


def spark_series(slice_id, authors, trends, month_lo, n_months):
    """Top-SPARK_AUTHORS authors by added lines, each with dense monthly series.

    Returns a list of {a, ad, rm} where ad/rm are length-n_months arrays of
    added/removed lines per month over the shared analysis axis.
    """
    top = sorted(authors.items(), key=lambda it: (-it[1][1], it[0].lower()))
    slice_trends = trends.get(slice_id, {})
    out = []
    for name, _data in top[:SPARK_AUTHORS]:
        per_month = slice_trends.get(name, {})
        added = [0] * n_months
        removed = [0] * n_months
        for month_idx, (a, r) in per_month.items():
            pos = month_idx - month_lo
            added[pos] = a
            removed[pos] = r
        out.append({"a": name, "ad": added, "rm": removed})
    return out


def build_payload(slice_stats, slice_survived, columns, sort, root_id, meta,
                  display_meta, breakdown=None, trends=None, month_range=None):
    """Assemble the JSON payload embedded into the HTML for the JS to render.

    Slices are the compressed directory nodes from ``display_meta`` (plus the
    root). Each carries its collapsed ``label`` (e.g. ``src/test``), display
    ``level`` and ``parent`` from the compressed tree, so single-child chains
    appear as one cell instead of a stack of identical rings.

    When ``breakdown`` is given, each row gets a ``top`` list -- the up-to-3
    files/folders contributing most to that author's added lines in the slice --
    which the HTML surfaces as a hover popup on the Lines Added cell.

    When ``trends``/``month_range`` are given, each slice gets a ``spark`` list
    of the top authors' monthly added/removed series for the activity panel.
    """
    root_label = root_id if root_id else "All"
    want_spark = trends is not None and month_range is not None
    month_lo = n_months = 0
    if want_spark:
        month_lo, month_hi = month_range
        n_months = month_hi - month_lo + 1
    slices = {}
    for slice_id, authors in slice_stats.items():
        if slice_id != root_id and slice_id not in display_meta:
            continue  # history-only dir that no longer exists at HEAD
        survived = slice_survived.get(slice_id, {})
        slice_bd = breakdown.get(slice_id, {}) if breakdown is not None else None
        ordered = sorted(
            authors.items(), key=lambda it: sort_key(it, sort, survived)
        )
        rows = []
        added_total = 0
        for name, data in ordered:
            added_total += data[1]
            row = {"author": name}
            for c in columns:
                row[c] = metric_value(c, name, data, survived)
            if slice_bd is not None:
                top = sorted(slice_bd.get(name, {}).items(),
                             key=lambda kv: (-kv[1], kv[0]))[:3]
                row["top"] = [[child, n] for child, n in top]
            if "survived" in columns:
                # survived as a share of this author's added lines (added may
                # not be a displayed column, so compute it here)
                added_v = data[1]
                row["spct"] = round(row["survived"] / added_v * 100) if added_v else None
            rows.append(row)
        if slice_id == root_id:
            label, level, parent = root_label, 0, ""
        else:
            m = display_meta[slice_id]
            label, level, parent = m["label"], m["level"], m["parent"]
        slices[slice_id] = {
            "label": label,
            "level": level,
            "parent": parent,
            "added_total": added_total,
            "rows": rows,
        }
        if want_spark:
            slices[slice_id]["spark"] = spark_series(
                slice_id, authors, trends, month_lo, n_months)
    payload = {
        "columns": columns,
        "sort": sort,
        "root_id": root_id,
        "root_label": root_label,
        "meta": meta,
        "slices": slices,
    }
    if want_spark:
        payload["trends"] = {"labels": month_labels(month_lo, n_months)}
    return payload


def month_labels(month_lo, n_months):
    """['YYYY-MM', ...] for n_months starting at month index month_lo."""
    labels = []
    for i in range(n_months):
        m = month_lo + i
        labels.append(f"{m // 12:04d}-{m % 12 + 1:02d}")
    return labels


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { --bg:#0f1115; --panel:#171a21; --fg:#e6e6e6; --muted:#8a93a2;
          --line:#2a2f3a; --green:#3fb950; --red:#f85149; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--fg);
         font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
  header { padding:20px 24px 8px; }
  h1 { margin:0 0 4px; font-size:20px; }
  .sub { color:var(--muted); font-size:13px; }
  .sub code { color:#c9d1d9; }
  .wrap { display:flex; flex-wrap:wrap; gap:24px; padding:16px 24px 40px; align-items:flex-start; }
  .chart-card, .table-card { background:var(--panel); border:1px solid var(--line);
        border-radius:10px; padding:16px; }
  .chart-card { flex:0 0 auto; }
  .table-card { flex:1 1 480px; min-width:360px; }
  svg { display:block; max-width:100%; height:auto; }
  .slice { cursor:pointer; transition:opacity .1s; }
  .slice:hover { opacity:.82; }
  .slice.sel { stroke:#fff; stroke-width:2.5; }
  .center-label { fill:#fff; font-size:13px; font-weight:600; pointer-events:none; }
  .center-sub { fill:#dfe6f0; font-size:10px; pointer-events:none; }
  .crumbbar { display:flex; align-items:baseline; gap:8px; margin-bottom:10px; }
  .crumb { font-size:15px; font-weight:600; }
  .crumb-path { color:var(--muted); font-size:12px; word-break:break-all; }
  table { border-collapse:collapse; width:100%; font-variant-numeric:tabular-nums; }
  th, td { padding:6px 10px; text-align:left; border-bottom:1px solid var(--line); }
  th { color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase;
       letter-spacing:.03em; white-space:nowrap; }
  td.num, th.num { text-align:right; }
  th.sortable { cursor:pointer; user-select:none; }
  th.sortable:hover { color:var(--fg); }
  th.sorted { color:var(--fg); }
  .bd { position:relative; cursor:help; border-bottom:1px dotted currentColor; }
  .bd-pop { display:none; position:absolute; right:0; top:100%; z-index:20;
            margin-top:4px; padding:5px 8px; background:#0b0d12;
            border:1px solid var(--line); border-radius:6px; font-size:11px;
            line-height:1.5; white-space:nowrap; text-align:right; color:var(--fg);
            box-shadow:0 4px 14px rgba(0,0,0,.5); font-variant-numeric:tabular-nums; }
  .bd:hover .bd-pop { display:block; }
  tfoot td { font-weight:700; border-top:2px solid var(--line); border-bottom:none; }
  .added { color:var(--green); }
  .removed { color:var(--red); }
  .pct { color:var(--muted); font-size:11px; }
  .legend { margin-top:12px; color:var(--muted); font-size:12px; max-width:360px; }
  .hint { color:var(--muted); font-size:12px; margin-top:6px; }
  .empty { color:var(--muted); padding:12px 0; }
  .gap { margin-top:12px; color:var(--muted); font-size:12px; max-width:360px; }
  .gap b { color:var(--fg); font-weight:600; font-variant-numeric:tabular-nums; }
  .gap:empty { display:none; }
  .sparks:empty { display:none; }
  .sparks { margin-bottom:16px; padding-bottom:12px; border-bottom:1px solid var(--line); }
  .sparks-h { color:var(--muted); font-size:12px; margin-bottom:8px; }
  .sk-lg i { display:inline-block; width:10px; height:2px; vertical-align:middle;
             margin:0 3px 0 10px; }
  .sk-lg i.ad { background:var(--green); } .sk-lg i.rm { background:var(--red); }
  .sparks-row { display:flex; flex-wrap:wrap; gap:10px; }
  .sk { background:var(--bg); border:1px solid var(--line); border-radius:6px;
        padding:6px 8px; }
  .sk-name { font-size:11px; color:var(--fg); margin-bottom:3px; max-width:132px;
             overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .sk svg { display:block; }
  .sk polyline { fill:none; stroke-width:1.5; }
  .sk polyline.ad { stroke:var(--green); }
  .sk polyline.rm { stroke:var(--red); stroke-dasharray:1 1; }
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <div class="sub" id="meta"></div>
</header>
<div class="wrap">
  <div class="chart-card">
    <div id="chart"></div>
    <div class="gap" id="gap"></div>
    <div class="hint">Click a slice to scope the table &middot; click the center for the full tree.<br>
      Arrow keys: &uarr; outward &middot; &darr; inward (parent) &middot; &larr;/&rarr; around the ring.</div>
    <div class="legend">Slice size = lines added. Rings are directory levels 1&ndash;3;
      gaps in an outer ring are lines in files directly in the parent directory.</div>
  </div>
  <div class="table-card">
    <div class="crumbbar">
      <span class="crumb" id="crumb"></span>
      <span class="crumb-path" id="crumbpath"></span>
    </div>
    <div class="sparks" id="sparks"></div>
    <div id="table"></div>
  </div>
</div>
<script>
const DATA = __DATA__;
const slices = DATA.slices;
const rootId = DATA.root_id;
const columns = DATA.columns;
const HEADERS = {commits:"Commits", added:"Lines Added", removed:"Lines Removed",
                 churn:"Churn", tenancy:"Tenancy (months)", survived:"Survived Lines"};
const SUMMABLE = new Set(["commits","added","removed","churn","survived"]);
const TRENDS = DATA.trends || null;   // per-author activity mini-graphs (--trends)
const TAU = Math.PI * 2;

// Interactive sort state (headers are clickable). Metric columns default to
// descending, the Author column to ascending. This state is global, so the
// chosen sort persists as the user navigates between slices.
let sortCol = DATA.sort;
let sortDesc = sortCol !== "author";

// ---- meta line ----
(function(){
  const m = DATA.meta;
  const bits = [];
  bits.push("repo: <code>" + esc(m.repo) + "</code>");
  if (m.dir) bits.push("dir: <code>" + esc(m.dir) + "</code>");
  if (m.rev_range) bits.push("range: <code>" + esc(m.rev_range) + "</code>");
  if (m.since) bits.push("since: <code>" + esc(m.since) + "</code>");
  if (m.filter) bits.push("filter: <code>" + esc(m.filter) + "</code>");
  bits.push("generated " + esc(m.generated_date));
  document.getElementById("meta").innerHTML = bits.join(" &middot; ");
})();

// ---- build children map ----
const children = {};
for (const id in slices) children[id] = [];
for (const id in slices) {
  if (id === rootId) continue;
  const p = slices[id].parent;
  if (p in children) children[p].push(id);
}

// ---- layout angles (nested; children subdivide the parent arc) ----
function layout(id, start, end, hue) {
  const n = slices[id];
  n._a0 = start; n._a1 = end; n._hue = hue;
  const kids = (children[id] || []).slice()
        .sort((a, b) => slices[b].added_total - slices[a].added_total);
  // Fill the parent's whole arc: size each child relative to its SIBLINGS, not
  // the parent's own total. The parent's total also counts lines in files
  // directly in it and in since-deleted subfolders, which have no child cell;
  // normalising by the sibling sum redistributes that slack so no gaps remain.
  const kidsTotal = kids.reduce((s, k) => s + slices[k].added_total, 0);
  const isRoot = (id === rootId);
  let cur = start;
  kids.forEach((kid, i) => {
    const span = kidsTotal > 0
      ? (slices[kid].added_total / kidsTotal) * (end - start)
      : (end - start) / kids.length;   // all-zero siblings: divide equally
    const kh = isRoot ? (kids.length ? (i * 360 / kids.length) : 0) : hue;
    layout(kid, cur, cur + span, kh);
    cur += span;
  });
}
layout(rootId, 0, TAU, 0);

// ---- geometry ----
const R0 = 66, RW = 52;
const rings = [[R0, R0 + RW], [R0 + RW, R0 + 2 * RW], [R0 + 2 * RW, R0 + 3 * RW]];
const OUTER = R0 + 3 * RW;
const PAD = 6;
const SIZE = 2 * (OUTER + PAD);
const CX = SIZE / 2, CY = SIZE / 2;

function polar(r, ang) {
  return [CX + r * Math.cos(ang - Math.PI / 2), CY + r * Math.sin(ang - Math.PI / 2)];
}
function annular(r0, r1, a0, a1) {
  const large = (a1 - a0) > Math.PI ? 1 : 0;
  const [x0, y0] = polar(r1, a0);
  const [x1, y1] = polar(r1, a1);
  const [x2, y2] = polar(r0, a1);
  const [x3, y3] = polar(r0, a0);
  return `M${x0} ${y0} A${r1} ${r1} 0 ${large} 1 ${x1} ${y1} `
       + `L${x2} ${y2} A${r0} ${r0} 0 ${large} 0 ${x3} ${y3} Z`;
}
function arcPath(r0, r1, a0, a1) {
  const span = a1 - a0;
  if (span <= 1e-6) return "";
  if (span >= TAU - 1e-4) {            // full ring: split so start != end
    const mid = a0 + Math.PI;
    return annular(r0, r1, a0, mid) + annular(r0, r1, mid, a1);
  }
  return annular(r0, r1, a0, a1);
}

// ---- draw sunburst ----
const idList = [];      // idx -> slice id
const idxOf = {};       // slice id -> idx
let svg = `<svg viewBox="0 0 ${SIZE} ${SIZE}" width="${SIZE}" height="${SIZE}" `
        + `role="img" aria-label="Directory sunburst">`;
for (const id in slices) {
  const n = slices[id];
  if (n.level === 0 || n.level > 3) continue;
  const [ri, ro] = rings[n.level - 1];
  const d = arcPath(ri, ro, n._a0, n._a1);
  if (!d) continue;
  const light = [0, 56, 66, 76][n.level];
  const idx = idList.length; idList.push(id); idxOf[id] = idx;
  svg += `<path class="slice" data-idx="${idx}" d="${d}" `
       + `fill="hsl(${n._hue.toFixed(1)},58%,${light}%)" stroke="#171a21" stroke-width="1">`
       + `<title>${esc(id)}\n+${n.added_total.toLocaleString()} lines</title></path>`;
}
// center = root
{
  const idx = idList.length; idList.push(rootId); idxOf[rootId] = idx;
  svg += `<circle class="slice" data-idx="${idx}" cx="${CX}" cy="${CY}" r="${R0}" `
       + `fill="#5b6472"><title>${esc(DATA.root_label)}\n`
       + `+${slices[rootId].added_total.toLocaleString()} lines</title></circle>`;
  svg += `<text class="center-label" x="${CX}" y="${CY - 4}" text-anchor="middle">`
       + esc(clip(DATA.root_label, 14)) + `</text>`;
  svg += `<text class="center-sub" x="${CX}" y="${CY + 12}" text-anchor="middle">`
       + `+${slices[rootId].added_total.toLocaleString()}</text>`;
}
svg += `</svg>`;
document.getElementById("chart").innerHTML = svg;

document.querySelectorAll(".slice").forEach(el => {
  el.addEventListener("click", () => select(idList[+el.dataset.idx]));
});

// ---- keyboard navigation ----
// Members of each ring (only drawn slices), ordered clockwise by start angle.
const ringOf = {};
idList.forEach(id => {
  const lv = slices[id].level;
  (ringOf[lv] = ringOf[lv] || []).push(id);
});
Object.keys(ringOf).forEach(lv =>
  ringOf[lv].sort((a, b) => slices[a]._a0 - slices[b]._a0));

function navigate(dir) {
  const cur = selected;
  const lv = slices[cur].level;
  if (dir === "up") {                 // outward: first child cell of the next ring
    const kids = (children[cur] || []).filter(k => k in idxOf)
          .sort((a, b) => slices[a]._a0 - slices[b]._a0);
    if (kids.length) select(kids[0]);
  } else if (dir === "down") {        // inward: the parent cell
    if (lv > 0 && slices[cur].parent in idxOf) select(slices[cur].parent);
  } else {                            // left/right: prev/next cell in the same ring
    const ring = ringOf[lv] || [];
    const i = ring.indexOf(cur);
    if (ring.length <= 1 || i < 0) return;
    const step = dir === "right" ? 1 : -1;
    select(ring[(i + step + ring.length) % ring.length]);  // wraps around the ring
  }
}

document.addEventListener("keydown", e => {
  const map = {ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right"};
  const d = map[e.key];
  if (!d) return;
  e.preventDefault();
  navigate(d);
});

// ---- selection + table ----
let selected = null;
function select(id) {
  selected = id;
  document.querySelectorAll(".slice").forEach(el => {
    el.classList.toggle("sel", +el.dataset.idx === idxOf[id]);
  });
  renderTable();
}
function cellClass(c, v) {
  if (c === "added") return "added";
  if (c === "removed") return "removed";
  if (c === "churn") return v > 0 ? "added" : (v < 0 ? "removed" : "");
  return "";
}
function compareRows(a, b) {
  let av, bv;
  if (sortCol === "author") { av = a.author.toLowerCase(); bv = b.author.toLowerCase(); }
  else { av = a[sortCol]; bv = b[sortCol]; }
  let cmp = av < bv ? -1 : (av > bv ? 1 : 0);
  if (sortDesc) cmp = -cmp;
  if (cmp === 0 && sortCol !== "author") {   // stable tie-break: author A->Z
    const an = a.author.toLowerCase(), bn = b.author.toLowerCase();
    cmp = an < bn ? -1 : (an > bn ? 1 : 0);
  }
  return cmp;
}
function setSort(col) {
  if (col === sortCol) sortDesc = !sortDesc;        // same column: reverse
  else { sortCol = col; sortDesc = col !== "author"; }
  renderTable();
}
function renderGap() {
  // How much of this slice's added lines is captured by its child rings. The
  // remainder (not shown) is lines in files directly in this folder plus lines
  // from since-deleted files/folders that have no child cell.
  const el = document.getElementById("gap");
  const kids = children[selected] || [];
  const total = slices[selected].added_total;
  if (!kids.length || total <= 0) { el.innerHTML = ""; return; }  // leaf: nothing to compare
  const kidsSum = kids.reduce((a, k) => a + slices[k].added_total, 0);
  const pct = kidsSum / total * 100;
  el.innerHTML =
    `Shown in sub-folder rings: <b>${kidsSum.toLocaleString()}</b> of `
    + `<b>${total.toLocaleString()}</b> added lines (<b>${pct.toFixed(1)}%</b>) `
    + `— the rest is files directly in this folder or in since-deleted files/folders.`;
}
function sparkPoints(vals, w, h, maxv) {
  // Map a value series to "x,y ..." polyline points; y is inverted (0 at bottom).
  const n = vals.length;
  return vals.map((v, i) => {
    const x = n > 1 ? i * w / (n - 1) : w / 2;
    const y = maxv > 0 ? h - (v / maxv) * h : h;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}
function renderSparks() {
  // Panel of mini dual-line graphs (added=green, removed=red) over the analysis
  // period, for the selected slice's top authors by lines added.
  const el = document.getElementById("sparks");
  const spark = TRENDS && slices[selected].spark;
  if (!spark || !spark.length) { el.innerHTML = ""; return; }
  const W = 132, H = 34, P = 3, iw = W - 2 * P, ih = H - 2 * P;
  const span = TRENDS.labels.length
    ? `${TRENDS.labels[0]} → ${TRENDS.labels[TRENDS.labels.length - 1]}` : "";
  let h = `<div class="sparks-h">Top ${spark.length} by lines added `
        + `&middot; ${esc(span)} <span class="sk-lg">`
        + `<i class="ad"></i>added<i class="rm"></i>removed</span></div>`
        + `<div class="sparks-row">`;
  for (const a of spark) {
    const maxv = Math.max(1, ...a.ad, ...a.rm);
    const totAd = a.ad.reduce((x, y) => x + y, 0);
    const totRm = a.rm.reduce((x, y) => x + y, 0);
    h += `<div class="sk" title="${esc(a.a)} — +${totAd.toLocaleString()} / `
       + `-${totRm.toLocaleString()} lines">`
       + `<div class="sk-name">${esc(clip(a.a, 18))}</div>`
       + `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`
       + `<g transform="translate(${P},${P})">`
       + `<polyline class="ad" points="${sparkPoints(a.ad, iw, ih, maxv)}"/>`
       + `<polyline class="rm" points="${sparkPoints(a.rm, iw, ih, maxv)}"/>`
       + `</g></svg></div>`;
  }
  el.innerHTML = h + "</div>";
}
function renderTable() {
  const s = slices[selected];
  const crumb = document.getElementById("crumb");
  const crumbpath = document.getElementById("crumbpath");
  crumb.textContent = selected === rootId ? DATA.root_label : s.label;
  crumbpath.textContent = selected === rootId ? "" : selected;
  renderGap();
  renderSparks();

  const box = document.getElementById("table");
  if (!s.rows.length) { box.innerHTML = '<div class="empty">No commits in this slice.</div>'; return; }

  const arrow = c => c === sortCol ? (sortDesc ? " ▼" : " ▲") : "";
  const th = (col, label, extra) =>
    `<th class="sortable${extra || ""}${col === sortCol ? " sorted" : ""}" `
    + `data-col="${col}">${esc(label)}${arrow(col)}</th>`;

  let h = "<table><thead><tr>" + th("author", "Author", "");
  columns.forEach(c => h += th(c, HEADERS[c], " num"));
  h += "</tr></thead><tbody>";

  const totals = {};
  columns.forEach(c => totals[c] = 0);
  const rows = s.rows.slice().sort(compareRows);
  for (const r of rows) {
    h += `<tr><td>${esc(r.author)}</td>`;
    for (const c of columns) {
      const v = r[c];
      if (SUMMABLE.has(c)) totals[c] += v;
      let inner = v.toLocaleString();
      if (c === "added" && r.top && r.top.length) {   // hover breakdown
        const lines = r.top
          .map(t => `${esc(t[0])}: ${t[1].toLocaleString()}`).join("<br>");
        inner = `<span class="bd">${inner}<span class="bd-pop">${lines}</span></span>`;
      }
      if (c === "survived" && r.spct != null) inner += ` <span class="pct">(${r.spct}%)</span>`;
      h += `<td class="num ${cellClass(c, v)}">${inner}</td>`;
    }
    h += "</tr>";
  }
  h += "</tbody><tfoot><tr><td>TOTAL</td>";
  for (const c of columns) {
    if (SUMMABLE.has(c)) {
      let ft = totals[c].toLocaleString();
      if (c === "survived" && s.added_total > 0) {  // survived as share of added
        ft += ` <span class="pct">(${Math.round(totals.survived / s.added_total * 100)}%)</span>`;
      }
      h += `<td class="num ${cellClass(c, totals[c])}">${ft}</td>`;
    } else {
      h += `<td class="num"></td>`;
    }
  }
  h += "</tr></tfoot></table>";
  box.innerHTML = h;
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function clip(s, n) { return s.length > n ? s.slice(0, n - 1) + "…" : s; }

// Header clicks change the sort; delegated so it survives table re-renders.
document.getElementById("table").addEventListener("click", e => {
  const th = e.target.closest("th[data-col]");
  if (th) setSort(th.dataset.col);
});

select(rootId);
</script>
</body>
</html>
"""


def render_html(payload):
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    title = payload["meta"]["title"]
    return (
        HTML_TEMPLATE
        .replace("__DATA__", data_json)
        .replace("__TITLE__", _html_escape(title))
    )


def _html_escape(s):
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main(argv=None):
    args = parse_args(argv)
    columns = parse_columns(args.columns)
    alias_map = build_alias_map(args.merge)
    root_id = normalize_root(args.dir)

    # Sorting is now interactive (clickable headers in the HTML); this is only
    # the initial column the table opens with.
    sort = "added" if "added" in columns else columns[0]
    since, since_ts = parse_since(args.since)
    ext_filter = parse_filter(args.filter)

    children_map = build_dir_tree(args.repo, root_id, ext_filter=ext_filter)
    display_meta, start_index = build_display_tree(children_map, root_id)

    slice_stats, breakdown, trends, month_range = collect_slice_stats(
        args.repo, args.rev_range, alias_map, root_id, start_index, since=since,
        want_trends=args.trends, ext_filter=ext_filter)
    if root_id not in slice_stats:
        print("No commits found.")
        return

    need_survived = "survived" in columns
    slice_survived = (
        collect_slice_survived(args.repo, alias_map, root_id, start_index,
                               since_ts=since_ts, ext_filter=ext_filter)
        if need_survived else {}
    )

    today = datetime.now().date().isoformat()
    scope = f" [{root_id}]" if root_id else ""
    meta = {
        "repo": args.repo,
        "rev_range": args.rev_range or "",
        "dir": root_id,
        "since": since or "",
        "filter": ",".join(sorted(ext_filter)) if ext_filter else "",
        "generated_date": today,
        "title": f"git-stats {today}{scope}",
    }
    payload = build_payload(slice_stats, slice_survived, columns, sort, root_id,
                            meta, display_meta, breakdown=breakdown,
                            trends=trends, month_range=month_range)
    html = render_html(payload)

    out_path = f"git-stats-{today}.html"
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(out_path)


if __name__ == "__main__":
    main()
