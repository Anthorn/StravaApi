import requests
import datetime
from requests_oauthlib import OAuth2Session
import yaml
import logging
import time

class StravaApi:

    def __init__(self):
        self.baseUrl = 'https://www.strava.com/api/v3'
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

    def post(self, url, payload, files=None):
        return requests.post(url, headers=self.headers, data=payload, files=files)

    def get(self, url):
        return requests.get(url, headers=self.headers)


    def createActivity(self, name, type, startDate, elapsedTime, distance, description="", trainer=0, commute=0):
        url = self.baseUrl + '/activities'
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

        return self.post(url, payload)


    def getAthlete(self ):
        url = self.baseUrl + '/athlete'
        return self.get(url)

    def uploadActivity(self, file, name, description, activity_type, trainer=0, commute=0, data_type='gpx', externalId=0):
        url = self.baseUrl + "/uploads"
        payload = {'activity_type' : activity_type, 'data_type' : data_type}
        currentHeader = {"Authorization": "Bearer " + self.token['access_token']}

        with open(file, 'rb') as f:
            files = {'file' : f}
            result = self.oath.request('POST', url, headers=currentHeader, data=payload, files=files)

        return result.json()["id"]

    def getUploadStatus(self, id):
        url = self.baseUrl + "/uploads/" + str(id)
        response = self.get(url)
        return response



def main():
    api = StravaApi()
    filePath = "c:/Users/antonn/source/repos/StravaApiRepo/2014-03-18-174929.gpx"
    uploadResId = api.uploadActivity(filePath, "Test", "First test of uploading gpx file", "run", data_type='gpx')

    response = api.getUploadStatus(uploadResId).json()
    while(response['status'] != "Your activity is ready."):
        time.sleep(3)
        response = api.getUploadStatus(uploadResId).json()
        print(response)
        print('\n\r')

if __name__ == "__main__":
    main()


