# utils/parser_utils.py (buat file ini kalau belum ada)

from app_v3_PAMLLG_FA.schema import PrimaryAgentOutput

def ensure_primary_result_object(data) -> PrimaryAgentOutput:
    if isinstance(data, PrimaryAgentOutput):
        return data
    return PrimaryAgentOutput(**data)
