#!/usr/bin/env python
#coding=utf8

import xlrd
import pytz
import hashlib
import sys
from datetime import datetime, timedelta

try:
    import google_cal
except:
    pass

# lists of cell types, that we use to identify row types
_ROW_TYPE_DATE = [xlrd.XL_CELL_TEXT, xlrd.XL_CELL_DATE, None, None, None]
_ROW_TYPE_PRES = [None]*3 +  [xlrd.XL_CELL_DATE]*2  + [None]
_ROW_TYPE_EMPTY = [xlrd.XL_CELL_EMPTY]*5
_TIMEZONE = 'Europe/Zurich'


def match_row_type_pattern(a, b):
    """ helper function to match two rows (a and b). Mostly used to match a row
    against a predefined row type
    """
    return all(x==y or x is None or y is None for y,x in zip(a,b))

def get_datetime(xldate, mode, ref_date=None):
    """ helper function to convert a xldate to a datetime object with Zurich
    timezone. if the xldate only contains a time, the date of the resulting
    datetime object is set to 1.1.1900 
    """
    t = list(xlrd.xldate_as_tuple(xldate, mode))
    assert len(t) == 6, "failed to convert xldate to datetime object"
    # if it is only a time
    if sum(t[0:3]) == 0:
        if ref_date is None:
            t = [1900, 1, 1] + t[3:]
        else:
            t = [ref_date.year, ref_date.month, ref_date.day] + t[3:]
    return pytz.timezone(_TIMEZONE).localize(datetime(*t), is_dst=None)


class Presentation(dict):
    """ Container class to hold a presentation instance. Technically, this is a
    dictionary with some modifications It contains these fields: type, student,
    supervisors, start, end, title Upon creating the object, the type string is
    checked for the keywords 'final' or 'interm' and for 'ba', 'som', 'sa' and
    'ba'. if no combination from the two sets is found an exception is thrown.
    """

    def __init__(self, type, student, supervisors, start, end, title):

        # assign the fields and check their type
        keys = ('type', 'student', 'supervisors', 'start', 'end', 'title')
        args = (type, student, supervisors, start, end, title)
        types = [basestring]*3 + [datetime]*2 +[basestring]
        for k, v, t in zip(keys, args, types):
            if not isinstance(v, t):
                raise TypeError(
                        "The field '{}' is expected to be of type '{}',"
                        "but is '{}'".format(k, t, type(v)))
            self[k] = v

        # check if the type string contains the necessary keywords
        self.validate_type()

    def validate_type(self):
        """ Validates the type field. Makes sure that at least one keyword from
        each of the following sets is found in it: {'final', 'interm'}, {'ba',
        'som', 'sa', 'ma'}
        """
        t = self.type.lower()
        if not 'final' in t and not 'interm' in t:
            raise RuntimeError(
                    "unknown type '{}' (none of 'final', 'interm')".format(t))
        candiates = ('ba', 'som', 'sa', 'ma')
        if not any(candidate in t for candidate in candiates):
            raise RuntimeError(
                    "unknown type '{}"\
                    "(none of '{}')".format(t, "', '".join(candidates)))
    
    def isfinal(self):
        """ check if the presentation is a final presentation """
        return 'final' in self.type.lower()
        

    def __getattr__(self, attr):
        try:
            return super(Presentation, self).__getattr__(attr)
        except AttributeError:
            try:
                return self[attr]
            except KeyError:
                known_fields = ','.join(self.keys())
                raise KeyError("unknown field '{}'. Known fields are: " \
                        "{}".format(attr, known_fields))

    def get_uid(self):
        """ Creates a unique id based on the name of the student and the type
        of the project. Assuming that each student only does one of a type
        project, this should be farely unique. As it is independent of the
        start or end datetime, this allows for easy updates of schedule changes
        (assuming that Lucy doesn't misspell any names, or at least does it
        consistently)
        """
        n = self.student.strip().lower().encode('utf8')
        t = self.type.strip().lower().encode('utf8')
        s = hashlib.sha224(n + t)
        return s.hexdigest()

    def get_google_cal_dict(self):
        info = u'Type: {}\nStudent: {}\nSupervisors: {}\nTitle: {}\n'.format(
                self.type, self.student, self.supervisors, self.title)
        event = {
          u'summary': u'[Stud. pres.] {}: {}'.format(self.type, self.title),
          u'id' : self.get_uid(),
          #'location': '', # Should be obvious ;)
          u'description': info,
          u'start': {
            u'dateTime': self.start.isoformat(),
            u'timeZone': str(self.start.tzinfo),
          },
          u'end': {
            u'dateTime': self.end.isoformat(),
            u'timeZone': str(self.end.tzinfo),
          }
        }
        return event

    def __unicode__(self):
        return u"{} {} - {}: {} of {} ({}): {}".format(
                self.start.strftime("%d.%m.%Y"),
                self.start.strftime("%H:%M"),
                self.end.strftime("%H:%M"),
                self.type,
                self.student,
                self.supervisors,
                self.title)

    def __str__(self):        
        return unicode(self).encode('utf-8')


def get_presentations_from_sheet(sheet):
    """ Function to parse an excel sheet and extract presentations """

    # initialize variables
    date = None
    blocks = list()

    for row_id in range(sheet.nrows):
        
        # get the row and the types of the cells
        row = sheet.row(row_id)
        row_t = [i.ctype for i in row]

        if match_row_type_pattern(row_t, _ROW_TYPE_DATE):
            # if it is a header row we just need to extract the date and append
            # a new block
            date = get_datetime(row[1].value, sheet.book.datemode)
            blocks.append([])

        elif match_row_type_pattern(row_t, _ROW_TYPE_PRES):
            # if it is a presentation row, we extract the data and append a new
            # Presentation instance to the newest block
            # first make sure that we already processed a headeer row
            assert date is not None, "found no date before first entry"
            # prepare the arguments for the Presentation object
            getd = lambda x: get_datetime(x.value, sheet.book.datemode, date)
            args = [i.value.strip() for i in row[:3]]
            args.extend(map(getd, row[3:5]))
            args.append(row[5].value)
            # create the presentation object and append it
            blocks[-1].append(Presentation(*args))

        elif match_row_type_pattern(row_t, _ROW_TYPE_EMPTY):
            # if it is an empty line we dont care
            pass
        else:
            # if the line does not fit any of the row types, print a warning
            print u"unknown row (id={}): ".format(row_id) + \
                    u','.join([unicode(i.value) for i in row])
    return blocks



def main(fname, calendar=None):
    print "Will get presentations from: {}".format(fname)
    book = xlrd.open_workbook(fname)
    blocks = get_presentations_from_sheet(book.sheet_by_index(0))


    counter = 0
    uids = list()
    for block in blocks:
        print "-"*100
        for item in block:
            print item
            uid =  item.get_uid()
            assert uid not in uids
            uids.append(uids)
    
    if calendar is None:
        print "Cannot procdeed, no calendar was provided"
        return 

    inp = ''
    while not inp in 'yn' or inp == '':
        inp = raw_input("proceed and publish to calendar? [y/n]")
    if inp == 'n':
        return

    cal_interface = google_cal.GoogleCalendarInterface(calendar)

    # start a week before the first, just to be sure
    first = blocks[0][0].start - timedelta(days=7)

    events = cal_interface.get_events(first.isoformat())

    for block in blocks:
        for item in block:
            if item.isfinal():
                event = item.get_google_cal_dict()
                cal_interface.insert_or_update(event, events)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        cal = sys.argv[2]
        if cal.startswith('CAL'): # is a file with a calendar adress in it
            with open(cal, 'r') as f:
                cal = f.read().strip('\n')
        print cal
        main(sys.argv[1], cal)
    else:
        main(sys.argv[1])
