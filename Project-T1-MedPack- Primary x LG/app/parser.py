# app/parser.py

from langchain_core.output_parsers import JsonOutputParser # type: ignore
from app.schema import AnomalyResult, DetectionResult, FinalOutput
from langchain_core.output_parsers import JsonOutputParser # type: ignore
from app.schema import BatchNumberResult,QuantityDetectionResult    # tambahkan model baru di schema

anomaly_parser = JsonOutputParser(pydantic_object=AnomalyResult)
detection_parser = JsonOutputParser(pydantic_object=DetectionResult)
final_parser = JsonOutputParser(pydantic_object=FinalOutput)
batch_number_parser = JsonOutputParser(pydantic_object=BatchNumberResult)
quantity_parser = JsonOutputParser(pydantic_object=QuantityDetectionResult)