"""
For create csv file and csv format string from different structure
"""
import random

# change the normal string to a formatted string
def change_to_formatted(string):
    _string = string.strip()
    flag = False
    if contains_comma(_string):
        flag = True
    if contains_quotation_mark(_string):
        _string = _string.replace('\"', '\"\"')
        flag = True
    if flag:
        _string = '\"' + _string + '\"'

    return _string


# check the string contains comma or not
def contains_comma(string):
    if ',' in string:
        return True
    return False


# check the string contains quotation mark or mot
def contains_quotation_mark(string):
    if '\"' in string:
        return True
    return False


# change content of dict to a formatted string
# [param] dict_value: a dict
# [param] tag_array: define the sort and part need 
#         to be set in the string
# [return] a formatted string
def change_dict_to_string(dict_value, tag_array):
    __random_magic_word = _random_magic_word()
    _string = ''
    for tag in tag_array:
        if len(_string) > 0:
                _string += ','
        if tag in dict_value:
            __str = change_to_formatted(str(dict_value[tag]))
            if len(__str) > 0:
                _string += __str
            else:
                _string += __random_magic_word
        else:
            _string += __random_magic_word
    _string = _string.replace(__random_magic_word, '')

    return _string


# change content of a tag array to a string
# for describe the head information in .csv file
def change_tags_to_string(tag_array):
    _string = ''
    for tag in tag_array:
        if len(_string) > 0:
            _string += ','
        _string += str(tag)
    
    return _string

# write content in a dict to .csv file
# [param] filename: name of file to be written
# [param] array_dict: an array with dict element, 
#         for example,
#         ad = [
#             {'a': aa},
#             {'a': ab}
#         ]
# [param] tag_array: tag for dict in the array
def write_array_dict_to_file(filename, array_dict, tag_array):
    with open(filename, 'w') as csv:
        _head_string = change_tags_to_string(tag_array)
        csv.writelines(_head_string + '\n')
        for d in array_dict:
            _content_string = change_dict_to_string(d, tag_array)
            csv.writelines(_content_string + '\n')


# a magic word for formatted creation progress
def _random_magic_word():
    return '#' + str(random.random()) + '#'


def _test():
    dict_value = {
        'test': 1,
        'test2': 'test2,',
        'test3': True
    }
    dict_value2 = {
        'test': 1,
        'test2': 'test2,',
        'test3': True
    }
    dict_value3 = {
        'test': 1,
        'test2': 'test2,',
        'test3': True
    }
    array_dict = [dict_value, dict_value2, dict_value3]
    tag_array = ['test_no', 'test', 'test2', 'test_no2', 'test3']
    write_array_dict_to_file('E:\\HeXingzhou\\workspace\\project_compare_py\\test.csv', array_dict, tag_array)


if __name__ == '__main__':
    _test()