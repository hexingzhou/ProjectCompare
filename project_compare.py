"""
A tool to compare two project in source and compare path.
It also calculate the size of files in two paths, and find
files with biggest different in size.
"""
import csv
import filecmp
import optparse
import os
import re
import stat
import sys
import xml.etree.ElementTree as et

countRegexList = []
filterRegexList = []

# create option parser
def create_option_parser():
    usage = 'usage: %prog [options]'
    version = '%prog 1.0'
    parser = optparse.OptionParser(usage=usage, version=version)

    parser.add_option('-c', '--config', 
        dest='config_file', metavar='FILE', default='compare.xml', help='config xml file')
    parser.add_option('--source', 
        dest='source', help='source project path')
    parser.add_option('--compare', 
        dest='compare', help='compare project path')
    parser.add_option('--number', 
        dest='number', type='int', default=10, help='number of results')
    parser.add_option('-r', '--result', 
        dest='result_file', metavar='FILE', default='analysis_result.csv', help='result csv format file')

    return parser


# check options and args
def check_options_and_args(options, args):
    if options.source is None:
        print 'source path is empty!'
        sys.exit()
    if options.compare is None:
        print 'compare path is empty!'
        sys.exit()

# analyze file path size change information
# test how big the change is from srcPath to comPath
def analyzeDirDiff(srcPath, comPath, filterFlag=False):
    dcmp = filecmp.dircmp(srcPath, comPath)

    src_only_array = []
    com_only_array = []
    common_array = []

    appendSizeToArray(dcmp.left_only, srcPath, src_only_array, filterFlag)
    appendSizeToArray(dcmp.right_only, comPath, com_only_array, filterFlag)

    for name in dcmp.common_files:
        src_path = srcPath + os.sep + name
        com_path = comPath + os.sep + name
        if filterFlag:
            if filterRegexCheck(src_path) or filterRegexCheck(com_path):
                continue
        src_size = os.stat(src_path)[stat.ST_SIZE]
        com_size = os.stat(com_path)[stat.ST_SIZE]
        diff_size = src_size - com_size
        obj = {
            'src_path': src_path,
            'com_path': com_path,
            'src_size': src_size,
            'com_size': com_size,
            'diff_size': diff_size
        }

        common_array.append(obj)

    for name in dcmp.common_dirs:
        if filterFlag:
            if filterRegexCheck(srcPath + os.sep + name) or filterRegexCheck(comPath + os.sep + name):
                continue
        sub_src_only_array, sub_com_only_array, sub_common_array = analyzeDirDiff(srcPath + os.sep + name, comPath + os.sep + name, filterFlag)
        appendListFromList(sub_src_only_array, src_only_array)
        appendListFromList(sub_com_only_array, com_only_array)
        appendListFromList(sub_common_array, common_array)

    return src_only_array, com_only_array, common_array


# first do the same thing as analyzeDirDiff
# and then put src_only_array and com_only_array to common_array
def analyzeDirDiffWithOnly(srcPath, comPath, filterFlag=False):
    src_only_array, com_only_array, common_array = analyzeDirDiff(srcPath, comPath, filterFlag)
    appendSrcOnlyArrayToCommonArray(src_only_array, common_array)
    appendComOnlyArrayToCommonArray(com_only_array, common_array)
    return src_only_array, com_only_array, common_array


def appendSrcOnlyArrayToCommonArray(onlyArray, commonArray):
    for e in onlyArray:
        obj = {
            'src_path': e['path'],
            'src_size': e['size'],
            'com_path': '',
            'com_size': 0,
            'diff_size': e['size']
        }
        commonArray.append(obj)


def appendComOnlyArrayToCommonArray(onlyArray, commonArray):
    for e in onlyArray:
        obj = {
            'com_path': e['path'],
            'com_size': e['size'],
            'src_path': '',
            'src_size': 0,
            'diff_size': 0 - e['size']
        }
        commonArray.append(obj)

# append contents in one list to another
def appendListFromList(srcList, desList):
    for obj in srcList:
        desList.append(obj)


# append file size to array for storage
def appendSizeToArray(plist, root, array, filterFlag=False):
    for name in plist:
        path = root + os.sep + name
        if os.path.isdir(path):
            for r, ds, fs in os.walk(path):
                for name in fs:
                    appendFileSizeToArray(r + os.sep + name, array, filterFlag)
        else:
            appendFileSizeToArray(path, array, filterFlag)

# append file to array
def appendFileSizeToArray(path, array, filterFlag=False):
    if filterFlag:
        if filterRegexCheck(path) == False:
            obj = {
                'path': path,
                'size': os.stat(path)[stat.ST_SIZE]
            }
            array.append(obj)

# parse compare config xml file to get
# 1. filter regular expression list
def parseCompareConfigFile(filename):
    try:
        root = et.parse(filename).getroot()
        all_list = root.findall('list')
        for l in all_list:
            lid = l.get('id')
            if lid == 'filter_regex':
                strings = l.findall('string')
                for string in strings:
                    filterRegexList.append(string.text)
            if lid == 'count_regex':
                strings = l.findall('string')
                for string in strings:
                    countRegexList.append(string.text)
    except IOError, e:
        print 'IOError parseCompareConfigFile(filename):', e

# using patterns in filter regular expression list to check string
# if any pattern match, return True, or return False
def filterRegexCheck(string):
    for pattern in filterRegexList:
        if re.match(pattern, string) is not None:
            return True
    return False


# to calculate dir total size
def calcTotalSize(src_array, com_array, common_array):
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


# to calculate files' total size with regular expression
def calcRegexFilesSize(src_array, com_array, common_array):
    src_list = []
    com_list = []
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
    

# get positive increase changed files from common array
def getPositiveIncreaseChangedFiles(array, number):
    sorted_array = sorted(array, key=lambda x:x['diff_size'], reverse=True)
    return getIncreaseChangedFiles(sorted_array, number)


# get negative increase changed files from common array
def getNegativeIncreaseChangedFiles(array, number):
    sorted_array = sorted(array, key=lambda x:x['diff_size'])
    return getIncreaseChangedFiles(sorted_array, number)


# get changed files with sorted array and number
def getIncreaseChangedFiles(sorted_array, number):
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
    parser = create_option_parser()
    (options, args) = parser.parse_args()
    check_options_and_args(options, args)

    parseCompareConfigFile(options.config_file)

    src_array, com_array, common_array = analyzeDirDiffWithOnly(options.source, options.compare, filterFlag=True)

    positive_array = getPositiveIncreaseChangedFiles(common_array, options.number)
    negative_array = getNegativeIncreaseChangedFiles(common_array, options.number)
    total_size = calcTotalSize(src_array, com_array, common_array)
    print 'total:'
    print total_size

    src_list, com_list = calcRegexFilesSize(src_array, com_array, common_array)
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

