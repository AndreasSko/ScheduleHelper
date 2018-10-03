"""
A backtracking algorithm to solve scheduling problems.

Copyright, 2018: Andreas Skorczyk <me@andreas-sk.de>
"""

from time import *
from random import shuffle


def main():
    global count
    start_time = time()
    candidates = ["A.Picone", "P.Skorczyk", "R.Stöhr", "R.Ritschel", "G.Teixera", "F.Camuto", "M.Stöhr"]
    candidates_cost = {'F.Camuto': 3, 'R.Ritschel': 2}
    not_available = []
    possible_solutions = []

    # Copy candidates list, so it can be changed
    new_candidates = candidates[:]

    # Find a solution. If there are not enough candidates and search fails, use more candidates
    while time() < start_time + 14000:
        while True:
            shuffle(new_candidates)

            solution = find_solution(new_candidates, not_available, [], 0, 0, time() + 600)

            # If a solution is found, we are done. If not: Increase candidate count
            if solution is not None:
                break

            print("No solution found yet. Increasing candidates..")

            new_candidates = new_candidates[:] + candidates[:]

        possible_solutions.append((solution, evaluate_solution(candidates, candidates_cost, solution)))

        # Print out possible solution
        print("One possible solution (of " + str(len(possible_solutions)) + ") found:")
        print_solution(solution)
        print("The cost of the solution: " + str(possible_solutions[-1][1]) + "\n")

    # Sort solution by cost
    possible_solutions = sorted(possible_solutions, key=lambda x: x[1])

    print("Finished! These are the cheapest solutions (of " + str(len(possible_solutions)) + "):")
    for i in range(0, 5):
        solution, cost = possible_solutions[i]
        print("Nr. " + str(i + 1) + " with cost of " + str(cost))
        print_solution(solution)
        print("-" * 10)


def find_solution(candidates, not_available, solution, current_week, current_column, timeout):
    """
    A recursive function using the backtracking technique to find a possible solution of the scheduling-problem.

    :param candidates: the possible candidates (left) for scheduling as a list.
    :param not_available: unavailable candidates, one list of candidates per week.
    :param solution: the previous solution on which the algorithm search forward.
    :param current_week: the current week.
    :param current_column: the current column.
    :param timeout: the time on which the algorithm should cancel the operation (in seconds).
    :return: solution
    """

    # Check, if solution is even possible with the amount of candidates
    if len(candidates) < len(not_available):
        return None

    # Check if there is still time left
    if timeout - time() < 0:
        return None

    # Initialize
    weeks_count = len(not_available)

    # If solution was found, return solution
    if current_week >= weeks_count and solution[current_week - 1][current_column] is not None:
        return solution

    # Try candidates, if no one available: backtrack
    for index, candidate in enumerate(candidates):
        # Ignore unavailable candidates
        if candidate in not_available[current_week]:
            continue

        # Copy candidate-list and remove current candidate from it
        new_candidates = candidates[:]
        del new_candidates[index]

        if current_column == 0:
            temp = solution[:]
            temp.append([candidate, None])
            new_solution = find_solution(new_candidates, not_available, temp, current_week, current_column + 1, timeout)
        else:
            # Ensure candidate is not in same column multiple times
            # TODO: Enable more than just 2 columns
            if candidate == solution[current_week][current_column - 1]:
                continue

            temp = solution[:]
            temp[current_week][current_column] = candidate
            new_solution = find_solution(new_candidates, not_available, temp, current_week + 1, 0, timeout)

        if new_solution is not None:
            return new_solution

    return None


def evaluate_solution(candidates, candidates_cost, solution):
    """
    Inspects the given solution for optimality and returns its calculated cost.
    :param candidates: the list of candidates
    :param candidates_cost: a dictionary of additional cost per candidate
    :param solution: the solution to evaluate
    :return: the cost of the given solution
    """
    cost = 0
    cand_appear = dict()

    # Create helper data structure: Dictionary for with every candidate and its appearances in the weeks
    for candidate in candidates:
        cand_appear[candidate] = []

    # For every appearance in schedule note it in cand_appear
    for week, entry in enumerate(solution):
        for candidate in entry:
            cand_appear[candidate].append(week)

    for candidate, appearance in cand_appear.items():
        # Count the appearance of the same candidate multiple times within the schedule
        if len(appearance) > 1:
            cost += 2 ** len(appearance)

            # Calculate distance between appearances (the smaller, the worse)
            for i, a1 in enumerate(appearance):
                for j, a2 in enumerate(appearance):
                    if not i == j or not i > j:
                        distance = a2 - a1
                        if distance == 1:
                            cost += 50

            # Add extra cost per person
            if candidate in candidates_cost:
                cost += candidates_cost[candidate] * len(appearance)

    return cost


def print_solution(solution):
    for i, week in enumerate(solution):
        response = "Week " + str(i + 1) + ": "
        for candidate in week:
            response += candidate + " "
        print(response)


if __name__ == "__main__":
    main()