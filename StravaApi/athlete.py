
import datetime as datetime

class Athlete:
    def __init__(self, athleteInfoRaw):
        self.id = athleteInfoRaw['id']
        self.name = athleteInfoRaw['firstname'] + ' ' + athleteInfoRaw['lastname']
        self.username = athleteInfoRaw['username']
        self.gender = 'Male' if athleteInfoRaw['sex'] is 'M' else 'Female'
        self.city = athleteInfoRaw['city']
        self.country = athleteInfoRaw['country']
        self.count = ''
        self.distance = ''
        self.movingTime = ''
        self.elapsedTime = ''
        self.elevationGain = ''

        self.latest_activity = {}


    def addAthleteSummary(self, athleteSummaryRaw):
        allRunTotals = athleteSummaryRaw['all_run_totals']
        self.count = allRunTotals['count']
        self.distance = allRunTotals['distance']
        self.movingTime = allRunTotals['moving_time']
        self.elapsedTime = allRunTotals['elapsed_time']
        self.elevationGain = allRunTotals['elevation_gain']

    def runningSummaryStr(self):
        return "----- Running ------\n" + \
               "Number of activities: " + str(self.count)  + "\n" + \
               "Total Distance: " + str((self.distance/1000)) + " km \n" + \
               "Total moving time(hh:mm:ss): " + str(datetime.timedelta(seconds=self.movingTime)) + " \n" + \
               "Total elapsed time(hh:mm:ss): " + str(datetime.timedelta(seconds=self.elapsedTime)) + " \n" + \
               "Total Elevation gain: " + str((self.elevationGain)) + " m"

    def addLatestActivity(self, latestActivityRaw):
        self.latest_activity = latestActivityRaw[0]


    def latestActivitySummaryStr(self):
        return "----- Latest Activity ------ \n" + \
               "Name: " + str(self.latest_activity['name']) + "\n" + \
               "Distance: " + str(self.latest_activity['distance']/1000) + " km\n" +\
               "Elapsed time: " + str(datetime.timedelta(seconds=self.latest_activity['elapsed_time'])) + "\n" +\
               "Type: " + str(self.latest_activity['type']) + "\n" +\
               "Start date: " + str(self.latest_activity['start_date']) + "\n" +\
               "Kudos: " + str(self.latest_activity['kudos_count']) + "\n"



