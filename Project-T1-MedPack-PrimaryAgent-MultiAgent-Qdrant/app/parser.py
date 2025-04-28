# app/parser.py

from langchain_core.output_parsers import JsonOutputParser  # type: ignore
from app.schema import (
    AnomalyResult, 
    DetectionResult, 
    FinalOutput,
    BatchAndExpiryResult,  # tambahkan
    QuantityResult          # tambahkan
)

anomaly_parser = JsonOutputParser(pydantic_object=AnomalyResult)
detection_parser = JsonOutputParser(pydantic_object=DetectionResult)
final_parser = JsonOutputParser(pydantic_object=FinalOutput)

# Tambahan baru:
batch_and_expiry_parser = JsonOutputParser(pydantic_object=BatchAndExpiryResult)
quantity_parser = JsonOutputParser(pydantic_object=QuantityResult)
