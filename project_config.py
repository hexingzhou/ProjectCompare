"""
Functions to parse config files

An example:
<project>
    <task id="">
        <list id="">
            <string>xxx</string>
            <string>xxx</string>
        </list>
        <list id=""/>
    </task>
</project>
"""
import xml.etree.ElementTree as et


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


# parse a list tag in config xml file to list dict
def parse_config_list(alist):
    list_dict = {}

    lid = alist.get('id')
    if lid is not None:
        list_dict['id'] = lid

    all_string = alist.findall('string')
    list_dict['string_array'] = []
    for astring in all_string:
        list_dict['string_array'].append(astring.text)

    size_large_than = alist.get('size_large_than')
    if size_large_than is not None:
        list_dict['size_large_than'] = size_large_than

    belong = alist.get('belong')
    if belong is not None:
        list_dict['belong'] = belong

    in_attribute = alist.get('in_attribute')
    if in_attribute is not None:
        list_dict['in_attribute'] = in_attribute

    not_belong = alist.get('not_belong')
    if not_belong is not None:
        list_dict['not_belong'] = not_belong

    return list_dict