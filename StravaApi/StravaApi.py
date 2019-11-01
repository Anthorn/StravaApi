import requests
import datetime
from requests_oauthlib import OAuth2Session
import yaml

class StravaApi:

    def __init__(self):
        self.baseUrl = 'https://www.strava.com/api/v3/'
        self.clientId = 0
        self.clientSecret = ''
        self.readConfig()
        self.oath = OAuth2Session(self.clientId, redirect_uri='https://localhost/test', scope='activity:read,activity:write')
        self.token = self.authorize(self.oath)
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

    def post(self, url, payload):
        return requests.post(url, headers=self.headers, data=payload)

    def get(self, url):
        return requests.get(url, headers=self.headers)


    def createActivity(self, name, type, startDate, elapsedTime, distance, description="", trainer=0, commute=0):
        payload = {
                   'name' : name
                 , 'type' : type
                 , 'start_date_local' : startDate
                 , 'elapsed_time' : elapsedTime
                 , 'description' : description
                 , 'distance' : distance
                 , 'trainer' : trainer
                 , 'photo_ids' : ''
                 , 'commute' : commute}

        url = baseUrl + 'activities'

        return post(url, payload)


    def getAthlete(self ):
        return get(self.baseUrl + 'athlete')


def main():
    api = StravaApi()
    currentTime = datetime.datetime.now().isoformat()
    result = api.createActivity("Script Test", "Run", currentTime, 150, 5000, "Testing out the Strava API")


if __name__ == "__main__":
    main()


