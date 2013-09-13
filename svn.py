"""
A package for using svn command line in python function
"""
import subprocess


# path of svn tool in system
# only be used in this file
__svn_tool = None


# set svn tool path of the system
def set_svn_tool(tool):
    global __svn_tool
    __svn_tool = tool


# check svn tool set or not
# it would raise Exception if not set
def _check_svn_tool():
    if __svn_tool is None:
        raise Exception('svn tool has not set!')


# use subprocess to run args
def _subprocess_run_args(args):
    return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]


# svn log
def svn_log(path, limit=10):
    _check_svn_tool()
    args = [__svn_tool, 'log', path, '-l', str(limit)]
    return _subprocess_run_args(args)


if __name__ == '__main__':
    set_svn_tool('svn')
    output = svn_log('E:\\HeXingzhou\\workspace\\SearchBox\\build.xml')
    print output