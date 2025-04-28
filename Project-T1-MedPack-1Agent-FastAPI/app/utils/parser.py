
from langchain_core.output_parsers import JsonOutputParser
from app.schemas.response_schema import AnomalyResult, DetectionResult, FinalOutput
from app.schemas.batch_expiry_schema import BatchExpiryResult
from app.schemas.quantity_schema import QuantityResult

anomaly_parser = JsonOutputParser(pydantic_object=AnomalyResult)
detection_parser = JsonOutputParser(pydantic_object=DetectionResult)
final_parser = JsonOutputParser(pydantic_object=FinalOutput)


batch_expiry_parser = JsonOutputParser(pydantic_object=BatchExpiryResult)
quantity_parser = JsonOutputParser(pydantic_object=QuantityResult)
