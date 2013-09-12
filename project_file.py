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


# parse config xml file to task dict
def parse_config_file(filename):
    _project = []

    _root = et.parse(filename).getroot()
    _all_task = _root.findall('task')
    for _task in _all_task:
        _task_dict = parse_config_task(_task)
        _project.append(_task_dict)

    return _project


def parse_config_task(task):
    _id = task.get('id')
    print _id


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

    parse_config_file(options.config_file)

    _array_dict = calc_file_size(args[0])
    _tag_array = ['path', 'size']
    csv.write_array_dict_to_file(options.result_file, _array_dict, _tag_array)