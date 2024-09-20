from typing import NamedTuple, Union

class Atomo(NamedTuple):
    type: int
    lexeme: str
    value: Union [int, float]
    operator: int               # LE, NE, LT, GE, GT, EQ
    line: int
 