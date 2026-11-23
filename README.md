# Exact accumulator widths for OCP MX dot products

The OCP Microscaling (MX) spec defines the dot product of two blocks as the sum of 32 element products, scaled by the two block scales, and leaves the internal precision of that sum to the implementer (v1.1, section 6.1).

A question that comes up as soon as you try to build one: if nothing inside is allowed to round or overflow, how wide does the accumulator have to be?

| Element format | Largest value | Smallest step | Accumulator bits |
|---|---:|---:|---:|
| MXFP4 (E2M1) | 6 | 1/2 | **14** |
| MXFP6 (E2M3) | 7.5 | 1/8 | **18** |
| MXFP6 (E3M2) | 28 | 1/16 | **24** |
| MXFP8 (E4M3) | 448 | 1/512 | **42** |
| MXFP8 (E5M2) | 57344 | 1/65536 | **70** |
| MXINT8, -127 to 127 | 127/64 | 1/64 | **20** |
| MXINT8, if -128 is allowed | 2 | 1/64 | **21** |

Widths are for a signed two's-complement accumulator, block size 32, both operands in the same format.

## Where the numbers come from

Every finite value of an MX element is a whole multiple of the format's smallest subnormal step. Call the largest element C steps. A product is then a whole number of steps squared, at most C², and 32 of them add up to at most 32·C². Holding that with a sign takes

    1 + bit_length(32 · C²)

bits. For MXFP4, C = 12, so 32·144 = 4608, which is 13 bits of magnitude and one of sign.

The block scales do not enter. They are powers of two, their exponents add, and the result is applied once to the finished sum.

These widths are tight. Fill both blocks with the largest element and the sum is exactly 32·C², which fits in the width given and overflows an accumulator one bit narrower. `widths.py` checks both directions for every row.

## Run it

    python widths.py

Plain Python, standard library only. The script builds each format's value set from its bit encoding (exponent bits, mantissa bits, bias, which codes are Inf or NaN), so the table is derived and not typed in.

## What this does and doesn't tell you

It tells you the width at which the sum itself is exact. It says nothing about rounding the final sum to an output format, about accumulating across many blocks, or about what a narrower accumulator with truncation costs you in accuracy. Those are separate questions with their own answers.

The gap between the formats is the thing to notice. 14 bits for MXFP4 is nothing. 70 bits for E5M2 is a real adder, and it is the reason people are tempted to truncate there.

## Contact

Amir Al-Herani, aalhorini@gmail.com
