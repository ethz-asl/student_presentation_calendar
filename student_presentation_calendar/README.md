The purpose of this script is to extract events of student presentations from the excelsheets and automatically upload them to a google calendar.
So far it hasn't been tested extensively and was written fairly ad hoc...


#### Usage

```
python translator.py excelfile [calendar]
```

 - `excelfile` is a path to an excel file with student presentations
 - `calendar` is either a google calendar id or a file which contains such an id. This argument is optional (if it isn't provided only the excel file is parsed).
 
#### Requirements
 
The following python packages need to be installed:
- [pytz](http://pytz.sourceforge.net/)
- [xlrd](https://github.com/python-excel/xlrd)

  run `pip install -U pytz xlrd`

For the google syncing functionality: 
- [google-api-python-client](https://developers.google.com/api-client-library/python/start/installation) (run `pip install -U google-api-python-client`)
- A `client_secret` and `client_id` to use the google api. Follow [this guide](https://developers.google.com/google-apps/calendar/quickstart/python) on how to get one. 
  Place the `client_secret.json` file in the sutdent_presentation_calendar folder. You might also have to change the application name accordingly in `google_cal.py`

