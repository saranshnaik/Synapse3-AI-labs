import argparse
import random
import time
import csv
def calculate_statistics(results_file):
    with open(results_file, 'r') as f:
        reader = csv.DictReader(f)
        trials = list(reader)
        
    hc_scores = [float(row['HC_score']) for row in trials]
    bs3_scores = [float(row['BS3_score']) for row in trials]
    bs4_scores = [float(row['BS4_score']) for row in trials]
    vnd_scores = [float(row['VND_score']) for row in trials]
    
    hc_times = [float(row['HC_time']) for row in trials]
    bs3_times = [float(row['BS3_time']) for row in trials]
    bs4_times = [float(row['BS4_time']) for row in trials]
    vnd_times = [float(row['VND_time']) for row in trials]

    # Calculate average scores and times
    avg_hc_score = sum(hc_scores) / len(hc_scores)
    avg_bs3_score = sum(bs3_scores) / len(bs3_scores)
    avg_bs4_score = sum(bs4_scores) / len(bs4_scores)
    avg_vnd_score = sum(vnd_scores) / len(vnd_scores)
    
    avg_hc_time = sum(hc_times) / len(hc_times)
    avg_bs3_time = sum(bs3_times) / len(bs3_times)
    avg_bs4_time = sum(bs4_times) / len(bs4_times)
    avg_vnd_time = sum(vnd_times) / len(vnd_times)

    # Output summary
    print(f"Average Scores (Penetrance) per Algorithm:")
    print(f"Hill-Climbing: {avg_hc_score}")
    print(f"Beam Search (width 3): {avg_bs3_score}")
    print(f"Beam Search (width 4): {avg_bs4_score}")
    print(f"Variable Neighborhood Descent: {avg_vnd_score}")
    
    print("\nAverage Times (Seconds) per Algorithm:")
    print(f"Hill-Climbing: {avg_hc_time}")
    print(f"Beam Search (width 3): {avg_bs3_time}")
    print(f"Beam Search (width 4): {avg_bs4_time}")
    print(f"Variable Neighborhood Descent: {avg_vnd_time}")
# -------------------------------
# SAT Generator
# -------------------------------
def generate_k_sat(k, n, m):
    clauses = []
    for _ in range(m):
        vars_chosen = random.sample(range(1, n + 1), k)
        clause = []
        for v in vars_chosen:
            if random.choice([True, False]):
                clause.append((v, True))
            else:
                clause.append((v, False))
        clauses.append(clause)
    return clauses

def evaluate(clauses, assignment):
    """Return number of satisfied clauses."""
    satisfied = 0
    for clause in clauses:
        if any((assignment[v] if pos else not assignment[v]) for v, pos in clause):
            satisfied += 1
    return satisfied

# -------------------------------
# Heuristics
# -------------------------------
def heuristic1(clauses, assignment):
    return evaluate(clauses, assignment)  # clause satisfaction count

def heuristic2(clauses, assignment):
    # make-break heuristic (net gain of flipping best variable)
    current = evaluate(clauses, assignment)
    best_gain = -len(clauses)
    for v in assignment:
        assignment[v] = not assignment[v]
        gain = evaluate(clauses, assignment) - current
        assignment[v] = not assignment[v]
        if gain > best_gain:
            best_gain = gain
    return current + best_gain

# -------------------------------
# Algorithms
# -------------------------------
def hill_climbing(clauses, n, max_iters=1000, restarts=5):
    best_score = -1
    for _ in range(restarts):
        assignment = {i: random.choice([True, False]) for i in range(1, n + 1)}
        for _ in range(max_iters):
            current = evaluate(clauses, assignment)
            if current > best_score:
                best_score = current
            improved = False
            for v in assignment:
                assignment[v] = not assignment[v]
                new_score = evaluate(clauses, assignment)
                if new_score > current:
                    improved = True
                    break
                else:
                    assignment[v] = not assignment[v]
            if not improved:
                break
    return best_score

def beam_search(clauses, n, beam_width=3, max_iters=100):
    beam = [{i: random.choice([True, False]) for i in range(1, n + 1)} for _ in range(beam_width)]
    best_score = -1
    for _ in range(max_iters):
        new_beam = []
        scored = []
        for assign in beam:
            current_score = evaluate(clauses, assign)
            scored.append((current_score, assign))
            if current_score > best_score:
                best_score = current_score
            for v in assign:
                neighbor = assign.copy()
                neighbor[v] = not neighbor[v]
                scored.append((evaluate(clauses, neighbor), neighbor))
        scored.sort(reverse=True, key=lambda x: x[0])
        beam = [s[1] for s in scored[:beam_width]]
    return best_score

def variable_neighborhood_descent(clauses, n, max_iters=300):
    assignment = {i: random.choice([True, False]) for i in range(1, n + 1)}
    best_score = evaluate(clauses, assignment)

    for _ in range(max_iters):
        improved = False
        # Neighborhood 1: single variable flip
        for v in assignment:
            assignment[v] = not assignment[v]
            new_score = evaluate(clauses, assignment)
            if new_score > best_score:
                best_score = new_score
                improved = True
                break
            assignment[v] = not assignment[v]
        if improved:
            continue

        # Neighborhood 2: pair flips
        for v1 in assignment:
            for v2 in assignment:
                if v1 >= v2:
                    continue
                assignment[v1] = not assignment[v1]
                assignment[v2] = not assignment[v2]
                new_score = evaluate(clauses, assignment)
                if new_score > best_score:
                    best_score = new_score
                    improved = True
                    break
                assignment[v1] = not assignment[v1]
                assignment[v2] = not assignment[v2]
            if improved:
                break
        if improved:
            continue

        # Neighborhood 3: triple flips (random sample)
        vars_list = list(assignment.keys())
        for _ in range(10):  # sample 10 triples
            v1, v2, v3 = random.sample(vars_list, 3)
            for v in (v1, v2, v3):
                assignment[v] = not assignment[v]
            new_score = evaluate(clauses, assignment)
            if new_score > best_score:
                best_score = new_score
                improved = True
                break
            for v in (v1, v2, v3):
                assignment[v] = not assignment[v]
        if not improved:
            break
    return best_score

# -------------------------------
# Experiment Runner
# -------------------------------
def run_experiment(n, m, trials, out_file):
    k = 3
    results = []
    for t in range(trials):
        clauses = generate_k_sat(k, n, m)

        start = time.time()
        hc_score = hill_climbing(clauses, n)
        hc_time = time.time() - start

        start = time.time()
        bs3_score = beam_search(clauses, n, beam_width=3)
        bs3_time = time.time() - start

        start = time.time()
        bs4_score = beam_search(clauses, n, beam_width=4)
        bs4_time = time.time() - start

        start = time.time()
        vnd_score = variable_neighborhood_descent(clauses, n)
        vnd_time = time.time() - start

        results.append({
            "trial": t + 1,
            "HC_score": hc_score, "HC_time": hc_time,
            "BS3_score": bs3_score, "BS3_time": bs3_time,
            "BS4_score": bs4_score, "BS4_time": bs4_time,
            "VND_score": vnd_score, "VND_time": vnd_time
        })

    with open(out_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3-SAT Solver Comparison")
    parser.add_argument("--n", type=int, required=True, help="Number of variables")
    parser.add_argument("--m", type=int, required=True, help="Number of clauses")
    parser.add_argument("--trials", type=int, default=5, help="Number of trials")
    parser.add_argument("--out", type=str, default="results.csv", help="Output CSV filename")
    args = parser.parse_args()

    run_experiment(args.n, args.m, args.trials, args.out)
    results_file = "results.csv"  # Path to the results CSV file
    calculate_statistics(results_file)