"""Exact accumulator widths for OCP MX dot products (block size 32).

For each MX element format this lists every finite value straight from the bit encoding,
then works out how many bits a two's-complement accumulator needs to hold the sum of 32
element products with no rounding and no overflow. Integers and fractions only, no floats.

    python widths.py
"""
from fractions import Fraction

K = 32   # MX block size


def float_values(exp_bits, man_bits, bias, top_code_special):
    """Finite non-negative values of a small float format with subnormals.

    top_code_special: mantissa codes in the highest exponent that are Inf or NaN
    and so are not numbers.
    """
    vals = set()
    for e in range(2 ** exp_bits):
        for m in range(2 ** man_bits):
            if e == 2 ** exp_bits - 1 and m in top_code_special:
                continue
            frac = Fraction(m, 2 ** man_bits)
            if e == 0:
                vals.add(frac * Fraction(2) ** (1 - bias))            # subnormal
            else:
                vals.add((1 + frac) * Fraction(2) ** (e - bias))      # normal
    return sorted(vals)


FORMATS = {
    # name: (element bits, finite non-negative values)
    "MXFP4  E2M1": (4, float_values(2, 1, 1, ())),
    "MXFP6  E2M3": (6, float_values(2, 3, 1, ())),
    "MXFP6  E3M2": (6, float_values(3, 2, 3, ())),
    "MXFP8  E4M3": (8, float_values(4, 3, 7, (7,))),            # S.1111.111 is NaN
    "MXFP8  E5M2": (8, float_values(5, 2, 15, (0, 1, 2, 3))),   # S.11111.xx is Inf or NaN
    "MXINT8 (-127..127)": (8, [Fraction(i, 64) for i in range(128)]),
    "MXINT8 (with -128)": (8, [Fraction(i, 64) for i in range(129)]),
}


def analyse(vals):
    step = min(v for v in vals if v > 0)          # every value is a whole multiple of this
    assert all((v / step).denominator == 1 for v in vals)
    c = int(max(vals) / step)                     # largest element, in steps
    total = K * c * c                             # largest |sum of 32 products|, in steps squared
    width = 1 + total.bit_length()                # magnitude bits plus a sign bit
    # the witness: 32 products that are all (largest element) x (largest element)
    assert total <= 2 ** (width - 1) - 1          # fits in `width` bits
    assert total > 2 ** (width - 2) - 1           # does not fit in `width - 1` bits
    return step, c, total, width


if __name__ == "__main__":
    print(f"{'format':20s} {'largest':>8s} {'step':>8s} {'C':>12s} {'32*C*C':>24s} {'bits':>5s}")
    for name, (_, vals) in FORMATS.items():
        step, c, total, width = analyse(vals)
        print(f"{name:20s} {str(max(vals)):>8s} {str(step):>8s} {c:12d} {total:24d} {width:5d}")
    print("\nWitness for every row: both operand blocks hold the largest element 32 times.")
    print("The sum is 32*C*C steps squared, which needs the width shown and overflows one bit less.")
    print("Flip the sign of one block to get the same magnitude negative.")
