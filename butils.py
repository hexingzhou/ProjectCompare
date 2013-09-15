"""
A utils package for b company production
"""
def get_lastest_name_from_svn_log(log_string):
    name = None
    lines = log_string.split('\n')
    lines.reverse()
    for line in lines:
        if '|' in line:
            parts = line.split('|')
            name = parts[1].strip()

    return name