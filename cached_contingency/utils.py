from numpy import nan, inf


def odds_ratio(c1r1: float, c2r1: float, c1r2: float, c2r2: float) -> float:
    """
    Calculate odds ratio of a contingency table
    """
    if any((
            c1r1 + c2r1 == 0, c1r2 + c2r2 == 0,  # row sums == 0
            c1r1 + c1r2 == 0, c2r1 + c2r2 == 0,  # col sums == 0
    )):
        return nan

    if not (c1r2 > 0 and c2r1 > 0):
        return inf

    return c1r1 * c2r2 / (c1r2 * c2r1)
