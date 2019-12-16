


class Athlete:
    def __init__(self, athleteInfoRaw):
        self.id = athleteInfoRaw['id']
        self.name = athleteInfoRaw['firstname'] + ' ' + athleteInfoRaw['lastname']
        self.username = athleteInfoRaw['username']
        self.gender = 'Male' if athleteInfoRaw['sex'] is 'M' else 'Female'
        self.city = athleteInfoRaw['city']
        self.country = athleteInfoRaw['country']


    def addAthleteSummary(self, athleteSummaryRaw):
        allRunTotals = athleteSummaryRaw['all_run_totals'];
        self.count = allRunTotals['count']
        self.distance = allRunTotals['distance']
        self.movingTime = allRunTotals['moving_time']
        self.elapsedTime = allRunTotals['elapsed_time']
        self.elevationGain = allRunTotals['elevation_gain']


