from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class NetworkExposurePolicy:
    allowed_hosts: tuple[str, ...] = ("127.0.0.1", "localhost")
    forbid_wildcard_cors: bool = True
    forbid_debug_ports: bool = True
    require_https_at_edge: bool = True


class NetworkExposureValidator:
    DEBUG_PORTS = {3000, 5000, 5173, 8000, 8080, 8888}

    def __init__(self, policy: NetworkExposurePolicy | None = None) -> None:
        self.policy = policy or NetworkExposurePolicy()

    def validate_allowed_hosts(self, hosts: Iterable[str]) -> list[str]:
        host_set = {str(host).strip() for host in hosts if str(host).strip()}
        findings: list[str] = []
        if "*" in host_set and self.policy.forbid_wildcard_cors:
            findings.append("wildcard host exposure is forbidden in production")
        if not host_set:
            findings.append("allowed hosts cannot be empty")
        if "0.0.0.0" in host_set:
            findings.append("0.0.0.0 is a bind address, not a safe allowed host")
        return findings

    def validate_cors_origins(self, origins: Iterable[str]) -> list[str]:
        origin_set = {str(origin).strip() for origin in origins if str(origin).strip()}
        findings: list[str] = []
        if self.policy.forbid_wildcard_cors and "*" in origin_set:
            findings.append("wildcard CORS origin is forbidden in production")
        for origin in origin_set:
            if origin.startswith("http://") and self.policy.require_https_at_edge:
                if "localhost" not in origin and "127.0.0.1" not in origin:
                    findings.append(f"non-local production origin must use HTTPS: {origin}")
        return findings

    def validate_port(self, port: int) -> list[str]:
        if self.policy.forbid_debug_ports and port in self.DEBUG_PORTS:
            return [f"debug/development port is not production-hardened: {port}"]
        if port <= 0 or port > 65535:
            return [f"invalid TCP port: {port}"]
        return []
