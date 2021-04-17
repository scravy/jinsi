from decimal import Decimal
from datetime import date
from typing import Union, List, Dict

Value = Union[None, str, bool, int, float, date, Decimal, List['Value'], Dict[str, 'Value']]
