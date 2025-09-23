#!/usr/bin/env python3
import argparse
import random
import sys

def generate_k_sat(k: int, n: int, m: int) -> list[list[int]]:
    """Generate a random k-SAT instance with n variables and m clauses.
    Each clause is a list of k distinct integer literals. A variable v
    appears as +v for positive or -v for negated.
    """
    if k > n:
        raise ValueError("k (clause length) cannot be greater than n (number of variables).")

    clauses: list[list[int]] = []
    for _ in range(m):
        # choose k distinct variables (1..n)
        vars_chosen = random.sample(range(1, n + 1), k)
        clause: list[int] = []
        for v in vars_chosen:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return clauses

def format_clauses(clauses: list[list[int]]) -> str:
    """Format clause list as '[a,b,-c] [d,-e,f]' etc."""
    return " ".join("[" + ",".join(str(l) for l in clause) + "]" for clause in clauses)

def main():
    parser = argparse.ArgumentParser(description="Uniform Random k-SAT Generator")
    parser.add_argument("--k", type=int, required=True, help="Clause size (k)")
    parser.add_argument("--n", type=int, required=True, help="Number of variables")
    parser.add_argument("--m", type=int, required=True, help="Number of clauses")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducibility")
    args = parser.parse_args()

    if args.k <= 0 or args.n <= 0 or args.m < 0:
        print("k and n must be positive integers; m must be non-negative.", file=sys.stderr)
        sys.exit(1)

    if args.seed is not None:
        random.seed(args.seed)

    try:
        clauses = generate_k_sat(args.k, args.n, args.m)
    except ValueError as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

    print("\nGenerated k-SAT Formula:")
    print(format_clauses(clauses))

if __name__ == "__main__":
    main()
