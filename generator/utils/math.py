def round_to_nearest_odd(number: float | int) -> int:
    high_odd = (number // 2) * 2 + 1
    low_odd = high_odd - 2
    return (
        int(high_odd)
        if abs(number - high_odd) < abs(number - low_odd)
        else int(low_odd)
    )
