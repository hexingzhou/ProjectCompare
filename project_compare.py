"""
A tool to compare two project in source and compare path.
It also calculate the size of files in two paths, and find
files with biggest different in size.
"""
import csv
import filecmp
import optparse
import os
import project_config
import re
import stat
import sys


def _create_option_parser():
    """
    create option parser
    """
    usage = 'usage: %prog [options]'
    version = '%prog 1.0'
    parser = optparse.OptionParser(usage=usage, version=version)

    parser.add_option('-c', '--config', 
        dest='config_file', metavar='FILE', 
        default='project_compare_config.xml', help='config xml file')
    parser.add_option('--source', 
        dest='source', help='source project path')
    parser.add_option('--compare', 
        dest='compare', help='compare project path')
    parser.add_option('--number', 
        dest='number', type='int', default=10, help='number of results')
    parser.add_option('-r', '--result', 
        dest='result_file', metavar='FILE', 
        default='project_compare_result.csv', help='result csv format file')

    return parser


def _check_options_and_args(options, args):
    """
    check options and args
    """
    if options.source is None:
        print 'source path is empty!'
        sys.exit()
    if options.compare is None:
        print 'compare path is empty!'
        sys.exit()


def analyze_dir_diff(src_path, com_path, project_dict):
    """
    analyze file path size change information
    test how big the change is from src_path to com_path
    """
    dcmp = filecmp.dircmp(src_path, com_path)

    src_only_array = []
    com_only_array = []
    common_array = []

    append_size_to_array(
        dcmp.left_only, src_path, src_only_array, project_dict)
    append_size_to_array(
        dcmp.right_only, com_path, com_only_array, project_dict)

    for name in dcmp.common_files:
        tsrc_path = src_path + os.sep + name
        tcom_path = com_path + os.sep + name
        if check_path_with_filter(tsrc_path, project_dict):
            continue
        if check_path_with_filter(tcom_path, project_dict):
            continue
        src_size = os.stat(tsrc_path)[stat.ST_SIZE]
        com_size = os.stat(tcom_path)[stat.ST_SIZE]
        diff_size = src_size - com_size
        obj = {
            'src_path': tsrc_path,
            'com_path': tcom_path,
            'src_size': src_size,
            'com_size': com_size,
            'diff_size': diff_size
        }

        common_array.append(obj)

    for name in dcmp.common_dirs:
        if check_path_with_filter(src_path + os.sep + name, project_dict):
            continue
        if check_path_with_filter(com_path + os.sep + name, project_dict):
            continue
        sub_src_only_array, sub_com_only_array, sub_common_array = analyze_dir_diff(
            src_path + os.sep + name, com_path + os.sep + name, project_dict)
        append_list_from_list(sub_src_only_array, src_only_array)
        append_list_from_list(sub_com_only_array, com_only_array)
        append_list_from_list(sub_common_array, common_array)

    return src_only_array, com_only_array, common_array


def analyze_dir_diff_with_only(src_path, com_path, project_dict):
    """
    first do the same thing as analyze_dir_diff
    and then put src_only_array and com_only_array to common_array
    """
    src_only_array, com_only_array, common_array = analyze_dir_diff(
        src_path, com_path, project_dict)
    append_src_only_to_common_array(src_only_array, common_array)
    append_com_only_to_common_array(com_only_array, common_array)
    return src_only_array, com_only_array, common_array


def append_src_only_to_common_array(only_array, common_array):
    """
    append content of src only array to common array
    """
    for only in only_array:
        obj = {
            'src_path': only['path'],
            'src_size': only['size'],
            'com_path': '',
            'com_size': 0,
            'diff_size': only['size']
        }
        common_array.append(obj)


def append_com_only_to_common_array(only_array, common_array):
    """
    append content of com only array to common array
    """
    for only in only_array:
        obj = {
            'com_path': only['path'],
            'com_size': only['size'],
            'src_path': '',
            'src_size': 0,
            'diff_size': 0 - only['size']
        }
        common_array.append(obj)


def append_list_from_list(src_list, des_list):
    """
    append contents in one list to another
    """
    for obj in src_list:
        des_list.append(obj)


def append_size_to_array(plist, root, array, project_dict):
    """
    append file size to array for storage
    """
    for name in plist:
        path = root + os.sep + name
        if os.path.isdir(path):
            for r, ds, fs in os.walk(path):
                for name in fs:
                    append_file_size_to_array(
                        r + os.sep + name, array, project_dict)
        else:
            append_file_size_to_array(path, array, project_dict)


def append_file_size_to_array(path, array, project_dict):
    """
    append file to array
    """
    if check_path_with_filter(path, project_dict) == False:
        obj = {
            'path': path,
            'size': os.stat(path)[stat.ST_SIZE]
        }
        array.append(obj)


def check_path_with_filter(path, project_dict):
    """
    check path with filter regex
    [param] project_dict: a project dict get from config xml
                          file contains filter regex used
                          for path string check
    [return] True if match anly one of filter regex,
             False if not
    """
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


def _check_path_with_filter_dict(path, list_dict):
    """
    check path with filter regex
    [param] list_dict: a list dict get from config xml
                       file contains filter regex used
                       for path string check
    [return] True if match anly one of filter regex,
             False if not
    """
    result = False
    if 'id' in list_dict and 'string_array' in list_dict:
        if list_dict['id'] == 'filter_regex':
            string_array = list_dict['string_array']
            for pattern in string_array:
                if re.match(pattern, path) is not None:
                    result = True
                    break
    return result


def check_path_with_count(path, project_dict):
    """
    check path with count regex
    [param] project_dict: a project dict get from config xml
                          file contains count regex used
                          for path string check
    [return] result, strings
             result: True if match anly one of count regex,
                     False if not
             strings: pattern strings that matches path
    """
    result = False
    strings = []
    if 'task_array' in project_dict:
        task_array = project_dict['task_array']
        for task_dict in task_array:
            if 'id' in task_dict and 'list_array' in task_dict:
                if task_dict['id'] == 'file':
                    list_array = task_dict['list_array']
                    for list_dict in list_array:
                        res, strs = _check_path_with_count_dict(path, list_dict)
                        if res:
                            result = True
                            for astr in strs:
                                strings.append(astr)
                            break
    return result, strings


def _check_path_with_count_dict(path, list_dict):
    """
    check path with count regex
    [param] list_dict: a list dict get from config xml
                       file contains count regex used
                       for path string check
    [return] result, strings
             result: True if match anly one of count regex,
                     False if not
             strings: pattern strings that matches path
    """
    result = False
    strings = []
    if 'id' in list_dict and 'string_array' in list_dict:
        if list_dict['id'] == 'count_regex':
            string_array = list_dict['string_array']
            for pattern in string_array:
                if re.match(pattern, path) is not None:
                    result = True
                    strings.append(pattern)
                    break
    return result, strings


def calc_total_size(src_array, com_array, common_array):
    """
    to calculate dir total size
    """
    src_size = 0
    com_size = 0
    for obj in src_array:
        src_size += obj['size']

    for obj in com_array:
        com_size += obj['size']

    for obj in common_array:
        src_size += obj['src_size']
        com_size += obj['com_size']

    return src_size, com_size, src_size - com_size


def append_count_strings_to_dict(size, strings, result_dict):
    """
    append results of count regex analysis to dict result
    """
    for string in strings:
        if string in result_dict:
            pass
        else:
            result_dict[string] = 0
        result_dict[string] += size


def calc_regex_files_size(src_array, com_array, common_array, project_dict):
    """
    to calculate files' total size with regular expression
    """
    src_dict = {}
    com_dict = {}
    for src_obj in src_array:
        res, strings = check_path_with_count(src_obj['path'], project_dict)
        if res:
            append_count_strings_to_dict(src_obj['size'], strings, src_dict)
    for com_obj in com_array:
        res, strings = check_path_with_count(com_obj['path'], project_dict)
        if res:
            append_count_strings_to_dict(com_obj['size'], strings, com_dict)
    for common_obj in common_array:
        res, strings = check_path_with_count(common_obj['src_path'], project_dict)
    for exp in countRegexList:
        left_size = 0
        right_size = 0
        left_array = []
        right_array = []
        for obj in src_array:
            if re.match(exp, obj['path']) is not None:
                left_size += obj['size']
                left_array.append(obj['path'])
        for obj in com_array:
            if re.match(exp, obj['path']) is not None:
                right_size += obj['size']
                right_array.append(obj['path'])
        for obj in common_array:
            if re.match(exp, obj['src_path']) is not None:
                left_size += obj['src_size']
                left_array.append(obj['src_path'])
            if re.match(exp, obj['com_path']) is not None:
                right_size += obj['com_size']
                right_array.append(obj['com_path'])
        sobj = {
            'regex': exp,
            'size': left_size,
            'list': left_array
        }
        cobj = {
            'regex': exp,
            'size': right_size,
            'list': right_array
        }
        src_list.append(sobj)
        com_list.append(cobj)

    return src_list, com_list
    

def get_pos_increase_change_files(array, number):
    """
    get positive increase changed files from common array
    """
    sorted_array = sorted(array, key=lambda x:x['diff_size'], reverse=True)
    return get_increase_change_files(sorted_array, number)


def get_neg_increase_change_files(array, number):
    """
    get negative increase changed files from common array
    """
    sorted_array = sorted(array, key=lambda x:x['diff_size'])
    return get_increase_change_files(sorted_array, number)


def get_increase_change_files(sorted_array, number):
    """
    get changed files with sorted array and number
    """
    array = []
    i = 0
    for obj in sorted_array:
        if i < number:
            array.append(obj)
        else:
            break
        i = i + 1

    return array


# main function
if __name__ == '__main__':
    parser = _create_option_parser()
    (options, args) = parser.parse_args()
    _check_options_and_args(options, args)

    project_dict = project_config.parse_config_file(options.config_file)
    # parseCompareConfigFile(options.config_file)

    src_array, com_array, common_array = analyze_dir_diff_with_only(
        options.source, options.compare, project_dict)

    positive_array = get_pos_increase_change_files(common_array, options.number)
    negative_array = get_neg_increase_change_files(common_array, options.number)
    total_size = calc_total_size(src_array, com_array, common_array)
    print 'total:'
    print total_size

    src_list, com_list = calc_regex_files_size(src_array, com_array, common_array)
    print 'source:'
    for obj in src_list:
        print obj['regex'], obj['size']
    print 'compare:'
    for obj in com_list:
        print obj['regex'], obj['size']

    tag_array = ['src_path', 'com_path', 'src_size', 'com_size', 'diff_size']
    for n in negative_array:
        positive_array.append(n)
    csv.write_array_dict_to_file(options.result_file, positive_array, tag_array)

