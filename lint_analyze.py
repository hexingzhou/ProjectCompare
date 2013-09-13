"""
Functions to analyze the lint analysis xml result
"""
import optparse
import os
import project_config
import re
import svn
import sys
import xml.etree.ElementTree as et


# create option parser
def _create_option_parser():
    usage = 'usage: %prog [options]'
    version = '%prog 1.0'
    parser = optparse.OptionParser(usage=usage, version=version)

    parser.add_option('-c', '--config', 
        dest='config_file', metavar='FILE', default='lint_analyze_config.xml', help='config xml file')
    parser.add_option('--android-project-root',
        dest='android_project_root', help='android project root path')
    parser.add_option('--lint-result',
        dest='lint_result', metavar='FILE', help='lint result xml file')
    parser.add_option('-r', '--result', 
        dest='result_file', metavar='FILE', default='lint_analyze_result.csv', 
        help='result csv format file')

    return parser


# check options and args
def _check_options_and_args(options, args):
    if options.lint_result is None:
        print 'lint result xml file path is empty!'
        sys.exit()
    if options.android_project_root is None:
        print 'android project root path is empty!'
        sys.exit()


def check_unused_resources(tree, project_dict):
    result = []
    root = tree.getroot()
    all_issues = root.findall('issue')
    for issue in all_issues:
        if _check_unused_resources_issue(issue, project_dict):
            path = _catch_need_unused_resources_issue(issue)
            if path is not None:
                result.append(path)
    return result


def _catch_need_unused_resources_issue(issue):
    result = None
    location = issue.find('location')
    if location is not None:
        filepath = location.get('file')
        if filepath is not None:
            result = filepath
    return result


def _check_unused_resources_issue(issue, project_dict):
    result = False
    if 'task_array' in project_dict:
        task_array = project_dict['task_array']
        for task_dict in task_array:
            if _check_unused_resources_issue_with_task(issue, task_dict):
                result = True
                break
    return result


def _check_unused_resources_issue_with_task(issue, task_dict):
    result = False
    if 'id' in task_dict and 'list_array' in task_dict:
        if task_dict['id'] == 'lint':
            list_array = task_dict['list_array']
            for list_dict in list_array:
                if _check_unused_resources_issue_with_list(issue, list_dict):
                    result = True
                    break
    return result


def _check_unused_resources_issue_with_list(issue, list_dict):
    result = False
    if 'id' in list_dict and 'belong' in list_dict and 'in_attribute' in list_dict:
        if list_dict['id'] == 'match_regex':
            belong = list_dict['belong']
            in_attribute = list_dict['in_attribute']

            iid = issue.get('id')
            if iid == belong:
                imessage = issue.get(in_attribute)
                if imessage is not None and 'string_array' in list_dict:
                    string_array = list_dict['string_array']
                    for pattern in string_array:
                        if re.match(pattern, imessage) is not None:
                            result = True
                            break
    return result


# remove tree note in lint result xml file
def clean_lint_result(path, project_dict):
    tree = et.parse(path)
    root = tree.getroot()
    all_issues = root.findall('issue')
    for issue in all_issues:
        iid = issue.get('id')
        if iid != 'NewApi':
            root.remove(issue)

    tree.write(path, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    parser = _create_option_parser()
    (options, args) = parser.parse_args()
    _check_options_and_args(options, args)

    project_dict = project_config.parse_config_file(options.config_file)
    tree = et.parse(options.lint_result)

    resource_array = check_unused_resources(tree, project_dict)
    svn.set_svn_tool('svn')
    for resource in resource_array:
        print resource
        print svn.svn_log(options.android_project_root + os.sep + resource, 1)

    # clean_lint_result(options.lint_result, None)