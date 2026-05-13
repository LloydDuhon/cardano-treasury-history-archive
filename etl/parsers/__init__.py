"""Parsers - convert third-party document formats into structured intermediates.

Each parser is a pure function: takes a path (or bytes) and returns a list of
dicts plus optional metadata. Parsers write intermediate JSON sidecars under
data/funds/fund-XX/_intermediate/ so the same parse output can be replayed
without re-running the parser.
"""
