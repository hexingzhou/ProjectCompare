import csv
import optparse
import urllib2

def createOptionParser():
    usage = 'usage: %prog [options] arg1 arg2'
    version = '%prog 1.0'
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=True)
    parser.add_option('-q', '--quiet', action='store_false', dest='verbose', help='This is a help of quiet')
    parser.add_option('-t', action='count', dest='count', default=2, help='help for -t')

    group = optparse.OptionGroup(parser, 'Test Group')
    group.add_option('-a', '-b', action='store_false', dest='test', help='help for -a or -b')
    group.add_option('-f', dest='filename', metavar='FILE', help='help for -f')

    parser.add_option_group(group)

    return parser

if __name__ == '__main__':
    # test for optparse
    parser = createOptionParser()
    (options, args) = parser.parse_args()
    print options
    print args

    print csv.change_to_formatted('\"')

    # response = urllib2.urlopen('http://www.baidu.com')