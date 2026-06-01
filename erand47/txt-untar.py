#!/usr/bin/env python3
"""txt-untar.py - Apply a txt-tar archive (snapshot or patch) to disk.

Format: see txt-tar.py.

Operations recognised in the filename slot:
    (none) or "= path"   write file (create or overwrite)
    "+ path"             create new; error if exists (unless --force)
    "- path"             delete file or symlink
    "> old -> new"       rename; if body non-empty, also writes new content

Safety guards (refusable, all on by default):
    Paths must stay inside the output directory; absolute paths and
    `..` escapes are refused. Symlink targets are validated similarly
    unless --allow-unsafe-links is given.
"""
import argparse
import base64
import os
import re
import sys
from pathlib import Path

FS = '\x1c'
RS = '\x1d'

RE_BIN = re.compile(r'^<BIN>(.*)</BIN>$', re.DOTALL)
RE_LINK = re.compile(r'^<LINK>(.*)</LINK>$', re.DOTALL)
RE_RENAME = re.compile(r'^(.*?)\s*->\s*(.*)$')


def parse_entry_name(raw: str):
    """Return (op, path, path2) where path2 is set only for rename."""
    name = raw.strip()
    if not name:
        return None
    if len(name) > 2 and name[1] == ' ' and name[0] in '=+->':
        op = name[0]
        rest = name[2:].strip()
    else:
        op = '='
        rest = name
    if op == '>':
        m = RE_RENAME.match(rest)
        if not m:
            raise ValueError(f"rename entry missing '->': {raw!r}")
        return op, m.group(1).strip(), m.group(2).strip()
    return op, rest, None


def parse_archive(text: str):
    """Yield (op, path, path2, body) for each entry. Header is skipped."""
    for chunk in text.split(FS):
        if RS not in chunk:
            continue  # header chunk or noise after final terminator
        name_part, body = chunk.split(RS, 1)
        parsed = parse_entry_name(name_part)
        if parsed is None:
            continue
        op, p1, p2 = parsed
        yield op, p1, p2, body


def decode_body(body: str):
    """Return (kind, content). kind is 'text'|'binary'|'symlink'."""
    s = body.strip()
    m = RE_BIN.match(s)
    if m:
        return 'binary', base64.b64decode(m.group(1))
    m = RE_LINK.match(s)
    if m:
        return 'symlink', m.group(1).strip()
    return 'text', body  # keep raw - do NOT strip text content


def safe_join(base: Path, rel: str) -> Path:
    if not rel:
        raise ValueError("empty path")
    p = Path(rel)
    if p.is_absolute():
        raise ValueError(f"absolute path refused: {rel}")
    target = (base / p).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        raise ValueError(f"path escapes output dir: {rel}")
    return target


def validate_link_target(target: str, link_path: Path, output_dir: Path,
                         allow_unsafe: bool) -> str:
    if allow_unsafe:
        return target
    tp = Path(target)
    if tp.is_absolute():
        raise ValueError(f"absolute symlink refused: -> {target}")
    resolved = (link_path.parent / tp).resolve()
    try:
        resolved.relative_to(output_dir.resolve())
    except ValueError:
        raise ValueError(f"symlink escapes output dir: -> {target}")
    return target


def write_atomic(path: Path, data, binary=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (path.name + '.tmp')
    mode = 'wb' if binary else 'w'
    kwargs = {} if binary else {'encoding': 'utf-8'}
    with open(tmp, mode, **kwargs) as f:
        f.write(data)
    os.replace(tmp, path)


def apply_entry(op, p1, p2, body, output_dir, *, force, no_clobber,
                allow_unsafe_links, dry_run, verbose):
    if op == '-':
        target = safe_join(output_dir, p1)
        if dry_run:
            print(f"[dry] delete {p1}")
            return
        if target.is_symlink() or target.exists():
            target.unlink()
            print(f"[-] {p1}")
        elif verbose:
            print(f"[ ] {p1} (not present)")
        return

    if op == '>':
        src = safe_join(output_dir, p1)
        dst = safe_join(output_dir, p2)
        if dry_run:
            print(f"[dry] rename {p1} -> {p2}"
                  + (" (and rewrite)" if body.strip() else ""))
            if not body.strip():
                return
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.rename(src, dst)
            print(f"[>] {p1} -> {p2}")
            if not body.strip():
                return
        # Fall through to rewrite dst with the new body
        op = '='
        p1 = p2

    target = safe_join(output_dir, p1)
    kind, content = decode_body(body)

    if op == '+' and target.exists() and not force:
        raise ValueError(f"+ refused: {p1} already exists (use --force)")
    if no_clobber and (target.exists() or target.is_symlink()):
        if verbose:
            print(f"[ ] {p1} (kept, --no-clobber)")
        return

    if kind == 'symlink':
        link_target = validate_link_target(content, target, output_dir,
                                           allow_unsafe_links)
        if dry_run:
            print(f"[dry] symlink {p1} -> {link_target}")
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or target.exists():
            target.unlink()
        os.symlink(link_target, target)
        print(f"[L] {p1} -> {link_target}")
        return

    if kind == 'binary':
        if dry_run:
            print(f"[dry] write binary {p1} ({len(content)} bytes)")
            return
        write_atomic(target, content, binary=True)
        print(f"[B] {p1}")
        return

    if dry_run:
        print(f"[dry] write text {p1} ({len(content)} bytes)")
        return
    write_atomic(target, content, binary=False)
    print(f"[T] {p1}")


def main():
    parser = argparse.ArgumentParser(
        description="Apply a txt-tar archive (snapshot or patch) to disk.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    txt-untar project.txt                 Extract into ./project/
    txt-untar project.txt -o ./out        Extract into a chosen directory
    txt-untar patch.txt -o .              Apply a patch to current dir
    txt-untar project.txt --dry-run -v    Show what would happen
""",
    )
    parser.add_argument('archive', help='Archive file')
    parser.add_argument('-o', '--output',
                        help='Output directory (default: <archive stem>/)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show actions without writing')
    parser.add_argument('--force', action='store_true',
                        help="Allow '+' op to overwrite existing files")
    parser.add_argument('--no-clobber', action='store_true',
                        help='Skip writing if target already exists')
    parser.add_argument('--allow-unsafe-links', action='store_true',
                        help='Allow symlinks that point outside the output dir')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show skipped entries and other detail')
    args = parser.parse_args()

    arc = Path(args.archive)
    if not arc.exists():
        print(f"Error: archive not found: {arc}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output) if args.output else Path(arc.stem)
    output_dir = output_dir.resolve()
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output: {output_dir}", file=sys.stderr)

    text = arc.read_text(encoding='utf-8')

    n = 0
    errors = 0
    for op, p1, p2, body in parse_archive(text):
        try:
            apply_entry(op, p1, p2, body, output_dir,
                        force=args.force, no_clobber=args.no_clobber,
                        allow_unsafe_links=args.allow_unsafe_links,
                        dry_run=args.dry_run, verbose=args.verbose)
            n += 1
        except (ValueError, OSError) as e:
            print(f"[!] {p1}: {e}", file=sys.stderr)
            errors += 1

    print(f"\n[OK] {n} entries processed, {errors} errors", file=sys.stderr)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
