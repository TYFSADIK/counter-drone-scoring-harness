"""SAPIENT-style detection report (BSI Flex 335 v2 concepts), as a plain dataclass.

The real interface is protobuf over TCP. Generate bindings from the official
.proto files into harness/sapient_pb2.py and convert with to_proto()/from_proto().
Keeping an internal dataclass means the scorer never depends on the wire format.
"""
from dataclasses import asdict, dataclass, field
import json
import uuid


@dataclass
class DetectionReport:
    node_id: str
    t: float                      # UTC seconds
    lat: float
    lon: float
    alt_m: float | None = None
    object_id: str = field(default_factory=lambda: str(uuid.uuid4()))   # node's track id
    classification: str = "unknown"   # e.g. "UAV/multirotor"
    confidence: float = 0.5
    sensor: str = "rf"                # rf | radar | eo | ir | acoustic

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, s: str) -> "DetectionReport":
        return cls(**json.loads(s))
