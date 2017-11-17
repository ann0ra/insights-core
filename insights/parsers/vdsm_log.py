"""
VDSMLog - file ``/var/log/vdsm/vdsm.log``
=========================================
"""

from insights import LogFileOutput, parser
from datetime import datetime
from insights.specs import vdsm_log


@parser(vdsm_log)
class VDSMLog(LogFileOutput):
    """
    Logs from the Virtual Desktop and Server Manager.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Sample logs from VDSM::

        Thread-60::DEBUG::2015-05-08 18:01:03,071::blockSD::600::Storage.Misc.excCmd::(getReadDelay) '/bin/dd if=/dev/5a30691d-4fae-4023-ae96-50704f6b253c/metadata iflag=direct of=/dev/null bs=4096 count=1' (cwd None)
        Thread-60::DEBUG::2015-05-08 18:01:03,090::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\\n1+0 records out\\n4096 bytes (4.1 kB) copied, 0.00038933 s, 10.5 MB/s\\n'; <rc> = 0
        Thread-65::DEBUG::2015-05-08 18:01:04,835::blockSD::600::Storage.Misc.excCmd::(getReadDelay) '/bin/dd if=/dev/e70cce65-0d02-4da4-8781-6aeeef5c86ff/metadata iflag=direct of=/dev/null bs=4096 count=1' (cwd None)
        Thread-65::DEBUG::2015-05-08 18:01:04,857::blockSD::600::Storage.Misc.excCmd::(getReadDelay) SUCCESS: <err> = '1+0 records in\\n1+0 records out\\n4096 bytes (4.1 kB) copied, 0.000157193 s, 26.1 MB/s\\n'; <rc> = 0
        Thread-4662::DEBUG::2015-05-08 18:01:05,560::task::595::TaskManager.Task::(_updateState) Task=`9a7948f6-b6d9-42c2-b91f-7e0346dfc1d6`::moving from state init -> state preparing

    Each line is parsed into a dictionary with the following keys:

        * **thread** - the thread or task ID
        * **level** - the log level
        * **timestamp** - the date of the log line (as a string)
        * **datetime** - the date as a datetime object (if conversion is possible)
        * **module** - the module logging the message
        * **line** - the line reporting this message within the module
        * **logname** - the logger's name
        * **funcname** - the function name reporting the message
        * **message** - the body of the message
        * **raw_message** - the original unparsed line

        The **datetime** field is only present if the `timestamp` field
        is present contains a time stamp in the valid format.

        If the line is too short, for some reason, then as many fields as
        possible are pulled from the line.

    Example:
        >>> log = shared[VDSMLog]
        >>> log.get('TaskManager')[0]
        {'raw_message': 'Thread-4662::DEBUG::2015-05-08 18:01:05,560::task::595::TaskManager.Task::(_updateState) Task=`9a7948f6-b6d9-42c2-b91f-7e0346dfc1d6`::moving from state init -> state preparing',
         'thread': 'Thread-4662',
         'level': 'DEBUG',
         'timestamp': '2015-05-08 18:01:05,560',
         'datetime': datetime(2015, 5, 8, 18, 1, 5),
         'module': 'task',
         'line': '595',
         'logname': 'TaskManager.Task',
         'funcname': '_updateState',
         'message': 'Task=`9a7948f6-b6d9-42c2-b91f-7e0346dfc1d6`::moving from state init -> state preparing'
        }
    """

    def _parse_line(self, line):
        """
        """

        # funcname is in brackets before message, so parse those separately
        fieldnames = ('thread', 'level', 'timestamp', 'module', 'line', 'logname')
        parts = line.split('::', 6)
        fields = {'raw_message': line}
        for k, v in zip(fieldnames, parts):
            fields.update({k: v})
        if len(parts) == 7:
            func, msg = parts[6].split(' ', 1)
            fields['funcname'] = func[1:-1]  # remove surrounding brackets
            fields['message'] = msg
        # Did we get a timestamp in there?
        if 'timestamp' in fields:
            # Try to convert the datetime if possible
            try:
                fields['datetime'] = datetime.strptime(
                    fields['timestamp'][:-4],  # skip milliseconds
                    self.time_format
                )
            except:
                pass
        return fields
