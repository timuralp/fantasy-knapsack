import re

class Player(object):
    FIELDS = None
    WEIGHT = None

    def __init__(self, entry):
        if not self.FIELDS:
            raise RuntimeError('fields not defined')
        fields = entry.rsplit(None, self.FIELDS)
        self.name = fields[0]
        self.team = fields[1]
        if self.name.endswith('Upside') or self.name.endswith('Risk'):
            parts = [part for part in self.name.split()
                     if part != 'Upside' and part != 'Risk']
            self.name = ' '.join(parts)
        self.points = float(fields[-1])
        self.cost = float(self.points) / self.WEIGHT

class WR(Player):
    FIELDS = 9
    WEIGHT = 3.7
    LIMIT = 3

class RB(Player):
    FIELDS = 9
    WEIGHT = 4.38
    LIMIT = 3

class TE(Player):
    FIELDS = 6
    WEIGHT = 4
    LIMIT = 1

class QB(Player):
    FIELDS = 11
    WEIGHT = 11.9
    LIMIT = 1

class FantasyKnapsack(object):
    def __init__(self, data_files, budget=200):
        self.all_players = []
        self.budget = 200
        players = {}
        for k, v in data_files.items():
            players[k] = self.load_players(*v)
    
        for v in players.values():
            self.all_players += v
        self.all_players.sort(cmp=lambda x, y: cmp(x.cost, y.cost))
        self.team = []

    @staticmethod
    def load_players(csv, position):
        with open(csv) as f:
            lines = f.readlines()
            return [position(entry) for entry in lines]
    
    @staticmethod
    def position_count(team, player):
        return sum(map(lambda p: 1 if type(player) == type(p) else 0, team))

    def _find_player(self, name):
        matches = filter(lambda player: re.findall(name, player.name,
            re.IGNORECASE), self.all_players)
        if not matches:
            return False
        if len(matches) > 1:
            return matches
        return matches[0]

    def add_player(self, name, cost, player=None):
        if not player:
            player = self._find_player(name)
            if not isinstance(player, Player):
                return player
        try:
            self.all_players.remove(player)
            player.cost = cost
            self.team.append(player)
            self.budget -= cost
            return True
        except ValueError:
            return False

    def remove_player(self, name, player=None):
        if not player:
            player = self._find_player(name)
            if not isinstance(player, Player):
                return player
        try:
            self.all_players.remove(player)
            return True
        except ValueError:
            return False

    def get_best_team(self):
        sol_table = []
        initial_points = sum(map(lambda player: player.points, self.team))
        for i in range(0, len(self.all_players)):
            sol_table.append([(initial_points, self.team)]*(self.budget+1))

        for i in range(0, len(self.all_players)):
            for current_budget in range(1, self.budget + 1):
                player = self.all_players[i]
                without_points, without_team = sol_table[i-1][current_budget]
                if player.cost > current_budget:
                    sol_table[i][current_budget] = (without_points, without_team)
                    continue

                with_points, with_team = sol_table[i-1][
                    int(current_budget - player.cost)]

                # check team constraints
                count = self.position_count(with_team, player)
                if count >= player.LIMIT:
                    sol_table[i][current_budget] = (without_points, without_team)
                    continue

                with_points += player.points
                if with_points > without_points:
                    new_team = list(with_team)
                    new_team.append(player)
                    sol_table[i][current_budget] = (with_points, new_team)
                else:
                    sol_table[i][current_budget] = (without_points, without_team)
        
        points, team = sol_table[len(self.all_players)-1][self.budget]
        print '> Season points:', points
        cost = 0
        print '> Team (Name, position, cost, season points):'
        for player in team:
            cost += player.cost
            print '> ', player.name, type(player).__name__, player.cost,\
                player.points
        print '> Budget: ', cost

def prompt_choice(players):
    print '> Multiple players found:'
    for index, player in enumerate(players):
        print '>  %d %s %s %s' % (index, player.name,
            type(player).__name__, player.team)
    while True:
        player = raw_input('Which one?\n')
        try:
            return players[int(player)]
        except ValueError:
            continue

def main():
    files = {
        'rb': ('./rbs.csv', RB),
        'wr': ('./wrs.csv', WR),
        'qbs': ('./qbs.csv', QB),
        'tes': ('./tes.csv', TE)
    }

    solver = FantasyKnapsack(files)

    while True:
        action = raw_input('What to do? ("help" for help)\n')
        if action == 'quit':
            break
        if action == 'best_team':
            solver.get_best_team()
        elif action == 'team':
            print '> Current team:'
            for player in solver.team:
                print '> %s %s %f %f' % (
                    player.name, type(player).__name__, player.cost, player.points)
        elif action.startswith('rm'):
            name = action.split(None, 1)[1].strip()
            ret = solver.remove_player(name)
            if not ret:
                print '> Player %s not found' % name
            elif type(ret) == list:
                player = prompt_choice(ret)
                ret = solver.remove_player(player.name, player=player)
                if not ret:
                    print '> Could not remove %s' % player.name
                else:
                    print '> Player %s removed' % player.name
            else:
                print '> Player %s removed' % name
        elif action.startswith('add'):
            name_cost = action.split(None, 1)[1].strip()
            name, cost = name_cost.rsplit(None, 1)
            try:
                cost = int(cost)
            except ValueError:
                print '> cost must be an integer'
                continue
            ret = solver.add_player(name, cost)
            if not ret:
                print '> Player %s not found' % player
            elif type(ret) == list:
                player = prompt_choice(ret)
                ret = solver.add_player(name, cost, player=player)
                if not ret:
                    print '> Could not add player %s' % player.name
                else:
                    print '> Player %s added' % player.name
            else:
                print '> Player %s added' % name
        elif action == 'budget':
            print solver.budget
        else:
            print '> add <player> <cost>'
            print '> rm <player>'
            print '> team'
            print '> best_team'
            print '> budget'
            print '> quit'

if __name__ == '__main__':
    main()
