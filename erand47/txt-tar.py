#!/usr/bin/env python3
"""txt-tar.py - Pack a directory tree into a single text archive that
survives copy/paste through AI chat interfaces.

This file is also the format spec - txt-untar.py reads the same shape.

WIRE FORMAT
    Header: human-readable '#' comment lines.
    Separator: a line containing exactly "---".
    Entries: each is  FS  filename  RS  body  with FS=0x1C, RS=0x1D.
    A final FS terminates the last entry so trailing whitespace cannot
    bleed into its body.

    body is one of:
        plain UTF-8 text
        <BIN>base64</BIN>      for binary files
        <LINK>target</LINK>    for symlinks

    filename slot may carry an op prefix (used by txt-untar for patches):
        (none)            -> default: update or create
        "= path"          -> same as no prefix
        "+ path"          -> create new (error if exists, unless --force)
        "- path"          -> delete
        "> old -> new"    -> rename; if body non-empty, also write content

    A snapshot is just a patch where every op is `=`. txt-tar emits
    snapshots; txt-untar accepts either.
"""
import argparse
import base64
import os
import sys
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

FS = '\x1c'
RS = '\x1d'

DEFAULT_EXCLUDES = [
    '.git', '.hg', '.svn',
    '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.venv', 'node_modules',
    '.idea', '.vscode',
    '.DS_Store', 'Thumbs.db',
    '*.pyc', '*.pyo', '*~', '*.swp',
]


def is_binary(data: bytes) -> bool:
    if not data:
        return False
    if b'\x00' in data:
        return True
    try:
        data.decode('utf-8')
        return False
    except UnicodeDecodeError:
        return True


def matches_any(rel_path: str, patterns) -> bool:
    if not patterns:
        return False
    name = rel_path.rsplit('/', 1)[-1]
    parts = rel_path.split('/')
    for pat in patterns:
        if fnmatch(rel_path, pat) or fnmatch(name, pat):
            return True
        if any(fnmatch(p, pat) for p in parts):
            return True
    return False


def should_include(rel_path, name, suffix,
                   include_ext, include_noext,
                   include_files, exclude_patterns):
    if matches_any(rel_path, exclude_patterns):
        return False
    if include_files:
        return matches_any(rel_path, include_files)
    if include_ext:
        if suffix:
            return suffix.lower() in include_ext
        return include_noext
    return True


def encode_body(file_path: Path) -> tuple:
    """Return (kind, body_string) where kind is 'text'|'binary'|'symlink'."""
    if file_path.is_symlink():
        target = os.readlink(file_path)
        return 'symlink', f"<LINK>{target}</LINK>"
    data = file_path.read_bytes()
    if is_binary(data):
        b64 = base64.b64encode(data).decode('ascii')
        return 'binary', f"<BIN>{b64}</BIN>"
    text = data.decode('utf-8')
    if FS in text or RS in text:
        raise ValueError(
            f"contains FS (0x1C) or RS (0x1D) byte - "
            f"cannot be packed safely with this format"
        )
    return 'text', text


def collect_files(directory, include_ext, include_noext,
                  include_files, exclude_patterns):
    base = directory.resolve()
    out = []
    for item in base.rglob('*'):
        if item.is_dir() and not item.is_symlink():
            continue
        rel = item.relative_to(base).as_posix()
        if should_include(rel, item.name, item.suffix,
                          include_ext, include_noext,
                          include_files, exclude_patterns):
            out.append(item)
    return sorted(set(out))


def build_tree(rel_paths):
    """Render a sorted list of relative paths as an indented tree."""
    tree = {}
    for rp in rel_paths:
        node = tree
        for part in rp.split('/'):
            node = node.setdefault(part, {})

    out = []

    def walk(node, depth):
        for name in sorted(node):
            child = node[name]
            suffix = '/' if child else ''
            out.append(f"#   {'  ' * depth}{name}{suffix}")
            if child:
                walk(child, depth + 1)

    walk(tree, 0)
    return out


def build_header(files, kinds, rel_paths, directories, base_path, include_ext):
    text_n = sum(1 for k in kinds if k == 'text')
    bin_n = sum(1 for k in kinds if k == 'binary')
    link_n = sum(1 for k in kinds if k == 'symlink')
    lines = [
        "# txt-tar archive",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Files: {len(files)} ({text_n} text, {bin_n} binary, {link_n} symlinks)",
        "#",
        "# Format: <FS>[op ]path<RS>body  with FS=0x1C, RS=0x1D, final FS terminator",
        "# Body:   text | <BIN>base64</BIN> | <LINK>target</LINK>",
        "# Ops:    = + - >  (see txt-untar.py for semantics)",
    ]
    if include_ext:
        lines.append(f"# Extensions: {', '.join(include_ext)}")
    if len(directories) > 1:
        lines.append("# Roots:")
        for d in directories:
            try:
                lines.append(f"#   {d.relative_to(base_path)}")
            except ValueError:
                lines.append(f"#   {d}")
    lines.append("#")
    lines.append("# Tree:")
    lines.extend(build_tree(rel_paths))
    lines += ["#", "---", ""]
    return "\n".join(lines)


def create_archive(files, base_path, directories, include_ext):
    bodies = []
    kinds = []
    for i, fp in enumerate(files, 1):
        rel = fp.relative_to(base_path).as_posix()
        print(f"\rPacking {i}/{len(files)}: {rel}",
              end='', flush=True, file=sys.stderr)
        try:
            kind, body = encode_body(fp)
        except ValueError as e:
            print(f"\n[ERROR] {rel}: {e}", file=sys.stderr)
            sys.exit(2)
        except OSError as e:
            print(f"\n[ERROR] {rel}: {e}", file=sys.stderr)
            sys.exit(2)
        kinds.append(kind)
        bodies.append((rel, body))

    rel_paths = [rel for rel, _ in bodies]
    header = build_header(files, kinds, rel_paths, directories, base_path,
                          include_ext)
    parts = [header]
    for rel, body in bodies:
        parts.append(f"{FS}{rel}{RS}{body}")
    parts.append(FS)  # terminate last body
    print(f"\n[OK] Packed {len(files)} entries", file=sys.stderr)
    return ''.join(parts)


def write_atomic(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (path.name + '.tmp')
    tmp.write_text(text, encoding='utf-8')
    os.replace(tmp, path)


def main():
    parser = argparse.ArgumentParser(
        description="Pack a directory tree into a single text archive.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    txt-tar src/                            Archive one directory
    txt-tar src/ docs/                      Archive multiple directories
    txt-tar src/ -o project.txt             Write to file
    txt-tar src/ --include-ext .py .md      Only .py and .md
    txt-tar src/ --include-ext .c --include-noext
                                            Add extensionless files (Makefile)
    txt-tar src/ --include-files "README*"  Only README files
    txt-tar src/ --exclude "*.log" tmp      Add patterns to default excludes
""",
    )
    parser.add_argument('directories', nargs='+', help='Directories to archive')
    parser.add_argument('--include-ext', nargs='*',
                        help='Only include files with these extensions')
    parser.add_argument('--include-noext', action='store_true',
                        help='With --include-ext, also include extensionless files')
    parser.add_argument('--include-files', nargs='*',
                        help='Only include files matching these glob patterns')
    parser.add_argument('--exclude', nargs='*', default=[],
                        help='Additional exclude patterns (added to defaults)')
    parser.add_argument('--no-default-excludes', action='store_true',
                        help='Disable the built-in exclude list')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    args = parser.parse_args()

    directories = [Path(d).resolve() for d in args.directories]
    for d in directories:
        if not d.is_dir():
            print(f"Error: not a directory: {d}", file=sys.stderr)
            sys.exit(1)

    include_ext = None
    if args.include_ext:
        include_ext = [
            (e if e.startswith('.') else '.' + e).lower()
            for e in args.include_ext
        ]

    excludes = list(args.exclude)
    if not args.no_default_excludes:
        excludes = DEFAULT_EXCLUDES + excludes

    if len(directories) == 1:
        base_path = directories[0]
    else:
        base_path = Path(os.path.commonpath([str(d) for d in directories]))

    all_files = []
    for d in directories:
        all_files.extend(
            collect_files(d, include_ext, args.include_noext,
                          args.include_files, excludes)
        )
    all_files = sorted(set(all_files))

    if not all_files:
        print("Error: no files to pack", file=sys.stderr)
        sys.exit(1)

    archive = create_archive(all_files, base_path, directories, include_ext)

    if args.output:
        out = Path(args.output)
        write_atomic(out, archive)
        print(f"Wrote: {out}", file=sys.stderr)
    else:
        sys.stdout.write(archive)


if __name__ == '__main__':
    main()
