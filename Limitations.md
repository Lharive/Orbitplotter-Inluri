# Some Limitations Of The Program

1. It still treats eccentricity and period as independent in the sampling process, only placing limits via rejection sampling; rather than using a joint probability distribution.

2. The mass range for the first planet is significantly narrower (and the narrowed range is generally fairly arbitrarily chosen)

3. The _Holman and Wiegert (1999)_ formula is an empirical one; this program treats it as a generally applicable model

4. Two of the reference papers; _Dietrich, Malhotra, & Apai (2024)_ and _Silburt, Gaidos, & Wu (2015)_ focus on single-star systems, and have been extrapolated into this binary system generator under the assumption that they transfer their findings reasonably well

5. The program is very inefficient for the generation of large batches of samples

6. The bounds used to truncate the various distributions during sampling are treated as fixed and abrupt rather than the gradual tapering it is in practice
