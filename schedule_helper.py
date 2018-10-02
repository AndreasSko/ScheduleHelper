"""
A backtracking algorithm to solve scheduling problems.

Copyright, 2018: Andreas Skorczyk <me@andreas-sk.de>
"""

from time import *
from random import shuffle

count = 0


def main():
    global count
    start_time = time()
    candidates = ["A.Picone", "P.Skorczyk", "R.Stöhr", "R.Ritschel", "G.Teixera", "F.Camuto", "M.Stöhr"]
    not_available = [[], ["M.Stöhr"], [], ["F.Camuto", "P.Skorczyk"], []]

    # Copy candidates list, so it can be changed
    new_candidates = candidates[:]

    # Find a solution. If there are not enough candidates and search fails, use more candidates
    while True:
        shuffle(new_candidates)
        print(new_candidates)

        solution = find_solution(new_candidates, not_available, [], 0, 0, time() + 5)

        # If a solution is found, we are done. If not: Increase candidate count
        if solution is not None:
            break

        print("No solution found yet. Increasing candidates..")
        print("Tried " + str(count))

        new_candidates = new_candidates[:] + candidates[:]

    # Print out solution
    print("Solution found in " + str(round(time() - start_time, 2)) + "s:")
    for i, week in enumerate(solution):
        response = "Week " + str(i + 1) + ": "
        for candidate in week:
            response += candidate + " "
        print(response)


def find_solution(candidates, not_available, solution, current_week, current_column, timeout):
    """
    A recursive function using the backtracking technique to find a possible solution of the scheduling-problem.

    :param candidates: the possible candidates (left) for scheduling as a list.
    :param not_available: unavailable candidates, one list of candidates per week.
    :param solution: the previous solution on which the algorithm search forward.
    :param current_week: the current week.
    :param current_column: the current column.
    :param timeout: the time on which the algorithm should cancel the operation (in seconds).
    :return:
    """
    global count

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

        count += 1

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


if __name__ == "__main__":
    main()