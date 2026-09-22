"""Trust the local TLS-inspecting proxy without turning verification off.

Some development machines run an antivirus/corporate proxy that terminates TLS
and re-signs every certificate with a locally installed root. Two things then
break for any crawler:

1. The proxy root is not in `certifi`, so the chain does not validate.
2. Python 3.13+ enables ``ssl.VERIFY_X509_STRICT`` in
   ``ssl.create_default_context()``. Several of these proxy roots (Avast's
   ``wscert.pem`` among them) encode ``basicConstraints`` as non-critical,
   which strict mode rejects with::

       CERTIFICATE_VERIFY_FAILED: Basic Constraints of CA cert not marked critical

The usual workaround is ``verify=False`` / ``CERT_NONE``. That is worse than the
problem: it disables hostname and chain checking for *every* host, so a crawl
can no longer tell a real server from anything that answers on port 443.

This shim keeps full chain + hostname verification. It only:

* adds the local proxy root to the trust store, and
* clears ``VERIFY_X509_STRICT`` so the proxy root's encoding quirk is tolerated.

It is opt-in and inert unless ``GREENSCAN_TRUST_LOCAL_PROXY=1`` is set, and it
is not on ``sys.path`` by default -- callers must add this directory to
``PYTHONPATH``. Never enable it in production; fix the trust store instead.

Usage (PowerShell)::

    $env:PYTHONPATH = "<repo>/tools/local_proxy_tls"
    $env:GREENSCAN_TRUST_LOCAL_PROXY = "1"
    python -m crawler.cli --config configs/companies.yml --company vnm --dry-run

Override the root with ``GREENSCAN_LOCAL_PROXY_CA=<path-to-pem>`` if the
autodetected locations do not match this machine.
"""

from __future__ import annotations

import os
import ssl
import tempfile
from pathlib import Path

_FLAG = "GREENSCAN_TRUST_LOCAL_PROXY"

# Known locations where TLS-inspecting security products drop their root.
_CANDIDATE_ROOTS = (
    r"C:\ProgramData\Avast Software\Avast\wscert.pem",
    r"C:\ProgramData\AVG\Antivirus\wscert.pem",
    r"C:\ProgramData\Kaspersky Lab\AVP\cert\(fake)Kaspersky Anti-Virus personal root certificate.cer",
)


def _proxy_roots() -> list[Path]:
    explicit = os.environ.get("GREENSCAN_LOCAL_PROXY_CA")
    paths = [Path(explicit)] if explicit else [Path(p) for p in _CANDIDATE_ROOTS]
    return [p for p in paths if p.is_file()]


def _combined_bundle() -> Path | None:
    """certifi's roots plus the local proxy roots, written to one PEM."""
    roots = _proxy_roots()
    if not roots:
        return None

    try:
        import certifi

        base = Path(certifi.where()).read_bytes()
    except Exception:  # noqa: BLE001 - certifi missing is not fatal here
        base = b""

    blob = base
    for root in roots:
        blob += b"\n" + root.read_bytes()

    out = Path(tempfile.gettempdir()) / "greenscan_local_proxy_ca.pem"
    if not out.is_file() or out.read_bytes() != blob:
        out.write_bytes(blob)
    return out


def _install() -> None:
    bundle = _combined_bundle()
    if bundle is None:
        return

    # httpx/requests/urllib all end up here, and libraries that build their own
    # SSLContext still call load_verify_locations on it.
    original_create = ssl.create_default_context
    original_load = ssl.SSLContext.load_verify_locations

    def create_default_context(*args, **kwargs):  # type: ignore[no-untyped-def]
        ctx = original_create(*args, **kwargs)
        _relax(ctx)
        return ctx

    def load_verify_locations(self, cafile=None, capath=None, cadata=None):  # type: ignore[no-untyped-def]
        result = original_load(self, cafile=cafile, capath=capath, cadata=cadata)
        _relax(self)
        return result

    def _relax(ctx: ssl.SSLContext) -> None:
        try:
            original_load(ctx, cafile=str(bundle))
        except ssl.SSLError:
            pass
        # Chain and hostname verification stay ON; only the strict DER-encoding
        # check that rejects the proxy root is cleared.
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT

    ssl.create_default_context = create_default_context  # type: ignore[assignment]
    ssl.SSLContext.load_verify_locations = load_verify_locations  # type: ignore[assignment]

    os.environ.setdefault("SSL_CERT_FILE", str(bundle))
    os.environ.setdefault("REQUESTS_CA_BUNDLE", str(bundle))


if os.environ.get(_FLAG) == "1":
    _install()
