from __future__ import annotations

from fastapi import APIRouter, Request

from runtime_core.api.dependency_chain_proof import build_dependency_chain_proof


router = APIRouter(tags=["Dependency Chain Proof"])


@router.get("/api/system/dependency-chain-proof")
def get_dependency_chain_proof(request: Request) -> dict:
    return build_dependency_chain_proof(request.app)


@router.get("/proof/dependency-chain")
def get_dependency_chain_proof_alias(request: Request) -> dict:
    return build_dependency_chain_proof(request.app)

