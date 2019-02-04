# ScheduleHelper
For the task of scheduling people for something like a shift-plan, I tried some techniques I learned in my AI-Lecture. This is my first proof-of-concept version, which already works ok:
For a given list of "candidates" it tries to find a schedule (using backtracking search) with the best "cost" (Things like: How often was a "candidate" scheduled? For a candidate who is scheduled multiple times: How much time is in between each schedule? Does the "candidate" have additional costs, so it shouldn't be scheduled too often?). For a given timeout, the script tries to find as many possible solutions as possible, determines each cost and, after the timeout, returns the best solution found.

For an online version you can try my angular fronted I built additionally: https://storage.googleapis.com/andreas-sk-de/ScheduleHelper/index.html
