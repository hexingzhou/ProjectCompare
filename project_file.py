"""
To analyze file size in a project.
It may create report for the result.
"""
import butils
import csv
import optparse
import os
import project_config
import re
import stat
import svn
import sys
import xml.etree.ElementTree as et


__KByte_Div = 1024
__MByte_Div = 1024 * __KByte_Div
__GByte_Div = 1024 * __MByte_Div


# create option parser
def _create_option_parser():
    usage = 'usage: %prog [options] project_path'
    version = '%prog 1.0'
    parser = optparse.OptionParser(usage=usage, version=version)

    parser.add_option('-c', '--config', 
        dest='config_file', metavar='FILE', default='project_file_config.xml', help='config xml file')
    parser.add_option('-r', '--result', 
        dest='result_file', metavar='FILE', default='project_file_analysis_result.csv', 
        help='analysis result file')

    return parser


# check path with count regex
# [param] project_dict: a project dict get from config xml
#                      file contains count regex used
#                      for path string check
# [return] True if match anly one of count regex,
#          False if not
def check_path_with_count(path, project_dict):
    result = False
    if 'task_array' in project_dict:
        task_array = project_dict['task_array']
        for task_dict in task_array:
            if 'id' in task_dict and 'list_array' in task_dict:
                if task_dict['id'] == 'file':
                    list_array = task_dict['list_array']
                    for list_dict in list_array:
                        if _check_path_with_count_dict(path, list_dict):
                            result = True
                            break
    return result


# check path with count regex
# [param] list_dict: a list dict get from config xml
#                    file contains count regex used
#                    for path string check
# [return] True if match anly one of count regex,
#          False if not
def _check_path_with_count_dict(path, list_dict):
    result = False
    if 'id' in list_dict and 'string_array' in list_dict:
        if list_dict['id'] == 'count_regex':
            string_array = list_dict['string_array']
            for pattern in string_array:
                if re.match(pattern, path) is not None:
                    result = True
                    break
    return result


# check path with match regex
# [param] project_dict: a project dict get from config xml
#                      file contains match regex used
#                      for path string check
# [return] result, conditions
#          result: True if match anly one of match regex,
#                  False if not
#          conditions: an array contains all conditions matched
def check_path_with_match(path, project_dict):
    result = False
    conditions = []
    if 'task_array' in project_dict:
        task_array = project_dict['task_array']
        for task_dict in task_array:
            if 'id' in task_dict and 'list_array' in task_dict:
                if task_dict['id'] == 'file':
                    list_array = task_dict['list_array']
                    for list_dict in list_array:
                        res, condition = _check_path_with_match_dict(path, list_dict)
                        if res:
                            conditions.append(condition)
                            result = True
    return result, conditions


# check path with match regex
# [param] list_dict: a list dict get from config xml
#                      file contains match regex used
#                      for path string check
# [return] result, condition
#          result: True if match anly one of match regex, 
#                  False if not
#          condition: a dict contains conditions
def _check_path_with_match_dict(path, list_dict):
    result = False
    condition = None
    if 'id' in list_dict and 'string_array' in list_dict:
        if list_dict['id'] == 'match_regex':
            condition = _get_condition_with_match_dict(list_dict)
            if _check_path_with_condition(path, condition):
                string_array = list_dict['string_array']
                for pattern in string_array:
                    if re.match(pattern, path) is not None:
                        result = True
                        break
    return result, condition


def _get_condition_with_match_dict(list_dict):
    condition = {}
    if 'size_large_than' in list_dict:
        condition['size_large_than'] = list_dict['size_large_than']
    return condition


# check path satisfy all conditions
# [param] condition: a dict contains all conditions
# [return] True if path satisfy all conditions,
#          False if not
def _check_path_with_condition(path, condition):
    result = True
    if 'size_large_than' in condition:
        if os.stat(path)[stat.ST_SIZE] <= int(condition['size_large_than']):
            result = False
    return result


# check path with filter regex
# [param] project_dict: a project dict get from config xml
#                      file contains filter regex used
#                      for path string check
# [return] True if match anly one of filter regex,
#          False if not
def check_path_with_filter(path, project_dict):
    result = False
    if 'task_array' in project_dict:
        task_array = project_dict['task_array']
        for task_dict in task_array:
            if 'id' in task_dict and 'list_array' in task_dict:
                if task_dict['id'] == 'file':
                    list_array = task_dict['list_array']
                    for list_dict in list_array:
                        if _check_path_with_filter_dict(path, list_dict):
                            result = True
                            break
    return result


# check path with filter regex
# [param] list_dict: a list dict get from config xml
#                    file contains filter regex used
#                    for path string check
# [return] True if match anly one of filter regex,
#          False if not
def _check_path_with_filter_dict(path, list_dict):
    result = False
    if 'id' in list_dict and 'string_array' in list_dict:
        if list_dict['id'] == 'filter_regex':
            string_array = list_dict['string_array']
            for pattern in string_array:
                if re.match(pattern, path) is not None:
                    result = True
                    break
    return result


# calculate file size in a path
# and set it in res_array
# [param] path: file path for analysis
def calc_file_size(path, sort_reverse=True):
    result_array = []
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            apath = os.path.join(dirpath, name)
            obj = {
                'path': apath,
                'size': os.stat(apath)[stat.ST_SIZE]
            }
            result_array.append(obj)

    result_array = sorted(result_array, key=lambda x:x['size'], reverse=sort_reverse)
    return result_array


# check options and args
def _check_options_and_args(options, args):
    if len(args) == 0:
        print 'no project_path'
        sys.exit()


if __name__ == '__main__':
    parser = _create_option_parser()
    (options, args) = parser.parse_args()
    _check_options_and_args(options, args)

    project_dict = project_config.parse_config_file(options.config_file)

    print 'calculate file size...'
    array_dict = calc_file_size(args[0])

    print 'check file author...'
    svn.set_svn_tool('svn')
    result_array = {}
    for d in array_dict:
        if check_path_with_filter(d['path'], project_dict):
            continue
        result, conditions = check_path_with_match(d['path'], project_dict)
        if result:
            for condition in conditions:
                if 'size_large_than' in condition:
                    log_string = svn.svn_log(d['path'], 1)
                    log_name = butils.get_lastest_name_from_svn_log(log_string)
                    if log_name in result_array:
                        pass
                    else:
                        result_array[log_name] = []
                    result_array[log_name].append((d['size'], d['path'], condition['size_large_than']))
                    break

    print 'write result to file...'
    with open(options.result_file, 'w') as rfile:
        rfile.writelines('Here are some files too large:\n')
        for name in result_array:
            rfile.writelines('\n')
            rfile.writelines('Author: ' + name + '\n')
            for m in result_array[name]:
                rfile.writelines('|-> ' + m[1] + ' ' + str(m[0] / __KByte_Div) + 'K\n')