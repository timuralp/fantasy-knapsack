Fantasy football auction knapsack solver
========================================

Simple tool to keep track of the fantasy auction draft. It is initialized with
csv files containing projections for each individual position (the data can be
obtained from fftoday.com, for example).

Sample format of the cvs file for each position:

 * QB: Name, Team, Bye week, attempts, completions, yards, TDs, INTs, rushing attempts, rushing yards, rushing TDs, season fantasy points
 * RB: Name, Team, Bye week, rushing attempts, yards, TDs, receptions, yards, TDs, season points
 * WR: Name, Team, Bye week, receptions, yards, TDs, rushes, yards, TDs, season points
 * TE: Name, Team, Bye week, receptions, yards, TDs, season points

Of these fields only Name, Team, and season points are used. These uniquely
identify each player to allow figuring out which ones are on the team.

For each position, a points to cost is defined (I couldn't find a better way to
assign cost to each player).

From that, [0-1 knapsack
algorithm](https://en.wikipedia.org/wiki/Knapsack_problem#0.2F1_knapsack_problem)
is used to figure out the best team combination within a $200 budget. The
algorithm takes into account the team and prevents more than a set number of
players to be on a team (e.g. only one QB).

The algorithm does not attempt to ensure a certain number of players on a team
(for example, it may product out a team of 5).

How to use
==========

Create files `qbs.csv`, `rbs.csv`, `wrs.csv`, and `tes.csv`. Run the program
with `python ./fantasy_knapsack.py`. To get help, type in `help`.

You can remove players from the pool with `rm <player name>`. Add a player to
your team with `add <player name> <cost>`. The cost will be deducted from your
budget.

`budget` will show the current budget.

`team` will show the current team.

`best_team` will run the knapsack algorithm and print out the current best team.
