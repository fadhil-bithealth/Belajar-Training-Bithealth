# app/parser.py

from langchain_core.output_parsers import JsonOutputParser # type: ignore
from app.schema import AnomalyResult, DetectionResult, FinalOutput

anomaly_parser = JsonOutputParser(pydantic_object=AnomalyResult)
detection_parser = JsonOutputParser(pydantic_object=DetectionResult)
final_parser = JsonOutputParser(pydantic_object=FinalOutput)
