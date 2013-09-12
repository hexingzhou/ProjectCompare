"""
To analyze file size in a project.
It may create report for the result.
"""
import csv
import optparse
import os
import stat
import sys
import xml.etree.ElementTree as et


# create option parser
def create_option_parser():
    usage = 'usage: %prog [options] project_path'
    version = '%prog 1.0'
    parser = optparse.OptionParser(usage=usage, version=version)

    parser.add_option('-c', '--config', 
        dest='config_file', metavar='FILE', default='project_file_config.xml', help='config xml file')
    parser.add_option('-r', '--result', 
        dest='result_file', metavar='FILE', default='project_file_analysis_result.csv', 
        help='result csv format file')

    return parser


# parse config xml file to project dict
def parse_config_file(filename):
    project = {}

    root = et.parse(filename).getroot()

    all_task = root.findall('task')
    project['task_array'] = []
    for task in all_task:
        task_dict = parse_config_task(task)
        project['task_array'].append(task_dict)

    return project


# parse a task tag in config xml file to task dict
def parse_config_task(task):
    task_dict = {}

    tid = task.get('id')
    if tid is not None:
        task_dict['id'] = tid

        all_list = task.findall('list')
        task_dict['list_array'] = []
        for alist in all_list:
            list_dict = parse_config_list(alist)
            task_dict['list_array'].append(list_dict)
    
    return task_dict


def parse_config_list(alist):
    list_dict = {}

    lid = alist.get('id')
    if lid is not None:
        list_dict['id'] = lid

        all_string = alist.findall('string')
        list_dict['string_array'] = []
        for astring in all_string:
            list_dict['string_array'].append(astring.text)

    return list_dict


# calculate file size in a path
# and set it in res_array
# [param] path: file path for analysis
def calc_file_size(path, sort_reverse=True):
    _result_array = []
    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            _path = os.path.join(dirpath, name)
            _obj = {
                'path': _path,
                'size': os.stat(_path)[stat.ST_SIZE]
            }
            _result_array.append(_obj)

    _result_array = sorted(_result_array, key=lambda x:x['size'], reverse=sort_reverse)
    return _result_array


# check options and args
def check_options_and_args(options, args):
    if len(args) == 0:
        print 'no project_path'
        sys.exit()


if __name__ == '__main__':
    parser = create_option_parser()
    (options, args) = parser.parse_args()
    check_options_and_args(options, args)

    print parse_config_file(options.config_file)

    array_dict = calc_file_size(args[0])
    tag_array = ['path', 'size']
    csv.write_array_dict_to_file(options.result_file, array_dict, tag_array)