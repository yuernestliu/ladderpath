# Code for computing ladderpaths

It is the code to compute the shortest ladderpaths of a target block or target system, associated with the paper "**Ladderpath Approach: How Tinkering and Reuse Increase Complexity and Information**" by Yu Liu, Zengru Di and Philip Gerlee.


------------
The description of the algorithm is detailed in the paper.

You could just download *ComputeLadderpath.py* and run. To compute the shortest ladderpaths of a target block or target system, you just need to change the variable *blocks0* in the INPUT section (there are examples listed there too), e.g. set
* blocks0 = ['ABCDEFCFEDCBFDBA']
* blocks0 = ['ABDZBZ', 'ABDZ', 'ABDABD', 'CAB', 'Z']


------------
Note that
* The code currently can only deal with short strings. There are many techniques to speed it up and we are working on that. But here we just want to show the proof of concept.

* If the total number of letters in the target is smaller than 15, the current code can finish in a reasonablly short time for a normal personal computer or laptop (from minutes to ~1 hour).

* The computing time also depends on the structure of the target. The higher the resulted ladderpath (i.e. the larger the order-index), the more time it needs to compute.
