import requests
from requests_oauthlib import OAuth2Session
import yaml
import time
import os
import xmltodict

class StravaApi:

    def __init__(self):
        self.baseUrl = 'https://www.strava.com/api/v3'
        self.clientId = 0
        self.clientSecret = ''
        self.directory = ''
        self.readConfig()
        self.oauth = OAuth2Session(self.clientId, redirect_uri='https://localhost/test', scope='activity:read,activity:write')
        self.token = self.authorize(self.oauth)
        self.headers = {"Authorization": "Bearer " + self.token['access_token']}


    def readConfig(self):
        yml = ''
        with open("conf.yaml", 'r') as stream:
            try:
                yml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        creds = yml['StravaApi']['credentials']
        self.clientId = creds['client_id']
        self.clientSecret = creds['client_secret']
        self.directory = yml['StravaApi']['activity_directory']


    def authorize(self, oauth):

        #Request Access
        params = {'approval_prompt':'force', 'response_type' : 'code'}
        url = 'https://www.strava.com/oauth/authorize'
        authUrl, state = oauth.authorization_url(url, params)

        print ('Please go to %s and authorize access.' % authUrl)
        authorization_response = input('Enter the full code key: ')

        #Exchange Token
        tokenParams = { 'grant_type' : 'authorization_code'}
        oauthToken = oauth.fetch_token('https://www.strava.com/api/v3/oauth/token'
                                           , include_client_id=self.clientId
                                           , code=authorization_response
                                           , client_secret=self.clientSecret
                                           , headers=tokenParams)
        return oauthToken


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


    def getAthlete(self ):
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

    def waitForUploadComplete(self, id):
        response = self.getUploadStatus(id)
        counter = 0;
        while (response['status'] != 'Your activity is ready.') and (counter < 10):
            time.sleep(1)
            response = self.getUploadStatus(id)
            print(response)
            print('\n\r')
            counter += 1

    def uploadActivitiesFromDirectory(self):
        for filename in os.listdir(self.directory):
            if filename.endswith('.gpx'):
                currentAbsPath = self.directory + "/" + filename
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


def checkUser(api):
    athleteResponse = api.getAthlete()
    if athleteResponse.status_code == 200:
        jsonResp = athleteResponse.json()
        userName = jsonResp['username']
        firstName = jsonResp['firstname']
        lastName = jsonResp['lastname']
        city = jsonResp['city']
        country = jsonResp['country']
        sex = 'Male' if jsonResp['sex'] is 'M' else 'Female'

        print('Welcome to my StravaApi!')
        print('Name: ' + firstName + " " + lastName)
        print('Username: ' + userName)
        print('Gender: ' + sex)
        print("City: " + city)
        print("Country: " + country)
        print("Is this you? ")
        yes = input("Yes/No: ").lower()

        return True if yes == 'yes' or yes == 'y' else False
    else:
        print("Failed to fetch athlete.")
        return False



def main():
    api = StravaApi()
    if(checkUser(api)):
        api.uploadActivitiesFromDirectory()
    else:
        print("User not ok.")



if __name__ == "__main__":
    main()


