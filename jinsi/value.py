import decimal
from typing import Union, List, Dict

import dezimal

Value = Union[None, str, bool, int, float, decimal.Decimal, dezimal.Dezimal, List['Value'], Dict[str, 'Value']]
