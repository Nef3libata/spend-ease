from dataclasses import dataclass
from datetime import date
from uuid import uuid4


@dataclass
class Transaction:
    id: str
    amount: float
    category: str
    date: date
    description: str


@dataclass
class Budget:
    category: str
    limit: float
    period: str
