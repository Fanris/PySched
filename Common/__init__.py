import datetime

def str2Datetime(s):
    '''
    @summary: Converts a string to a datetime object.
    The String format has to be "YYYY-MM-DD HH:MM:SS"
    @param s: the String to convert
    @result:
    '''
    if not s:
        return
    parts = s.split('.')
    dt = datetime.datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
    return dt

def datetime2Str(datetime):
    '''
    @summary: Converts a datetime to a string and strips the milliseconds
    @param datetime: the datetime to convert
    @result:
    '''
    if not datetime:
        return

    result = str(datetime).split(".")[0]
    return result
