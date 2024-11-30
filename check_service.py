import os
import re
import csv
from netmiko import ConnectHandler

os_path = os.path.dirname(os.path.abspath('check_serv.py'))

def create_show_bmw():
    directory = os_path + '\\show_commands_before_mw'
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_table_bmw():
    directory = os_path + '\\table_before_mw'
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_outputs_bmw():
    directory = os_path + '\\outputs_before_mw'
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_outputs_amw():
    directory = os_path + '\\outputs_after_mw'
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_show_amw():
    directory = os_path + '\\show_commands_after_mw'
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_table():
    directory = os_path + '\\tables'
    if not os.path.exists(directory):
        os.makedirs(directory)

def route_table():
    regex = ('(.*): \d+ destinations, (\d+) routes')
    route_table = os_path + '\\table_before_mw\\route summary.csv'
    with open(route_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["vpn_name", "routes_before"])
        with open(os_path + '\\show_commands_before_mw\\show route summary') as a:
                for line in a:
                    match = re.finditer(regex, line)
                    if "inet" in line:
                        if match:
                            for m in match:
                                name = m.group(1)
                                routes = m.group(2)
                                writer.writerow([name] + [routes])

def dict_route_table():
    regex = ('(.*): \d+ destinations, (\d+) routes')
    dict = {}
    with open(os_path + '\\show_commands_before_mw\\show route summary') as a:
        for line in a:
            match = re.finditer(regex, line)
            if "inet" in line:
                if match:
                    for m in match:
                        name = m.group(1)
                        routes = m.group(2)
                        dict[name] = routes
    return (dict)

def route_table_amw():
    regex = ('(.*): \d+ destinations, (\d+) routes')
    route_table = os_path + '\\tables\\route summary.csv'
    dict_route_table1 = {}
    with open(route_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["vpn_name", "routes_before", "routes_after", "diff", "summary"])
        with open(os_path + '\\show_commands_after_mw\\show route summary') as a:
            for line in a:
                match = re.finditer(regex, line)
                if "inet" in line:
                    if match:
                        for m in match:
                            name = m.group(1)
                            routes = m.group(2)
                            dict_route_table1[name] = routes
                            if (name == k for k in dict_route_table().keys()):
                                diff = round((1-(int(routes)+1)/(int((dict_route_table()[name]))+1))*100)
                                if int(str(diff).strip("%")) > 20:
                                    result = ">20%"
                                else:
                                    result = ""
                                writer.writerow([name] + [dict_route_table()[name]] + [routes] + [str(diff)+"%"] + [result])

def dict_interfaces_state_table():
    regex = ('Physical interface: (.*), .*, Physical link is (.*)\n'
             '  Input rate     : .* bps .*\n'
             '  Output rate    : .* bps .*')
    dict = {}
    with open(os_path + '\\show_commands_before_mw\\show interfaces.log') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return (dict)

def dict_interfaces_traffic_in_table():
    regex = ('Physical interface: (.*), .*, Physical link is .*\n'
             '  Input rate     : (.*) bps .*\n'
             '  Output rate    : .* bps .*')
    dict = {}
    with open(os_path + '\\show_commands_before_mw\\show interfaces.log') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                in_traffic = m.group(2)
                dict[name] = {in_traffic}
    return (dict)

def dict_interfaces_traffic_out_table():
    regex = ('Physical interface: (.*), .*, Physical link is .*\n'
             '  Input rate     : .* bps .*\n'
             '  Output rate    : (.*) bps .*')
    dict = {}
    with open(os_path + '\\show_commands_before_mw\\show interfaces.log') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                out_traffic = m.group(2)
                dict[name] = {out_traffic}
    return (dict)

def interface_state_table_amw():
    regex = ('Physical interface: (.*), .*, Physical link is (.*)\n'
             '  Input rate     : .* bps .*\n'
             '  Output rate    : .* bps .*')
    dict = {}
    interface_state_table = os_path + '\\tables\\interface state.csv'
    with open(interface_state_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interfaces_name", "state_before", "state_after", "summary"])
        with open(os_path + '\\show_commands_after_mw\\show interfaces.log') as a:
            match = re.finditer(regex, a.read())
            if match:
                for m in match:
                    name = m.group(1)
                    state = m.group(2)
                    dict[name] = {state}
                    if (name == k for k in dict_interfaces_state_table().keys()):
                        state_before = str(dict_interfaces_state_table()[name]).replace("{'", "").replace("'}", "")
                        if state_before == state:
                            result = "Ok"
                        else:
                            result = "Not Ok"
                        writer.writerow([name] + [state_before] + [state] + [result])

def interface_traffic_table_amw():
    regex = ('Physical interface: (.*), .*, Physical link is .*\n'
             '  Input rate     : (.*) bps .*\n'
             '  Output rate    : (.*) bps .*')
    dict = {}
    interface_traffic_table = os_path + '\\tables\\interface traffic.csv'
    with open(interface_traffic_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interfaces_name", "traffic_in_before", "traffic_in_after", "diff", "summary", "traffic_out_before", "traffic_out_after", "diff", "summary"])
        with open(os_path + '\\show_commands_after_mw\\show interfaces.log') as a:
            match = re.finditer(regex, a.read())
            if match:
                for m in match:
                    name = m.group(1)
                    in_traffic = m.group(2)
                    out_traffic = m.group(3)
                    dict[name] = {in_traffic, out_traffic}
                    if (name == k for k in dict_interfaces_traffic_in_table().keys()):
                        traffic_in_before = str(dict_interfaces_traffic_in_table()[name]).replace("{'", "").replace("'}", "")
                        traffic_out_before = str(dict_interfaces_traffic_out_table()[name]).replace("{'", "").replace("'}", "")
                        try:
                            diff_in_traffic = round((1-(int(in_traffic))/(int(traffic_in_before)))*100)
                        except ZeroDivisionError:
                            diff_in_traffic = 0
                        try:
                            diff_out_traffic = round((1-(int(out_traffic))/(int(traffic_out_before)))*100)
                        except ZeroDivisionError:
                            diff_in_traffic = 0
                        if diff_in_traffic > 30:
                            result_in_traffic = ">30%"
                        elif diff_in_traffic <= 30:
                            result_in_traffic = ""
                        if diff_out_traffic > 30:
                            result_out_traffic = ">30%"
                        elif diff_out_traffic <= 30:
                            result_out_traffic = ""
                        writer.writerow([name] + [traffic_in_before] + [in_traffic] + [str(diff_in_traffic) + "%"] + [result_in_traffic] + [traffic_out_before] + [out_traffic] + [str(diff_out_traffic) + "%"] + [result_out_traffic])

def bgp_summary_amw():
    regex = ('(\S+)\s+\d+\s+\d+\s+\d+.*\n')
    bgp_summary_table = os_path + '\\tables\\bgp summary.csv'
    with open(bgp_summary_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["neighbor", "summary"])
        with open(os_path + '\\show_commands_before_mw\\show bgp summary') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                with open(os_path + '\\show_commands_after_mw\\show bgp summary') as b:
                    if (name + " ") in b.read():
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [result])

def dict_bfd_table():
    regex = ('(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\d+\s+\n')
    dict = {}
    with open(os_path + '\\show_commands_before_mw\\show bfd session') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return (dict)

def bfd_amw():
    regex = ('(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\d+\s+\n')
    bfd_table = os_path + '\\tables\\bfd.csv'
    dict = {}
    with open(bfd_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["neighbor", "state_before", "state_after", "summary"])
        with open(os_path + '\\show_commands_after_mw\\show bfd session') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                state = m.group(2)
                if (name == k for k in dict_bfd_table().keys()):
                    state_before = str(dict_bfd_table()[name]).replace("{'", "").replace("'}", "")
                    if state_before == state:
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [state_before] + [state] + [result])

def dict_isis_name_table():
    regex = ('(\S+)\s+(\S+)\s+\d+\s+\S+\s+\d+\n')
    dict = {}
    with open(os_path + '\\show_commands_before_mw\\show isis adjacency.log') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                neighbor = m.group(2)
                dict[name] = {neighbor}
    return (dict)

def dict_isis_state_table():
    regex = ('(\S+)\s+\S+\s+\d+\s+(\S+)\s+\d+\n')
    dict = {}
    with open(os_path + '\\show_commands_before_mw\\show isis adjacency.log') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return (dict)

def isis_adjacency_amw():
    regex = ('(\S+)\s+(\S+)\s+\d+\s+(\S+)\s+\d+\n')
    isis_adjacency_table = os_path + '\\tables\\isis adjacency.csv'
    dict = {}
    with open(isis_adjacency_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interface", "neighbor", "state_before", "state_after", "summary"])
        with open(os_path + '\\show_commands_after_mw\\show isis adjacency.log') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                neighbor =m.group(2)
                state = m.group(3)
                if (name == k for k in dict_isis_name_table().keys()):
                    state_before = str(dict_isis_state_table()[name]).replace("{'", "").replace("'}", "")
                    if state_before == state:
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [neighbor] + [state_before] + [state] + [result])

def dict_l2circuit_table():
    regex = ('\s+(\S+\(vc\s+\d+\))\s+\S+\s+(\S+).*')
    dict = {}
    with open(os_path + '\\show_commands_before_mw\\show l2circuit connect') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return (dict)

def l2circuit_amw():
    regex = ('\s+(\S+\(vc\s+\d+\))\s+\S+\s+(\S+).*')
    l2_circuit_table = os_path + '\\tables\\l2circuit.csv'
    with open(l2_circuit_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interface", "state_before", "state_after", "summary"])
        with open(os_path + '\\show_commands_after_mw\\show l2circuit connect') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                state = m.group(2)
                if (name == k for k in dict_l2circuit_table().keys()):
                    state_before = str(dict_l2circuit_table()[name]).replace("{'", "").replace("'}", "")
                    if state_before == state:
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [state_before] + [state] + [result])

def ldp_neighbor():
    regex = ('(\S+)\s+\S+\s+\S+\s+\d+\n')
    ldp_neighbor_table = os_path + '\\tables\\ldp neighbor.csv'
    with open(ldp_neighbor_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["neighbor", "summary"])
        with open(os_path + '\\show_commands_before_mw\\show ldp neighbor') as b:
            match = re.finditer(regex, b.read())
            for m in match:
                name = m.group(1)
                with open(os_path + '\\show_commands_after_mw\\show ldp neighbor') as a:
                    if (name + " ") in a.read():
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [result])

def dict_ldp_session_table():
    regex = ('(\S+)\s+(\S+)\s+\S+\s+\d+\s+\S+\n')
    dict = {}
    with open(os_path + '\\show_commands_before_mw\\show mpls lsp') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return (dict)

def ldp_session():
    regex = ('(\S+)\s+(\S+)\s+\S+\s+\d+\s+\S+\n')
    ldp_session_table = os_path + '\\tables\\ldp session.csv'
    with open(ldp_session_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["address", "state_before", "state_after", "summary"])
        with open(os_path + '\\show_commands_before_mw\\show ldp session') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                state = m.group(2)
                if (name in dict_ldp_session_table().keys()):
                    state_after = str(dict_ldp_session_table()[name]).replace("{'", "").replace("'}", "")
                    if state_after == state:
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [state] + [state_after] + [result])
                else:
                    writer.writerow([name] + [state] + [""] + ["Not Ok"])

def list_mpls_lsp_ingress_table():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\S+)\n')
    list = []
    with open(os_path + '\\show_commands_after_mw\\show mpls lsp') as a:
        for n, line in enumerate(a):
            if "Ingress" in line:
                start = n+1
                list.append(start)
            elif "Egress" in line:
                end = n-2
                list.append(end)
    #print(list)
    return (list)

def list_mpls_lsp_egress_table():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\S+)\n')
    list = []
    with open(os_path + '\\show_commands_after_mw\\show mpls lsp') as a:
        for n, line in enumerate(a):
            if "Egress" in line:
                start = n+1
                list.append(start)
            elif "Transit" in line:
                end = n-2
                list.append(end)
    #print(list)
    return (list)

def list_mpls_lsp_transit_table():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\S+)\n')
    list = []
    with open(os_path + '\\show_commands_after_mw\\show mpls lsp') as a:
        for n, line in enumerate(a):
            if "Transit" in line:
                start = n+1
    return (start)

def dict_ingress_lsp():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\S+)\n')
    dict = {}
    with open(os_path + '\\show_commands_after_mw\\show mpls lsp') as a:
        for n, line in enumerate(a):
            if n > list_mpls_lsp_ingress_table()[0] and n < list_mpls_lsp_ingress_table()[1]:
                to = re.search(regex, line).group(1)
                state = re.search(regex, line).group(3)
                dict[to] = state
    return (dict)

def dict_egress_lsp():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    dict = {}
    with open(os_path + '\\show_commands_after_mw\\show mpls lsp') as a:
        for n, line in enumerate(a):
            if n > list_mpls_lsp_egress_table()[0] and n < list_mpls_lsp_egress_table()[1]:
                from_ip = re.search(regex, line).group(2)
                state = re.search(regex, line).group(3)
                dict[from_ip] = state
    return (dict)

def dict_transit_lsp():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    dict = {}
    with open(os_path + '\\show_commands_after_mw\\show mpls lsp') as a:
        for n, line in enumerate(a):
            if n > list_mpls_lsp_transit_table() and ("." in line):
                state = re.search(regex, line).group(3)
                name = re.search(regex, line).group(4)
                dict[name] = state
        print(dict)
    return (dict)
def ssh_to_router(command):
    with open(os_path + "\\ssh_connection.txt") as a:
        login = re.search('login: (.*)\n', a.readline()).group(1)
        password = re.search('password: (.*)\n', a.readline()).group(1)
        ip = re.search('loopback: (.*)\n', a.readline()).group(1)
        device = {
            "device_type": "juniper_junos",
            "username": login,
            "password": password,
            "ip": ip,
            "port": "22",
            "timeout": "20"}
        with ConnectHandler(**device) as ssh:
            ssh.enable()
            result = ssh.send_command(command)
        print(result)
        return (result)

def collect_outputs_before_upgrade():
    with open(os_path + "\\ssh_connection.txt") as a:
        hostname = "@" + re.search('hostname: (.*)', a.read()).group(1) + ">"
        commands = {'show task replication | no-more',
                    'show pim neighbors | no-more',
                    'show chassis fabric summary | no-more',
                    'show bgp summary logical-system all | no-more',
                    'show bgp summary logical-system all | no-more | m Establ',
                    'show bgp summary logical-system all | no-more | m Establ | count',
                    'show lacp interfaces | no-more',
                    'show chassis routing-engine | no-more',
                    'show chassis hardware| no-more',
                    'show chassis fpc | no-more',
                    'show interfaces descriptions | no-more',
                    'show interfaces descriptions | except down | no-more',
                    'show interfaces descriptions | except down | count',
                    'show isis adjacency | no-more',
                    'show chassis alarms | no-more',
                    'show rsvp session | no-more',
                    'show rsvp session | match total',
                    'show interfaces | match "rate|ge-|xe-|ae-|et-" | no-more',
                    'show route summary | no-more',
                    'show vpls connections | match rmt | match up | no-more',
                    'show vpls connections | match rmt | match up | count',
                    'show l2circuit connect | match rmt | match Up | count',
                    'show l2circuit connect | match rmt | match Up | no-more',
                    'show configuration | display set | count',
                    'show ldp session | no-more',
                    'show ldp session | count',
                    'show ldp neighbor | no-more',
                    'show ldp neighbor | count',
                    'show bfd session | no-more',
                    'show mpls lsp | no-more',
                    'show vrrp summary | no-more',
                    'show vpls mac-table | no-more',
                    'show vpls mac-table count',
                    'show system processes extensive | match rpd'}
        with open(os_path + '\\outputs_before_mw\\' + "show bgp summary logical-system all" + '.txt', "w") as a:
            with open(os_path + '\\outputs_before_mw\\' + "show interfaces descriptions" + '.txt', "w") as a:
                with open(os_path + '\\outputs_before_mw\\' + "show rsvp session" + '.txt', "w") as a:
                    with open(os_path + '\\outputs_before_mw\\' + "show vpls connections" + '.txt', "w") as a:
                        with open(os_path + '\\outputs_before_mw\\' + "show l2circuit connect" + '.txt', "w") as a:
                            with open(os_path + '\\outputs_before_mw\\' + "show ldp session" + '.txt', "w") as a:
                                with open(os_path + '\\outputs_before_mw\\' + "show ldp neighbor" + '.txt', "w") as a:
                                    with open(os_path + '\\outputs_before_mw\\' + "show vpls mac-table" + '.txt', "w") as a:
                                        with open(os_path + '\\outputs_before_mw\\' + "show chassis" + '.txt', "w") as a:
                                            for command in commands:
                                                result = ssh_to_router(command)
                                                if " | no-more" in command or "total" in command or "count" in command:
                                                    if "bgp" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show bgp summary logical-system all" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                            with open(os_path + '\\outputs_before_mw\\' + "show bgp summary" + '.txt', "w") as b:
                                                                b.write(hostname + "show bgp  logical-system all | no-more | m Establ" + "\n" + ssh_to_router('show bgp summary logical-system all | no-more | m Establ') + "\n" + hostname + "\n")
                                                    elif "interfaces descriptions" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show interfaces descriptions" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "rsvp session" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show rsvp session" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show interfaces | " in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show interfaces" + '.txt', "w") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show vpls connections" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show vpls connections" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show l2circuit connect" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show l2circuit connect" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show configuration | display set | count" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show configuration" + '.txt', "w") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show ldp session" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show ldp session" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show ldp neighbor" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show ldp neighbor" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show vpls mac-table" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show vpls mac-table" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "chassis" in command:
                                                        with open(os_path + '\\outputs_before_mw\\' + "show chassis" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    else:
                                                        with open(os_path + '\\outputs_before_mw\\' + command.replace(" | no-more", "") + '.txt', "w") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                else:
                                                    with open(os_path + '\\outputs_before_mw\\' + "show system processes extensive" + '.txt', "w") as a:
                                                        a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")

def collect_outputs_after_upgrade():
    with open(os_path + "\\ssh_connection.txt") as a:
        hostname = "@" + re.search('hostname: (.*)', a.read()).group(1) + ">"
        commands = {'show task replication | no-more',
                    'show pim neighbors | no-more',
                    'show chassis fabric summary | no-more',
                    'show bgp summary logical-system all | no-more',
                    'show bgp summary logical-system all | no-more | m Establ',
                    'show bgp summary logical-system all | no-more | m Establ | count',
                    'show lacp interfaces | no-more',
                    'show chassis routing-engine | no-more',
                    'show chassis hardware| no-more',
                    'show chassis fpc | no-more',
                    'show interfaces descriptions | no-more',
                    'show interfaces descriptions | except down | no-more',
                    'show interfaces descriptions | except down | count',
                    'show isis adjacency | no-more',
                    'show chassis alarms | no-more',
                    'show rsvp session | no-more',
                    'show rsvp session | match total',
                    'show interfaces | match "rate|ge-|xe-|ae-|et-" | no-more',
                    'show route summary | no-more',
                    'show vpls connections | match rmt | match up | no-more',
                    'show vpls connections | match rmt | match up | count',
                    'show l2circuit connect | match rmt | match Up | count',
                    'show l2circuit connect | match rmt | match Up | no-more',
                    'show configuration | display set | count',
                    'show ldp session | no-more',
                    'show ldp session | count',
                    'show ldp neighbor | no-more',
                    'show ldp neighbor | count',
                    'show bfd session | no-more',
                    'show mpls lsp | no-more',
                    'show vrrp summary | no-more',
                    'show vpls mac-table | no-more',
                    'show vpls mac-table count',
                    'show system processes extensive | match rpd'}
        with open(os_path + '\\outputs_after_mw\\' + "show bgp summary logical-system all" + '.txt', "w") as a:
            with open(os_path + '\\outputs_after_mw\\' + "show interfaces descriptions" + '.txt', "w") as a:
                with open(os_path + '\\outputs_after_mw\\' + "show rsvp session" + '.txt', "w") as a:
                    with open(os_path + '\\outputs_after_mw\\' + "show vpls connections" + '.txt', "w") as a:
                        with open(os_path + '\\outputs_after_mw\\' + "show l2circuit connect" + '.txt', "w") as a:
                            with open(os_path + '\\outputs_after_mw\\' + "show ldp session" + '.txt', "w") as a:
                                with open(os_path + '\\outputs_after_mw\\' + "show ldp neighbor" + '.txt', "w") as a:
                                    with open(os_path + '\\outputs_after_mw\\' + "show vpls mac-table" + '.txt', "w") as a:
                                        with open(os_path + '\\outputs_after_mw\\' + "show chassis" + '.txt', "w") as a:
                                            for command in commands:
                                                result = ssh_to_router(command)
                                                if " | no-more" in command or "total" in command or "count" in command:
                                                    if "bgp" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show bgp summary logical-system all" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                            with open(os_path + '\\outputs_after_mw\\' + "show bgp summary" + '.txt', "w") as b:
                                                                b.write(hostname + "show bgp  logical-system all | no-more | m Establ" + "\n" + ssh_to_router('show bgp summary logical-system all | no-more | m Establ') + "\n" + hostname + "\n")
                                                    elif "interfaces descriptions" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show interfaces descriptions" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "rsvp session" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show rsvp session" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show interfaces | " in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show interfaces" + '.txt', "w") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show vpls connections" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show vpls connections" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show l2circuit connect" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show l2circuit connect" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show configuration | display set | count" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show configuration" + '.txt', "w") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show ldp session" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show ldp session" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show ldp neighbor" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show ldp neighbor" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "show vpls mac-table" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show vpls mac-table" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    elif "chassis" in command:
                                                        with open(os_path + '\\outputs_after_mw\\' + "show chassis" + '.txt', "a") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                    else:
                                                        with open(os_path + '\\outputs_after_mw\\' + command.replace(" | no-more", "") + '.txt', "w") as a:
                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                else:
                                                    with open(os_path + '\\outputs_after_mw\\' + "show system processes extensive" + '.txt', "w") as a:
                                                        a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")

def summary():
    route_table = os_path + '\\tables\\route summary.csv'
    interface_state_table = os_path + '\\tables\\interface traffic.csv'
    interface_traffic_table = os_path + '\\tables\\interface traffic.csv'
    bgp_summary_table = os_path + '\\tables\\bgp summary.csv'
    bfd_table = os_path + '\\tables\\bfd.csv'
    isis_adjacency_table = os_path + '\\tables\\isis adjacency.csv'
    l2_circuit_table = os_path + '\\tables\\l2circuit.csv'
    ldp_neighbor_table = os_path + '\\tables\\ldp neighbor.csv'
    ldp_session_table = os_path + '\\tables\\ldp session.csv'
    with open(route_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "w") as a:
            if ">20%" in f.read():
                a.write("Статус маршрутов:     Not Ok\n")
            else:
                a.write("Статус маршрутов:     Ok\n")
    with open(interface_state_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("Статус интерфейсов:   Not Ok\n")
            else:
                a.write("Статус интерфейсов:   Ok\n")
    with open(interface_traffic_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if ">30%" in f.read():
                a.write("Трафик интерфейсов:   Not Ok\n")
            else:
                a.write("Трафик интерфейсов:   Ok\n")
    with open(bgp_summary_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("Статус BGP сессий:    Not Ok\n")
            else:
                a.write("Статус BGP сессий:    Ok\n")
    with open(bfd_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("Статус bfd сессий:    Not Ok\n")
            else:
                a.write("Статус bfd сессий:    Ok\n")
    with open(isis_adjacency_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("ISIS adjacency:       Not Ok\n")
            else:
                a.write("ISIS adjacency:       Ok\n")
    with open(l2_circuit_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write(":L2circuit            Not Ok\n")
            else:
                a.write("L2circuit:            Ok\n")
    with open(ldp_neighbor_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("Статус LDP neighbor:  Not Ok\n")
            else:
                a.write("Статус LDP neighbor:  Ok\n")
    with open(ldp_session_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("Статус LDP сессий:    Not Ok\n")
            else:
                a.write("Статус LDP сессий:    Ok\n")


def function():
    #filename = find_config(folder)
    if not "outputs_before_upgrade" in os.listdir(os_path):
        #create_show_bmw()
        create_outputs_bmw()
        collect_outputs_before_upgrade()
    else:
        create_outputs_amw()
        create_table()
        #collect_outputs_after_upgrade()
        #route_table()
        route_table_amw()
        interface_state_table_amw()
        interface_traffic_table_amw()
        bgp_summary_amw()
        bfd_amw()
        isis_adjacency_amw()
        l2circuit_amw()
        ldp_neighbor()
        ldp_session()
        dict_ingress_lsp()
        dict_egress_lsp()
        dict_transit_lsp()
        summary()
        #ssh_to_router()
        #diff_set_conf(filename, set_conf, diff_conf)
        #diff_del_conf(filename, del_conf, diff_conf)

function()
