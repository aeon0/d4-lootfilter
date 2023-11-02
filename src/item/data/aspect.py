from dataclasses import dataclass


@dataclass
class Aspect:
    type: str
    value: float = None
    text: str = ""
