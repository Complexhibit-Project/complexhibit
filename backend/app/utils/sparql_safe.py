"""
Helpers to safely embed user-controlled values into SPARQL queries.

These prevent SPARQL injection in the two contexts used across the routers:
  * inside a double-quoted string literal  -> escape_sparql_string
  * inside an IRI reference  <...>          -> escape_sparql_iri
"""

# Characters that would let an attacker break out of a <...> IRI reference.
_IRI_UNSAFE = {
    "<": "%3C", ">": "%3E", '"': "%22", "{": "%7B", "}": "%7D",
    "|": "%7C", "\\": "%5C", "^": "%5E", "`": "%60", " ": "%20",
}


def escape_sparql_string(value: str) -> str:
    """Escape a value for safe use inside a SPARQL double-quoted string literal."""
    if value is None:
        return ""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def escape_sparql_iri(value: str) -> str:
    """
    Neutralize characters that could break out of a SPARQL IRI reference.

    Legitimate ids (hex hashes, simple slugs) are left unchanged; only
    IRI-illegal / control characters are percent-encoded.
    """
    if value is None:
        return ""
    out = []
    for ch in str(value):
        if ch in _IRI_UNSAFE:
            out.append(_IRI_UNSAFE[ch])
        elif ord(ch) < 0x20 or ord(ch) == 0x7F:
            out.append("%{:02X}".format(ord(ch)))
        else:
            out.append(ch)
    return "".join(out)
