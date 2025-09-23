#!/usr/bin/env python3
"""
Uniform random k-SAT generator and local-search solvers (Hill-Climbing, Beam Search, VND)
Single-file experiment harness suitable for submission.

Usage examples:
  python3 ksat_solver_experiment.py --k 3 --n 50 --m 210 --trials 30 --algos hc,beam3,beam4,vnd --out results.csv

Dependencies: only Python standard library.

Output: CSV with per-trial results (score, penetrance, time) for each algorithm.
"""

import argparse
import csv
import random
import time
import math
from collections import defaultdict

# ------------------------ k-SAT generator ------------------------

def gen_random_k_sat(k, m, n, seed=None):
    """Generate m clauses of length k over n variables (1..n).
    Each clause is a tuple of signed integers (positive -> var, negative -> negated var).
    """
    if seed is not None:
        random.seed(seed)
    clauses = []
    for _ in range(m):
        vars_ = random.sample(range(1, n+1), k)
        clause = []
        for v in vars_:
            sign = random.choice([True, False])
            lit = v if sign else -v
            clause.append(lit)
        clauses.append(tuple(clause))
    return clauses

# ------------------------ evaluation helpers ------------------------

def eval_clause(clause, assignment):
    for lit in clause:
        var = abs(lit)
        val = assignment[var]
        if lit < 0:
            val = not val
        if val:
            return True
    return False


def score_assignment(clauses, assignment):
    satisfied = 0
    for c in clauses:
        if eval_clause(c, assignment):
            satisfied += 1
    return satisfied


def random_assignment(n):
    return {i: random.choice([False, True]) for i in range(1, n+1)}

# ------------------------ occurrence lists and incremental helpers ------------------------

def build_occurrences(clauses, n):
    occ = {i: [] for i in range(1, n+1)}
    for ci, clause in enumerate(clauses):
        for lit in clause:
            occ[abs(lit)].append(ci)
    return occ


def initial_clause_true_counts(clauses, assignment):
    counts = [0]*len(clauses)
    for i, c in enumerate(clauses):
        cnt = 0
        for lit in c:
            var = abs(lit)
            val = assignment[var]
            if lit < 0:
                val = not val
            if val:
                cnt += 1
        counts[i] = cnt
    return counts


def flip_effect_make_break(var, clauses, assignment, clause_counts, occ):
    make = 0
    brk = 0
    old_val = assignment[var]
    new_val = not old_val
    for ci in occ[var]:
        # determine contribution of var to clause before and after
        contributes_before = False
        contributes_after = False
        for lit in clauses[ci]:
            if abs(lit) == var:
                val_before = old_val if lit > 0 else (not old_val)
                val_after = new_val if lit > 0 else (not new_val)
                contributes_before = contributes_before or val_before
                contributes_after = contributes_after or val_after
        new_count = clause_counts[ci] - (1 if contributes_before else 0) + (1 if contributes_after else 0)
        was_sat = clause_counts[ci] > 0
        now_sat = new_count > 0
        if not was_sat and now_sat:
            make += 1
        if was_sat and not now_sat:
            brk += 1
    return make, brk

# ------------------------ Hill-Climbing ------------------------

def hill_climbing(clauses, n, max_iters=10000, restarts=20, seed=None, allow_sideways=False):
    if seed is not None:
        random.seed(seed)
    occ = build_occurrences(clauses, n)
    best_global = None
    best_score = -1
    stats = {'restarts': 0, 'flips': 0}
    start_time = time.time()
    for r in range(restarts):
        stats['restarts'] += 1
        assignment = random_assignment(n)
        clause_counts = initial_clause_true_counts(clauses, assignment)
        current_score = score_assignment(clauses, assignment)
        iters = 0
        while iters < max_iters:
            iters += 1
            stats['flips'] += 1
            best_var = None
            best_val = -10**9
            tie_vars = []
            for var in range(1, n+1):
                make, brk = flip_effect_make_break(var, clauses, assignment, clause_counts, occ)
                val = make - brk
                if val > best_val:
                    best_val = val
                    tie_vars = [var]
                elif val == best_val:
                    tie_vars.append(var)
            if not tie_vars:
                break
            # choose variable (tie break random)
            best_var = random.choice(tie_vars)
            # if best_val < 0, no improving flip
            if best_val < 0 or (best_val == 0 and not allow_sideways):
                break
            # apply flip
            assignment[best_var] = not assignment[best_var]
            # update clause_counts (recompute affected clauses for clarity)
            for ci in occ[best_var]:
                cnt = 0
                for lit in clauses[ci]:
                    varr = abs(lit)
                    val = assignment[varr]
                    if lit < 0:
                        val = not val
                    if val:
                        cnt += 1
                clause_counts[ci] = cnt
            current_score = score_assignment(clauses, assignment)
            if current_score > best_score:
                best_score = current_score
                best_global = dict(assignment)
            if best_score == len(clauses):
                break
    total_time = time.time() - start_time
    return best_global, best_score, {'time': total_time, 'flips': stats['flips']}

# ------------------------ Beam Search (complete-assignment beam over flips) ------------------------

def beam_search(clauses, n, beam_width=3, max_iters=1000, seed=None):
    if seed is not None:
        random.seed(seed)
    start_time = time.time()
    # initial beam: unique random assignments
    beam = []
    seen = set()
    while len(beam) < beam_width:
        a = random_assignment(n)
        key = tuple(sorted(a.items()))
        if key in seen:
            continue
        seen.add(key)
        s = score_assignment(clauses, a)
        beam.append((s, a))
    beam.sort(reverse=True, key=lambda x: x[0])
    iters = 0
    while iters < max_iters:
        iters += 1
        candidates = []
        cand_keys = set()
        for s, a in beam:
            for var in range(1, n+1):
                new_a = dict(a)
                new_a[var] = not new_a[var]
                key = tuple(sorted(new_a.items()))
                if key in cand_keys:
                    continue
                cand_keys.add(key)
                s_new = score_assignment(clauses, new_a)
                candidates.append((s_new, new_a))
        if not candidates:
            break
        candidates.sort(reverse=True, key=lambda x: x[0])
        new_beam = []
        new_keys = set()
        for s_new, new_a in candidates:
            key = tuple(sorted(new_a.items()))
            if key in new_keys:
                continue
            new_beam.append((s_new, new_a))
            new_keys.add(key)
            if len(new_beam) >= beam_width:
                break
        beam = new_beam
        # check solution
        for s, a in beam:
            if s == len(clauses):
                return a, s, {'time': time.time()-start_time, 'iters': iters}
    return beam[0][1], beam[0][0], {'time': time.time()-start_time, 'iters': iters}

# ------------------------ Variable-Neighborhood Descent (VND) ------------------------

def vnd(clauses, n, max_iters=5000, sample_pairs=200, sample_triples=500, seed=None):
    if seed is not None:
        random.seed(seed)
    start_time = time.time()
    assignment = random_assignment(n)
    clause_counts = initial_clause_true_counts(clauses, assignment)
    best_score = score_assignment(clauses, assignment)
    iters = 0
    improved_overall = True
    vars_list = list(range(1, n+1))
    while iters < max_iters and improved_overall:
        improved_overall = False
        # N1: best single flip
        best_var = None
        best_delta = 0
        for var in vars_list:
            make, brk = flip_effect_make_break(var, clauses, assignment, clause_counts, build_occurrences(clauses, n))
            delta = make - brk
            if delta > best_delta:
                best_delta = delta
                best_var = var
        if best_delta > 0:
            assignment[best_var] = not assignment[best_var]
            clause_counts = initial_clause_true_counts(clauses, assignment)
            best_score = score_assignment(clauses, assignment)
            improved_overall = True
            iters += 1
            continue
        # N2: sampled pair flips
        best_pair = None
        best_pair_delta = 0
        limit = min(sample_pairs, math.comb(n,2) if n>=2 else 0)
        tried = set()
        for _ in range(limit):
            a,b = random.sample(vars_list, 2)
            key = (min(a,b), max(a,b))
            if key in tried:
                continue
            tried.add(key)
            # simulate
            assignment[a] = not assignment[a]
            assignment[b] = not assignment[b]
            sc = score_assignment(clauses, assignment)
            # revert
            assignment[a] = not assignment[a]
            assignment[b] = not assignment[b]
            delta = sc - best_score
            if delta > best_pair_delta:
                best_pair_delta = delta
                best_pair = (a,b)
        if best_pair_delta > 0:
            a,b = best_pair
            assignment[a] = not assignment[a]
            assignment[b] = not assignment[b]
            clause_counts = initial_clause_true_counts(clauses, assignment)
            best_score = score_assignment(clauses, assignment)
            improved_overall = True
            iters += 1
            continue
        # N3: sampled triple flips
        best_triple = None
        best_triple_delta = 0
        limit3 = min(sample_triples, math.comb(n,3) if n>=3 else 0)
        tried3 = set()
        for _ in range(limit3):
            trio = tuple(sorted(random.sample(vars_list, 3)))
            if trio in tried3:
                continue
            tried3.add(trio)
            for v in trio:
                assignment[v] = not assignment[v]
            sc = score_assignment(clauses, assignment)
            for v in trio:
                assignment[v] = not assignment[v]
            delta = sc - best_score
            if delta > best_triple_delta:
                best_triple_delta = delta
                best_triple = trio
        if best_triple_delta > 0:
            for v in best_triple:
                assignment[v] = not assignment[v]
            clause_counts = initial_clause_true_counts(clauses, assignment)
            best_score = score_assignment(clauses, assignment)
            improved_overall = True
            iters += 1
            continue
        # no improvement
        break
    total_time = time.time() - start_time
    return assignment, best_score, {'time': total_time, 'iters': iters}

# ------------------------ Experiment harness and CLI ------------------------

def run_trial(clauses, n, algo, seed=None):
    if algo == 'hc':
        a, s, st = hill_climbing(clauses, n, restarts=10, max_iters=2000, seed=seed)
    elif algo == 'beam3':
        a, s, st = beam_search(clauses, n, beam_width=3, max_iters=1000, seed=seed)
    elif algo == 'beam4':
        a, s, st = beam_search(clauses, n, beam_width=4, max_iters=1000, seed=seed)
    elif algo == 'vnd':
        a, s, st = vnd(clauses, n, max_iters=2000, seed=seed)
    else:
        raise ValueError('Unknown algorithm')
    return s, st


def main():
    parser = argparse.ArgumentParser(description='Uniform random k-SAT experiments')
    parser.add_argument('--k', type=int, default=3)
    parser.add_argument('--n', type=int, required=True)
    parser.add_argument('--m', type=int, required=True)
    parser.add_argument('--trials', type=int, default=30)
    parser.add_argument('--algos', type=str, default='hc,beam3,beam4,vnd',
                        help='comma-separated: hc, beam3, beam4, vnd')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--out', type=str, default='ksat_results.csv')
    args = parser.parse_args()

    algos = [a.strip() for a in args.algos.split(',') if a.strip()]
    header = ['trial','n','m','algo','score','penetrance','time_seconds']

    with open(args.out, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for t in range(args.trials):
            seed = args.seed + t
            clauses = gen_random_k_sat(args.k, args.m, args.n, seed=seed)
            for algo in algos:
                s, st = run_trial(clauses, args.n, algo, seed=seed)
                penetrance = s / len(clauses)
                writer.writerow([t, args.n, args.m, algo, s, f'{penetrance:.6f}', f'{st["time"]:.6f}'])
                # flush occasionally
                csvfile.flush()
    print(f'Results saved to {args.out}')

if __name__ == '__main__':
    main()
