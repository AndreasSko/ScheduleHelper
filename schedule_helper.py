"""
A backtracking algorithm to solve scheduling problems.

Copyright, 2018: Andreas Skorczyk <me@andreas-sk.de>
"""

from time import *
from random import shuffle
import sys


class ScheduleHelper:
    """

    """
    candidates: list
    candidates_cost: dict
    not_available: list
    per_solution_timeout: int
    global_timeout: int

    _search_order: list

    solutions: list

    def __init__(self, candidates: list, candidates_cost: dict, not_available: list, per_solution_timeout: int,
                 global_timeout: int):
        """

        :param candidates: list of all possible candidats.
        :param candidates_cost: additional costs for some candidats as dictionary.
        :param not_available: unavailable candidates, one list of candidates per week.
        :param per_solution_timeout: the maximum time to search for one solution, after timeout try different
               possible solution
        :param global_timeout: the maximum time to search for solutions, after that the best five are returned
        """
        self.candidates = candidates
        self.candidates_cost = candidates_cost
        self.not_available = not_available
        self.per_solution_timeout = per_solution_timeout
        self.global_timeout = global_timeout

        # Create helper-structures
        self._search_order = self.determine_search_order()

        self.solutions = list()

    def start_calculation(self) -> None:
        """
        Using the given values the function tries to find as many solutions as possible using the backtracking-algorithm.
        :return: None
        """
        start_time = time()

        # Copy candidates list, so it can be changed
        new_candidates = self.candidates[:]

        # Find a solution. If there are not enough candidates and search fails, use more candidates
        while time() < start_time + self.global_timeout:
            while True:
                shuffle(new_candidates)

                solution = self.find_solution(new_candidates, [[]] * len(self.not_available),
                                              self.determine_next_week(None), 0,
                                              int(time()) + self.per_solution_timeout)

                # If a solution is found, we are done. If not: Increase candidate count
                if solution is not None:
                    break

                new_candidates = new_candidates[:] + self.candidates[:]

            self.solutions.append((solution, self.evaluate_solution(solution)))

        # Sort solution by cost
        self.solutions = sorted(self.solutions, key=lambda x: x[1])

        print("Finished! These are the cheapest solutions (of " + str(len(self.solutions)) + "):")
        for i in range(0, 5):
            if not i >= len(self.solutions):
                solution, cost = self.solutions[i]
                print("Nr. " + str(i + 1) + " with cost of " + str(cost))
                self.print_solution(solution)
                print("-" * 10)

    def find_solution(self, candidates: list, solution: list, current_week: int,
                      current_column: int, timeout: int) -> list or None:
        """
        A recursive function using the backtracking technique to find a possible solution of the scheduling-problem.

        :param candidates: the possible candidates (left) for scheduling as a list.
        :param solution: the previous solution on which the algorithm search forward.
        :param current_week: the current week.
        :param current_column: the current column.
        :param timeout: the time on which the algorithm should cancel the operation (in seconds).
        :return: solution
        """

        # Check, if solution is even possible with the amount of candidates
        if len(candidates) < len(self.not_available):
            return None

        # Check if there is still time left
        if timeout - time() < 0:
            return None

        # If solution was found, return solution
        if current_week == -1 \
                and solution[self.determine_prev_week(current_week)][current_column] is not None:
            return solution

        # Try candidates, if no one available: backtrack
        for index, candidate in enumerate(candidates):
            # Ignore unavailable candidates
            if candidate in self.not_available[current_week]:
                continue

            # Copy candidate-list and remove current candidate from it
            new_candidates = candidates[:]
            del new_candidates[index]

            if current_column == 0:
                temp = solution[:]
                temp[current_week] = ([candidate, None])
                new_solution = self.find_solution(new_candidates, temp, current_week, current_column + 1, timeout)
            else:
                # Ensure candidate is not in same column multiple times
                # TODO: Enable more than just 2 columns
                if candidate == solution[current_week][current_column - 1]:
                    continue

                temp = solution[:]
                temp[current_week][current_column] = candidate
                new_solution = self.find_solution(new_candidates, temp,
                                                  self.determine_next_week(current_week), 0, timeout)

            if new_solution is not None:
                return new_solution

        return None

    def evaluate_solution(self, solution: list) -> int:
        """
        Inspects the given solution for optimality and returns its calculated cost.
        :param solution: the solution to evaluate
        :return: the cost of the given solution
        """
        cost = 0
        cand_appear = dict()

        # Create helper data structure: Dictionary for with every candidate and its appearances in the weeks
        for candidate in self.candidates:
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
            if candidate in self.candidates_cost:
                cost += candidates_cost[candidate] * len(appearance)

        return cost

    def determine_search_order(self) -> list:
        """
        Determines the optimal search order after the heuristic of "most constrained first" to detect possible
        failures early on.
        :return: the optimal search order as a list of weeks
        """

        # For every week count the number of unavailable persons
        not_available_count = list()
        for i, unavailable in enumerate(self.not_available):
            not_available_count.append((i, len(unavailable)))

        not_available_count = sorted(not_available_count, key=lambda x: x[1], reverse=True)

        result = []

        for week in not_available_count:
            result.append(week[0])

        return result

    def determine_next_week(self, current_week: int or None) -> int:
        """
        Determines the next week to find a solution for using the optimal search-order.
        :param current_week: the current week
        :return: next week
        """
        # Return first week in search_order
        if current_week is None:
            return self._search_order[0]

        # If current_week == last week to search for, return -1 to signal this
        if self._search_order.index(current_week) == (len(not_available) - 1):
            return -1

        return self._search_order[self._search_order.index(current_week) + 1]

    def determine_prev_week(self, current_week: int or None) -> int:
        """
        Determines the previous week using the optimal search-order.
        :param current_week: the current week
        :return: previous week
        """
        # Return first week in search_order
        if current_week is None:
            return self._search_order[0]

        # Return last week in search_order
        if current_week == -1:
            return self._search_order[-1]

        # If current_week already first week in search_order, return -1 to signal this
        if self._search_order[self._search_order.index(current_week) - 1] == self._search_order[-1]:
            return -1

        return self._search_order[self._search_order.index(current_week) - 1]

    def print_solution(self, solution: list) -> None:
        """
        For a given solution, print out a per week summary.
        :param solution: the solution
        :return: None
        """
        for i, week in enumerate(solution):
            response = "Week " + str(i + 1) + ": "
            for candidate in week:
                response += candidate + " "
            print(response)


# For debug-purposes
if len(sys.argv) >= 2:
    if sys.argv[1] == 'debug':
        print("DEBUG")
        candidates = ["A", "B", "C", "D", "E", "F", "G"]
        not_available = [[], ["G"], [], ["F", "B"], []]

        s_helper = ScheduleHelper(candidates, {}, not_available, 10, 30)

        s_helper.start_calculation()

    exit()

# Command-line usage
if __name__ == "__main__":
    candidates_string = input("Please name the candidates for scheduling (as a comma separated list without spaces): ")
    candidates = list()
    for candidate in candidates_string.split(','):
        candidates.append(candidate)

    candidates_cost_string = input("Are there candidates with additional costs? Please name them like A:Cost,B:Cost ")
    candidates_cost = dict()
    for tpl in candidates_cost_string.split(','):
        candidate, cost = tpl.split(':')
        candidates_cost[candidate] = int(cost)

    weeks = int(input("How many weeks should be scheduled? "))

    not_available = list()
    for i in range(0, weeks):
        na_string = input("For week " + str(i+1) + " name the candidates that are not available: ")

        not_available.append(list())
        for na in na_string.split(','):
            not_available[i].append(na)

    print("\n Now some more technical questions. As a starter it's recommended to just use the default values.")
    per_solution_timeout = int(input("For how long should the program search for a specific solution until it " +
                                     "times out? (Default: 30s) ") or 30)

    global_timeout = int(input("For how long should the program try out different solutions until it shows you the " +
                               "the best found? (Default: 60s) ") or 60)

    print("Alright, we can start now. This may take a while (at least " + str(global_timeout) + "s), so please be" +
          "patient.")

    s_helper = ScheduleHelper(candidates, candidates_cost, not_available, per_solution_timeout, global_timeout)

    s_helper.start_calculation()