"""A quickstart example showing usage of the Google Calendar API."""
from datetime import datetime, timedelta
import os

from apiclient.discovery import build
from httplib2 import Http
import oauth2client
from oauth2client import client
from oauth2client import tools
import googleapiclient.errors

#try:
#    import argparse
#    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#except ImportError:
#    flags = None

#TODO: figure out how to use argparse in cascaded modules
flags = None

#SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'test'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'test.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials


class GoogleCalendarInterface(object):
    """ a simple interface class, which provides a bunch of convenient
    functions
    """

    def __init__(self, calendar):
        """ We get the credentials and initialize the service to access the
        calendar """
        self.calendar = calendar
        self.credentials = get_credentials()
        self.service = build(
                'calendar', 'v3', 
                http=self.credentials.authorize(Http()))

    def get_events(self, tstart='now', maxResults=250):
        """Get a list of 'maxResults' events starting from the date 'tstart'"""
        if tstart == 'now':
            tstart = datetime.utcnow().isoformat() + 'Z' # 'Z' = UTC time
        eventsResult = self.service.events().list(
                calendarId=self.calendar, timeMin=tstart,
                maxResults=maxResults, singleEvents=True,
                orderBy='startTime').execute()
        return eventsResult.get('items', [])

    def insert_event(self, event):
        """ insert an event into the calendar (will fail if the calendar
        already has an item with the same id)
        """
        return self.service.events().insert(
                calendarId=self.calendar, body=event).execute()

    def update_event(self, event):
        """ update an event. The event must have an id field (obviously) """
        assert 'id' in event, "Event must have an id field"
        return self.service.events().update(
                calendarId=self.calendar, eventId=event['id'],
                body=event).execute()

    def insert_or_update(self, event, events=[]):
        """ Insert or update an event. If available a list of events from the
        calendar can be provided. If inserting fails, update is called """
        if any(event['id'] == e['id'] for e in events):
            print "updating event", event.get('summary', '')
            self.update_event(event)
        else:
            print "inserting event", event.get('summary', '')
            try:
                self.insert_event(event)
            except googleapiclient.errors.HttpError:
                self.update_event(event)



def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    service = build('calendar', 'v3', http=credentials.authorize(Http()))

    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print 'Getting the upcoming 10 events'
    eventsResult = service.events().list(
        calendarId='primary',
        #timeMin=now, 
        maxResults=2500,
        singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print 'No upcoming events found.'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print start, unicode(event['summary']), event['start']


if __name__ == '__main__':
    main()
