# Indexed Combinatorial Spaces: the 400-Student Hostel Demonstrator

A zero-dependency HTML/JavaScript demonstration of **direct indexing (unranking)** over a very large combinatorial space, and of the point where constraints make that indexing hard.

Author: **Marko Valant**, independent researcher, Bled, Slovenia. Code and text were developed with the help of AI assistants (GPT-5, Gemini, DeepSeek-R1, Claude).

---

## What the demonstrator shows

**Problem.** 400 students (200 boys, 200 girls) are placed into 100 rooms of four. Boys and girls never share a room. Boy rooms and girl rooms may interleave in any order across `Ro-1 … Ro-100`.

**Method.** Every admissible arrangement gets a unique integer index. Entering an index decodes it directly into one arrangement, without enumerating any other arrangement. This is *unranking* in a mixed-radix number system, a standard technique in combinatorics (see Knuth, *TAOCP* Vol. 4A).

The index is split into independent "digits":

| digit | meaning | number of values |
|---|---|---|
| interleave | which 50 of the 100 rooms are boy rooms | C(100, 50) ≈ 1.0·10²⁹ |
| boys | how the 200 boys fill the 50 boy rooms | see below |
| girls | how the 200 girls fill the 50 girl rooms | see below |

Decoding uses JavaScript `BigInt`, so indices with 560–641 digits are handled exactly. A decode takes a few milliseconds, and an independent checker confirms gender separation, room size and that every student appears exactly once.

## Two index spaces

| file | space | size | one index means |
|---|---|---|---|
| `hostel_matrix.html` (v12) | students → pairs → two pairs per room, rooms in canonical order | ≈ 3.33·10⁵⁵⁹ (560 digits) | one *pairing structure* |
| `hostel_pnp_v13.html` | each numbered room gets a 4-subset of the remaining students | ≈ 10⁶⁴⁰ (641 digits) | one *distinct* assignment of students to numbered rooms |

The two spaces are not the same set:

- in v12 one room occupancy is reached by 3 different pairings of its four students (3¹⁰⁰ ≈ 10⁴⁸ repetitions in total);
- in v12 the 50!·50! ≈ 10¹²⁹ orders of rooms within each gender are not reached.

A small check (8 students, 2 rooms) gives 315 v12 indices, 35 distinct occupancies, and 70 occupancies with numbered rooms. v13 is an exact bijection: every assignment of students to numbered rooms has exactly one index.

## What this does and does not show about P vs NP

**What it shows.** Without extra rules, every index is a valid solution by construction. Navigating a space of 10⁶⁴⁰ arrangements, jumping to any of them and verifying it all take polynomial time. This is a clear, hands-on illustration of ranking and unranking.

**What it does not show.** It does not solve an NP-hard problem. When every index is already a solution, there is no search problem: the hard part of P vs NP is *finding* a solution that satisfies constraints, not *listing* solutions of an unconstrained space.

**Where it becomes hard (v13).** v13 adds the rule "these students must not share a room":

- **Filtering pairs is easy.** Forbidden pairs can be removed from the pair triangle: `n(n−1)/2 − k` allowed pairs remain.
- **Counting is hard.** Exact unranking needs the number of complete arrangements in every branch. Without rules all branches are equal, so the index is split by division. With rules the branches differ, and computing them means counting:
  - **pairs only:** perfect matchings that use only allowed pairs. Deciding that one exists is polynomial (Edmonds' blossom algorithm). Counting them is #P-complete in general (Valiant, 1979).
  - **rooms of four:** deciding whether *one* conflict-free arrangement exists is already NP-complete in general (partition into groups of a fixed size ≥ 3; Garey & Johnson).

A "valid-only" index (1, 2, 3, … over valid arrangements) therefore exists mathematically, but building it requires exactly these counts.

## v13 features

1. **Exact unique-occupancy decoder** with visible counter digits: one digit per room, radix `C(200 − 4t, 4)`.
2. **Conflict rules**, typed by hand or generated randomly.
3. **Valid fraction by sampling.** In test runs: 10 conflicts → about 86 % of indices valid; 100 → about 26 %; 1 000 → none in a sample of 300.
4. **Naive scan** (index+1, +2, …). It fails: the least significant digits change only the interleave and the last rooms, so a conflict in an early room survives for blocks of about 10⁶⁰⁰ consecutive indices.
5. **Block skip.** Finds the exact next valid index by jumping over whole blocks that share the first conflicting room. This is backtracking search expressed with indices. In single runs: 100 conflicts → 2 checks; 1 000 conflicts → about 47 000 checks and a jump of about 10⁶⁰⁰ indices. With dense conflicts the search tree explodes.
6. **Small exact lab.** Exact counts of valid pairings and valid rooms for 8–24 students by dynamic programming over subsets. Time and memory grow about 2ⁿ; for 200 students this would be about 10⁶⁰ states.
7. The v12 structured space is kept as a second tab for comparison.

## Run

Download the HTML file and open it in a browser. No installation, server or network is needed.

## Research context and open direction

This demonstrator is part of the author's long-term independent work on how representation (indexing, geometry, multidimensional encodings) affects the practical cost of large combinatorial problems. That broader view is a **working hypothesis**; it is not established by this code.

A concrete, testable next step:

> Identify **classes of constraints** for which the number of valid arrangements in every branch can be computed in polynomial time. Examples are conflicts that form a forest, have bounded degree, or have bounded treewidth. For such classes, a valid-only index with polynomial-time jumps is possible. For general constraint sets, no such method is known, and finding one would imply a major result in complexity theory.


## References

- D. E. Knuth, *The Art of Computer Programming*, Vol. 4A: combinatorial generation, ranking and unranking.
- J. Edmonds, "Paths, trees, and flowers", *Canad. J. Math.* 17 (1965).
- L. G. Valiant, "The complexity of computing the permanent", *Theor. Comput. Sci.* 8 (1979).
- M. R. Garey, D. S. Johnson, *Computers and Intractability* (1979).
- S. Cook, "The P versus NP problem", Clay Mathematics Institute problem description.

## License

MIT License (see `LICENSE`).

## Contact

infokrog.bled@gmail.com · Bled, Slovenia
