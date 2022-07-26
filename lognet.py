# Importing required standard libraries
import argparse
import logging
import time
import os
import ipaddress

# Importing required external libraries
import psutil


# Global Variables
known_connections = []
known_processes = []
new_connections = []
new_processes = []


def create_conn_logger(output_file):
    # Function creates Logging Object and File Handler for Connections
    # /var/log/netlog/ needs to exist and the user running this script requires write permissions

    # archive old log file
    timestamp = time.localtime()
    if os.path.exists(output_file):
        archived_connections_log_file = output_file[:-4] + '_' \
                                        + str(timestamp.tm_year) + '-' \
                                        + str(f'{timestamp.tm_mon:02d}') + '-' \
                                        + str(f'{timestamp.tm_mday:02d}') + '_' \
                                        + str(f'{timestamp.tm_hour:02d}') + ':' \
                                        + str(f'{timestamp.tm_min:02d}') \
                                        + '.log'
        os.renames(output_file, archived_connections_log_file)

    # create new logging object (and file)
    conn_logger = logging.getLogger('conn_logger')
    conn_handler = logging.FileHandler(output_file, mode='a', encoding='utf8')
    conn_logger.addHandler(conn_handler)
    conn_logger.setLevel(level=logging.INFO)

    # adding ELF header to log file (https://en.wikipedia.org/wiki/Extended_Log_Format)
    conn_logger.info('#Version: 1.0')
    conn_logger.info('#Date: ' + str(timestamp.tm_year)
                     + '-' + str(f'{timestamp.tm_mon:02d}')
                     + '-' + str(f'{timestamp.tm_mday:02d}')
                     + ' ' + str(f'{timestamp.tm_hour:02d}')
                     + ':' + str(f'{timestamp.tm_min:02d}')
                     + ':' + str(f'{timestamp.tm_sec:02d}'))
    conn_logger.info('#Fields: timestamp prot laddr lport raddr rport status upid')

    return conn_logger


def create_proc_logger(output_file):
    # Function creates Logging Object and File Handler for Processes
    # /var/log/netlog/ needs to exist and the user running this script requires write permissions

    # archive old log file
    timestamp = time.localtime()
    if os.path.exists(output_file):
        archived_processes_log_file = output_file[:-4] + '_' \
                                        + str(timestamp.tm_year) + '-' \
                                        + str(f'{timestamp.tm_mon:02d}') + '-' \
                                        + str(f'{timestamp.tm_mday:02d}') + '_' \
                                        + str(f'{timestamp.tm_hour:02d}') + ':' \
                                        + str(f'{timestamp.tm_min:02d}') \
                                        + '.log'
        os.renames(output_file, archived_processes_log_file)

    # create new logging object (and file)
    proc_logger = logging.getLogger('proc_logger')
    proc_handler = logging.FileHandler(output_file, mode='a', encoding='utf8')
    proc_logger.addHandler(proc_handler)
    proc_logger.setLevel(level=logging.INFO)

    # adding ELF header to log file (https://en.wikipedia.org/wiki/Extended_Log_Format)
    proc_logger.info('#Version: 1.0')
    proc_logger.info('#Date: ' + str(timestamp.tm_year)
                     + '-' + str(f'{timestamp.tm_mon:02d}')
                     + '-' + str(f'{timestamp.tm_mday:02d}')
                     + ' ' + str(f'{timestamp.tm_hour:02d}')
                     + ':' + str(f'{timestamp.tm_min:02d}')
                     + ':' + str(f'{timestamp.tm_sec:02d}'))
    proc_logger.info('#Fields: timestamp upid [command_line with parameters]')

    return proc_logger


def log_new_connections(conn_logger):
    # Function empties new_connections array into log file

    for conn in new_connections:
        timestamp = time.localtime()

        # create the timestamp string and add it to the log message
        ts_string = str(timestamp.tm_year) \
                      + '-' + str(f'{timestamp.tm_mon:02d}') \
                      + '-' + str(f'{timestamp.tm_mday:02d}') \
                      + '|' + str(f'{timestamp.tm_hour:02d}') \
                      + ':' + str(f'{timestamp.tm_min:02d}') \
                      + ':' + str(f'{timestamp.tm_sec:02d}')
        log_message = ts_string

        # create the PROT string and add it to the log message
        if conn['type']:
            if str(conn['type']) == 'SocketKind.SOCK_DGRAM':
                prot_string = 'UDP'
            elif str(conn['type']) == 'SocketKind.SOCK_STREAM':
                prot_string = 'TCP'
            else:
                prot_string = str(conn['type'])
            log_message = log_message + ' ' + prot_string
        else:
            log_message = log_message + ' ' + '-'

        # create the LADDR string and add it to the log message
        if len(conn['laddr']) > 0:
            laddr_string = str(conn['laddr'][0])
            log_message = log_message + ' ' + laddr_string
        else:
            log_message = log_message + ' ' + '-'

        # create the LPORT string and add it to the log message
        if len(conn['laddr']) > 1:
            lport_string = str(conn['laddr'][1])
            log_message = log_message + ' ' + lport_string
        else:
            log_message = log_message + ' ' + '-'

        # create the RADDR string and add it to the log message
        if len(conn['raddr']) > 0:
            raddr_string = str(conn['raddr'][0])
            log_message = log_message + ' ' + raddr_string
        else:
            log_message = log_message + ' ' + '-'

        # create the RPORT string and add it to the log message
        if len(conn['raddr']) > 1:
            rport_string = str(conn['raddr'][1])
            log_message = log_message + ' ' + rport_string
        else:
            log_message = log_message + ' ' + '-'

        # create the STATUS string and add it to the log message
        if conn['status']:
            status_string = str(conn['status'])
            log_message = log_message + ' ' + status_string
        else:
            log_message = log_message + ' ' + '-'

        # create the uPID string and add it to the log message
        if conn['uPID']:
            upid_string = str(conn['uPID'])
            log_message = log_message + ' ' + upid_string
        else:
            log_message = log_message + ' ' + '-'

        # write log message into the log
        conn_logger.info(log_message)

    new_connections.clear()


def log_new_processes(proc_logger):
    # Function empties new_connections array into log file

    for proc in new_processes:
        timestamp = time.localtime()

        # create the timestamp string and add it to the log message
        ts_string = str(timestamp.tm_year) \
                    + '-' + str(f'{timestamp.tm_mon:02d}') \
                    + '-' + str(f'{timestamp.tm_mday:02d}') \
                    + '|' + str(f'{timestamp.tm_hour:02d}') \
                    + ':' + str(f'{timestamp.tm_min:02d}') \
                    + ':' + str(f'{timestamp.tm_sec:02d}')
        log_message = ts_string

        # create the uPID string and add it to the log message
        if len(proc['uPID']) > 0:
            upid_string = str(proc['uPID'])
            log_message = log_message + ' ' + upid_string
        else:
            log_message = log_message + ' ' + '-'

        # create the COMMAND_LINE string and add it to the log message
        if len(proc['command_line']) > 0:
            command_line_string = str(proc['command_line'])
            log_message = log_message + ' ' + command_line_string
        else:
            log_message = log_message + ' ' + '-'

        # write log message into the log
        proc_logger.info(log_message)

    new_processes.clear()


def connection_is_known(unique_conn) -> bool:
    # Function checks whether a connection with unique_conn is known

    conn_is_known = False
    for conn in known_connections:
        if conn['uConn'] == unique_conn:
            conn_is_known = True

    return conn_is_known


def process_is_known(unique_pid) -> bool:
    # Function checks whether a process with unique_pid is known

    process_is_known = False
    for process in known_processes:
        if process['uPID'] == unique_pid:
            process_is_known = True

    return process_is_known


def check_connections(args) -> bool:
    # Function gets current snapshot of network connections on the system and processes them

    # gather all connections based on command line arguments
    if args.ipv and args.p:
        if args.p == 'udp' and args.ipv == 4:
            current_connections = psutil.net_connections(kind='udp4')
        elif args.p == 'tcp' and args.ipv == 4:
            current_connections = psutil.net_connections(kind='tcp4')
        elif args.p == 'udp' and args.ipv == 6:
            current_connections = psutil.net_connections(kind='udp6')
        elif args.p == 'tcp' and args.ipv == 6:
            current_connections = psutil.net_connections(kind='tcp6')
    elif args.ipv and not args.p:
        if args.ipv == 4:
            current_connections = psutil.net_connections(kind='inet4')
        elif args.ipv == 6:
            current_connections = psutil.net_connections(kind='inet6')
    elif args.p and not args.ipv:
        if args.p == 'udp':
            current_connections = psutil.net_connections(kind='udp')
        elif args.p == 'tcp':
            current_connections = psutil.net_connections(kind='tcp')
    else:
        current_connections = psutil.net_connections(kind='inet')

    # process new connections
    for connection in current_connections:

        omit_local_network = False
        omit_conns_to_self = False

        # if command line argument "--omit-privnet-conns" is set, ignore conns to private networks
        if args.omit_privnet_conns and connection.raddr:
            r_ip = ipaddress.ip_address(str(connection.raddr[0]))
            if r_ip in ipaddress.ip_network('192.168.0.0/16'):
                omit_local_network = True
            elif r_ip in ipaddress.ip_network('172.16.0.0/12'):
                omit_local_network = True
            elif r_ip in ipaddress.ip_network('10.0.0.0/8'):
                omit_local_network = True
        # if command line argument "--omit-self-conns" is set, ignore conns to self
        if args.omit_self_conns and not connection.raddr:
            omit_conns_to_self = True

        if not omit_conns_to_self and not omit_local_network:

            # gather info on the process and add to list, if not known
            process = psutil.Process(connection.pid)
            u_pid = str(process.name()) + '|' + str(process.pid) + '|' + str(process.create_time())
            if process_is_known(u_pid):
                pass
            else:
                new_process = {'uPID': u_pid,
                               'pid': process.pid,
                               'name': process.name(),
                               'command_line': process.cmdline(),
                               'create_time': process.create_time()}
                new_processes.append(new_process)
                known_processes.append(new_process)

            # gather info on connection and add to list, if not known
            u_conn = str(connection.fd) + '|' + str(connection.laddr) + '|' + str(connection.raddr) + '|' + str(connection.status) + '|' + u_pid
            if connection_is_known(u_conn):
                pass
            else:
                new_connection = {'uConn': u_conn,
                                  'fd': connection.fd,
                                  'family': connection.family,
                                  'type': connection.type,
                                  'laddr': connection.laddr,
                                  'raddr': connection.raddr,
                                  'status': connection.status,
                                  'uPID': u_pid}
                new_connections.append(new_connection)
                known_connections.append(new_connection)

    if new_connections or new_processes:
        return True
    else:
        return False


def get_argument_parser():
    # helper function to add command line arguments

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-i", type=float,default=3,
                                 help="interval (in seconds) for connection enumeration (default: 3s)")
    argument_parser.add_argument("-clog", type=str, default="/var/log/netlog/connections.log",
                                 help="output file for connections log (default: /var/log/netlog/connections.log)")
    argument_parser.add_argument("-plog", type=str, default="/var/log/netlog/processes.log",
                                 help="output file for processes list (default: /var/log/netlog/processes.log)")
    argument_parser.add_argument("-ipv", type=int, choices=[4, 6],
                                 help="filters by internet protocol version (if omitted, it includes both)")
    argument_parser.add_argument("-p", type=str, choices=["udp", "tcp"],
                                 help="filters by protocol (if omitted, it includes both)")
    argument_parser.add_argument("--omit-self-conns", action="store_true",
                                 help="omits connections without remote address")
    argument_parser.add_argument("--omit-privnet-conns", action="store_true",
                                 help="omits connections to private networks")

    return argument_parser.parse_args()


if __name__ == '__main__':

    arguments = get_argument_parser()
    connection_logger = create_conn_logger(arguments.clog)
    process_logger = create_proc_logger(arguments.plog)

    while True:
        # IF we found new connections or processes, we need to add them to the logs
        if check_connections(arguments):
            log_new_connections(connection_logger)
            log_new_processes(process_logger)
        else:
            time.sleep(arguments.i)
