"""
Functions to analyze the lint analysis xml result
"""
import butils
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
        dest='result_file', metavar='FILE', default='lint_analyze_result', 
        help='result file')

    return parser


# check options and args
def _check_options_and_args(options, args):
    if options.lint_result is None:
        print 'lint result xml file path is empty!'
        sys.exit()
    if options.android_project_root is None:
        print 'android project root path is empty!'
        sys.exit()


def check_unused_resources(path, project_dict):
    return check_unused_resources_tree(et.parse(path), project_dict)


def check_unused_resources_tree(tree, project_dict):
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
    clean_lint_result_tree(tree, project_dict)


def clean_lint_result_tree(tree, project_dict):
    root = tree.getroot()
    all_issues = root.findall('issue')
    for issue in all_issues:
        if _check_issue_need_remove(issue, project_dict):
            root.remove(issue)

    tree.write(path, encoding='utf-8', xml_declaration=True)


def _check_issue_need_remove(issue, project_dict):
    result = False
    if 'task_array' in project_dict:
        task_array = project_dict['task_array']
        for task_dict in task_array:
            if _check_issue_need_remove_with_task(issue, task_dict):
                result = True
                break
    return result


def _check_issue_need_remove_with_task(issue, task_dict):
    result = False
    if 'id' in task_dict and 'list_array' in task_dict:
        if task_dict['id'] == 'lint':
            list_array = task_dict['list_array']
            for list_dict in list_array:
                if _check_issue_need_remove_with_list(issue, list_dict):
                    result = True
                    break
    return result


def _check_issue_need_remove_with_list(issue, list_dict):
    result = False
    if 'id' in list_dict and 'not_belong' in list_dict:
        if list_dict['id'] == 'clean_issue':
            not_belong = list_dict['not_belong']
            iid = issue.get('id')
            if iid != not_belong:
                result = True
    return result


if __name__ == '__main__':
    parser = _create_option_parser()
    (options, args) = parser.parse_args()
    _check_options_and_args(options, args)

    project_dict = project_config.parse_config_file(options.config_file)

    svn.set_svn_tool('svn')
    result_dict = {}

    resource_array = check_unused_resources(options.lint_result, project_dict)
    svn.set_svn_tool('svn')
    for resource in resource_array:
        log_string = svn.svn_log(options.android_project_root + os.sep + resource, 1)
        log_name = butils.get_lastest_name_from_svn_log(log_string)
        if log_name is not None:
            if log_name in result_dict:
                pass
            else:
                result_dict[log_name] = []
            result_dict[log_name].append(resource)

    with open(options.result_file, 'w') as rfile:
        rfile.writelines('Here may be some unused resources:\n')
        for name in result_dict:
            rfile.writelines('\n')
            rfile.writelines('Author: ' + name + '\n')
            for res in result_dict[name]:
                rfile.writelines('|-> ' + res + '\n')

    clean_lint_result(options.lint_result, project_dict)