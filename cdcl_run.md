# Input formula
```F = { ωi | i = 1 .. 13 }```
*where*
ω1 = (**x1**, **x2**)
ω2 = (**x1**, **¬x2**, x4)
ω3 = (**¬x4**, **x3**, x5, ¬x6)
ω4 = (**¬x4**, **x3**, x5, x6)
ω5 = (**x3**, **¬x5**, x7)
ω6 = (**x3**, **¬x5**, ¬x7)
ω7 = (**¬x3**, **¬x4**, x8)
ω8 = (**¬x3**, **¬x4**, ¬x8)
ω9 = (**¬x1**, **¬x2**)
ω10 = (**¬x1**, **x2**, ¬x3)
ω11 = (**x2**, **x3**, ¬x4)
ω12 = (**¬x1**, **x4**, x8)
ω13 = (**¬x1**, **x4**, ¬x8)


The watched literals in each clause are in bold.
*Decision heuristic*: make the decision 'xi is true' where i is the least index of the variable that has not been assigned yet.


 ## CDCL run

 - **x1 @ 1**
   + (¬x2, ω9)
