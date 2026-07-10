# Defines the shape a valid sensor reading has to match before it's
# allowed anywhere near the warehouse.

from datetime import datetime
from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    container_id: str = Field(..., description="Unique container identifier, e.g. CTR-001")
    timestamp: datetime = Field(..., description="UTC timestamp of the reading")
    temperature: float = Field(..., description="Internal container temperature in Celsius")
    humidity: float = Field(..., description="Relative humidity inside the container, in percent")
    co2_level: float = Field(..., description="CO2 concentration inside the container, in ppm")