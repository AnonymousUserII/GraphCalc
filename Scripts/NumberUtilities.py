from math import fabs
from sigfig import round


def mantissa(num: float) -> float:
    """
    Returns the mantissa of a decimal float
    """
    if not str(num).replace('.', "").rstrip('0'):  # If num is 0
        return 0
    return fabs(float(str(num).replace('.', "").rstrip('0')))


def d_round(num: float, dec_places: int = 0) -> str:
    """
    Dynamically rounds specifically for the numbers that are displayed on the bounds and graph
    """
    a_num: float = fabs(num)
    if a_num < 1E-6:
        return '0'
    if a_num >= 1E4:
        return str(round(num, sigfigs=min(5, len(str(mantissa(num))) - 2), notation="scientific"))
    if a_num >= 2:
        return str(round(num, sigfigs=min(5, len(str(mantissa(num))) - 2), notation="standard"))
    if a_num > 1E-1:
        return str(round(num, decimals=min(5, dec_places), notation="standard"))
    return str(round(num, decimals=min(5, dec_places), notation="scientific"))
