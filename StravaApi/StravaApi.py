import requests
from requests_oauthlib import OAuth2Session
import yaml
import time
import os
import xmltodict
import sys
from PyQt5.QtCore import (Qt, pyqtSignal, QObject)

from athlete import *

class StravaApi(QObject):

    apiMessage = pyqtSignal(str)
    baseUrl = 'https://www.strava.com/api/v3'

    def __init__(self, startWithGui=False):
        QObject.__init__(self)
        self.clientId = 0
        self.clientSecret = ''
        self.directory = ''
        self.athlete = None
        if not startWithGui:
            _,_ = self.readDefaultCredentialsFromConfig()

    def readCredentialsFromGui(self, clientId, clientSecret):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.oauth = OAuth2Session(self.clientId, redirect_uri='https://localhost/test', scope='activity:read,activity:write')

    def readDefaultCredentialsFromConfig(self):
        yml = ''
        with open("conf.yaml", 'r') as stream:
            try:
                yml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                self.apiMessage.emit(exc)
        creds = yml['StravaApi']['credentials']
        self.clientId = creds['client_id']
        self.clientSecret = creds['client_secret']
        self.directory = yml['StravaApi']['activity_directory']

        return (self.clientId, self.clientSecret)

    def buildAuthUrl(self):
        params = {'approval_prompt':'force', 'response_type' : 'code'}
        url = 'https://www.strava.com/oauth/authorize'
        authUrl, _ = self.oauth.authorization_url(url, params)

        self.apiMessage.emit('Please go to %s and authorize access.' % authUrl)
        return authUrl

    def authorize(self, authResponse):
        try:
            tokenParams = { 'grant_type' : 'authorization_code'}
            oauthToken = self.oauth.fetch_token('https://www.strava.com/api/v3/oauth/token'
                                               , include_client_id=self.clientId
                                               , code=authResponse
                                               , client_secret=self.clientSecret
                                               , headers=tokenParams)
            self.token = oauthToken
            self.headers = {"Authorization": "Bearer " + self.token['access_token']}
        except ValueError as er:
            self.apiMessage.emit('ValueError' + er)


    def createActivity(self, name, type, startDate, elapsedTime, distance, description="", trainer=0, commute=0):
        url = self.baseUrl + '/activities'
        payload = {'name' : name \
                 , 'type' : type \
                 , 'start_date_local' : startDate \
                 , 'elapsed_time' : elapsedTime \
                 , 'description' : description \
                 , 'distance' : distance \
                 , 'trainer' : trainer \
                 , 'photo_ids' : '' \
                 , 'commute' : commute}

        return self.oauth.request('POST', url, payload)

    def getAthlete(self):
        url = self.baseUrl + '/athlete'

        return self.oauth.request('GET', url)

    def uploadActivity(self, file, name, description="", activity_type="run", trainer=0, commute=0, data_type='gpx', externalId=0):
        url = self.baseUrl + "/uploads"
        payload = {'activity_type' : activity_type, 'data_type' : data_type}
        currentHeader = {"Authorization": "Bearer " + self.token['access_token']}

        with open(file, 'rb') as f:
            files = {'file' : f}
            result = self.oauth.request('POST', url, headers=currentHeader, data=payload, files=files)

        return result.json()["id"]

    def getUploadStatus(self, id):
        url = self.baseUrl + "/uploads/" + str(id)
        response = self.oauth.request('GET', url)

        return response.json()

    def getAthleteStats(self, id):
        url = self.baseUrl + '/athletes/%s/stats' % str(id)
        payload = {'page' : '1', 'per_page' : '50'}
        currentHeader = {"Authorization": "Bearer " + self.token['access_token']}

        return self.oauth.request('GET', url, headers=currentHeader, data=payload)

    def listAthleteActivities(self, per_page=None):
        url = self.baseUrl + '/athlete/activities'
        payload = {'page' : '1', 'per_page' : per_page if per_page else '30'}
        current_header = {"Authorization": "Bearer " + self.token['access_token']}

        return self.oauth.request('GET', url, headers=current_header, data=payload)



    ## --- Mid level api functions, to be moved to a separate class in the future --- ##
    def waitForUploadComplete(self, id):
        response = self.getUploadStatus(id)
        counter = 0
        while (response['status'] != 'Your activity is ready.') and (counter < 10):
            time.sleep(1)
            response = self.getUploadStatus(id)
            self.apiMessage.emit(response['status'])
            self.apiMessage.emit('\n\r')
            counter += 1

    def uploadActivitiesFromDirectory(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith('.gpx'):
                currentAbsPath = directory + "/" + filename
                activityType = self.findActivityType(currentAbsPath)
                id = self.uploadActivity(currentAbsPath, filename, activity_type=activityType)
                self.waitForUploadComplete(id)


    def findActivityType(self, file):
        with open(file) as f:
            parsed = xmltodict.parse(f.read())
            activityString = parsed['gpx']['trk']['name']

        return self.translateRunkeeperActivityToStrava(activityString)


    def translateRunkeeperActivityToStrava(self, activityString):
        result = ""
        if 'Running' in activityString:
            result = "run"
        elif 'Walking' in activityString:
            result = "walk"

        return result

    def currentAthlete(self, forceUpdateAthlete=False):
        if(self.athlete is None or forceUpdateAthlete):
            athleteResponse = self.getAthlete()
            if athleteResponse.status_code == 200:
                self.athlete = Athlete(athleteResponse.json())

                return self.athlete
            else:
                return None
        else:
            return self.athlete

    def athleteSummary(self):
        athlete = self.currentAthlete()
        athleteStatsResponse = self.getAthleteStats(athlete.id)
        if athleteStatsResponse.status_code == 200:
            athlete.addAthleteSummary(athleteStatsResponse.json())

            self.apiMessage.emit("------- Athlete Summary --------")
            self.apiMessage.emit(athlete.runningSummaryStr())


    def checkUser(self):
        athleteResponse = self.getAthlete()
        if athleteResponse.status_code == 200:
            jsonResp = athleteResponse.json()
            userName = jsonResp['username']
            firstName = jsonResp['firstname']
            lastName = jsonResp['lastname']
            city = jsonResp['city']
            country = jsonResp['country']
            sex = 'Male' if jsonResp['sex'] is 'M' else 'Female'

            self.apiMessage.emit('Welcome to my StravaApi!')
            self.apiMessage.emit('Name: ' + firstName + " " + lastName)
            self.apiMessage.emit('Username: ' + userName)
            self.apiMessage.emit('Gender: ' + sex)
            self.apiMessage.emit("City: " + city)
            self.apiMessage.emit("Country: " + country)
            self.apiMessage.emit("Is this you? ")

            return True
        else:
            self.apiMessage.emit("Failed to fetch athlete.")

            return False

    def getLatestActivity(self):
        latestActivityResponse = self.listAthleteActivities('1')
        currentAthlete = self.currentAthlete()
        currentAthlete.addLatestActivity(latestActivityResponse.json())

        self.apiMessage.emit(currentAthlete.latestActivitySummaryStr())




