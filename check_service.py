import os
import re
import csv
from netmiko import ConnectHandler

os_path = os.path.dirname(os.path.abspath('check_serv.py'))

def create_outputs_before_upgrade():
    directory = os_path + '\\outputs_before_upgrade'
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_outputs_after_upgrade():
    directory = os_path + '\\outputs_after_upgrade'
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_table():
    directory = os_path + '\\tables'
    if not os.path.exists(directory):
        os.makedirs(directory)

def dict_route_table():
    regex = ('(.*): \d+ destinations, (\d+) routes')
    dict = {}
    with open(os_path + '\\outputs_before_upgrade\\show route summary.txt') as a:
        for line in a:
            match = re.finditer(regex, line)
            if "inet" in line:
                if match:
                    for m in match:
                        name = m.group(1)
                        routes = m.group(2)
                        dict[name] = routes
    return dict

def route_table():
    regex = ('(.*): \d+ destinations, (\d+) routes')
    route_table = os_path + '\\tables\\route summary.csv'
    with open(route_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["vpn_name", "routes_before", "routes_after", "diff", "summary"])
        with open(os_path + '\\outputs_after_upgrade\\show route summary.txt') as a:
            for line in a:
                match = re.finditer(regex, line)
                if "inet" in line:
                    if match:
                        for m in match:
                            name = m.group(1)
                            routes = m.group(2)
                            if (name == k for k in dict_route_table().keys()):
                                diff = round((1-(int(routes)+1)/(int((dict_route_table()[name]))+1))*100)
                                if int(str(diff).strip("%")) > 20:
                                    result = ">20%"
                                else:
                                    result = ""
                                writer.writerow([name] + [dict_route_table()[name]] + [routes] + [str(diff)+"%"] + [result])

def dict_interfaces_state():
    regex = ('Physical interface: (.*), .*, Physical link is (.*)\n'
             '  Input rate     : .* bps .*\n'
             '  Output rate    : .* bps .*')
    dict = {}
    with open(os_path + '\\outputs_before_upgrade\\show interfaces.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return dict

def dict_interfaces_traffic_in():
    regex = ('Physical interface: (.*), .*, Physical link is .*\n'
             '  Input rate     : (.*) bps .*\n'
             '  Output rate    : .* bps .*')
    dict = {}
    with open(os_path + '\\outputs_before_upgrade\\show interfaces.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                in_traffic = m.group(2)
                dict[name] = {in_traffic}
    return dict

def dict_interfaces_traffic_out():
    regex = ('Physical interface: (.*), .*, Physical link is .*\n'
             '  Input rate     : .* bps .*\n'
             '  Output rate    : (.*) bps .*')
    dict = {}
    with open(os_path + '\\outputs_before_upgrade\\show interfaces.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                out_traffic = m.group(2)
                dict[name] = {out_traffic}
    return dict

def interface_state():
    regex = ('Physical interface: (.*), .*, Physical link is (.*)\n'
             '  Input rate     : .* bps .*\n'
             '  Output rate    : .* bps .*')
    dict = {}
    interface_state_table = os_path + '\\tables\\interface state.csv'
    with open(interface_state_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interfaces_name", "state_before", "state_after", "summary"])
        with open(os_path + '\\outputs_after_upgrade\\show interfaces.txt') as a:
            match = re.finditer(regex, a.read())
            if match:
                for m in match:
                    name = m.group(1)
                    state = m.group(2)
                    dict[name] = {state}
                    if (name == k for k in dict_interfaces_state().keys()):
                        state_before = str(dict_interfaces_state()[name]).replace("{'", "").replace("'}", "")
                        if state_before == state:
                            result = "Ok"
                        else:
                            result = "Not Ok"
                        writer.writerow([name] + [state_before] + [state] + [result])

def interface_traffic():
    regex = ('Physical interface: (.*), .*, Physical link is .*\n'
             '  Input rate     : (.*) bps .*\n'
             '  Output rate    : (.*) bps .*')
    dict = {}
    interface_traffic_table = os_path + '\\tables\\interface traffic.csv'
    with open(interface_traffic_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interfaces_name", "traffic_in_before", "traffic_in_after", "diff", "summary", "traffic_out_before", "traffic_out_after", "diff", "summary"])
        with open(os_path + '\\outputs_after_upgrade\\show interfaces.txt') as a:
            match = re.finditer(regex, a.read())
            if match:
                for m in match:
                    name = m.group(1)
                    in_traffic = m.group(2)
                    out_traffic = m.group(3)
                    dict[name] = {in_traffic, out_traffic}
                    if (name == k for k in dict_interfaces_traffic_in().keys()):
                        traffic_in_before = str(dict_interfaces_traffic_in()[name]).replace("{'", "").replace("'}", "")
                        traffic_out_before = str(dict_interfaces_traffic_out()[name]).replace("{'", "").replace("'}", "")
                        try:
                            diff_in_traffic = round((1-(int(in_traffic))/(int(traffic_in_before)))*100)
                        except ZeroDivisionError:
                            diff_in_traffic = 0
                        try:
                            diff_out_traffic = round((1-(int(out_traffic))/(int(traffic_out_before)))*100)
                        except ZeroDivisionError:
                            diff_out_traffic = 0
                        if diff_in_traffic > 30:
                            result_in_traffic = ">30%"
                        elif diff_in_traffic <= 30:
                            result_in_traffic = ""
                        if diff_out_traffic > 30:
                            result_out_traffic = ">30%"
                        elif diff_out_traffic <= 30:
                            result_out_traffic = ""
                        writer.writerow([name] + [traffic_in_before] + [in_traffic] + [str(diff_in_traffic) + "%"] + [result_in_traffic] + [traffic_out_before] + [out_traffic] + [str(diff_out_traffic) + "%"] + [result_out_traffic])

def bgp_summary():
    regex = ('(\S+)\s+\d+\s+\d+\s+\d+.*\n')
    bgp_summary_table = os_path + '\\tables\\bgp summary.csv'
    with open(bgp_summary_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["neighbor", "summary"])
        with open(os_path + '\\outputs_before_upgrade\\show bgp summary.txt') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                with open(os_path + '\\outputs_after_upgrade\\show bgp summary.txt') as b:
                    if (name + " ") in b.read():
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [result])

def dict_bfd():
    regex = ('(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\d+\s+\n')
    dict = {}
    with open(os_path + '\\outputs_before_upgrade\\show bfd session.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return dict

def bfd():
    regex = ('(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\d+\s+\n')
    bfd_table = os_path + '\\tables\\bfd.csv'
    with open(bfd_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["neighbor", "state_before", "state_after", "summary"])
        with open(os_path + '\\outputs_after_upgrade\\show bfd session.txt') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                state = m.group(2)
                if (name == k for k in dict_bfd().keys()):
                    state_before = str(dict_bfd()[name]).replace("{'", "").replace("'}", "")
                    if state_before == state:
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [state_before] + [state] + [result])

def dict_isis_name():
    regex = ('(\S+)\s+(\S+)\s+\d+\s+\S+\s+\d+\n')
    dict = {}
    with open(os_path + '\\outputs_before_upgrade\\show isis adjacency.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                neighbor = m.group(2)
                dict[name] = {neighbor}
    return dict

def dict_isis_state():
    regex = ('(\S+)\s+\S+\s+\d+\s+(\S+)\s+\d+\n')
    dict = {}
    with open(os_path + '\\outputs_before_upgrade\\show isis adjacency.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return dict

def isis_adjacency():
    regex = ('(\S+)\s+(\S+)\s+\d+\s+(\S+)\s+\d+\n')
    isis_adjacency_table = os_path + '\\tables\\isis adjacency.csv'
    with open(isis_adjacency_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interface", "neighbor", "state_before", "state_after", "summary"])
        with open(os_path + '\\outputs_after_upgrade\\show isis adjacency.txt') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                neighbor = m.group(2)
                state = m.group(3)
                if (name == k for k in dict_isis_name().keys()):
                    state_before = str(dict_isis_state()[name]).replace("{'", "").replace("'}", "")
                    if state_before == state:
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [neighbor] + [state_before] + [state] + [result])

def dict_l2circuit():
    regex = ('\s+(\S+\(vc\s+\d+\))\s+\S+\s+(\S+).*')
    dict = {}
    with open(os_path + '\\outputs_before_upgrade\\show l2circuit connect.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return dict

def l2circuit():
    regex = ('\s+(\S+\(vc\s+\d+\))\s+\S+\s+(\S+).*')
    l2_circuit_table = os_path + '\\tables\\l2circuit.csv'
    with open(l2_circuit_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interface", "state_before", "state_after", "summary"])
        with open(os_path + '\\outputs_after_upgrade\\show l2circuit connect.txt') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                state = m.group(2)
                if (name == k for k in dict_l2circuit().keys()):
                    state_before = str(dict_l2circuit()[name]).replace("{'", "").replace("'}", "")
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
        with open(os_path + '\\outputs_before_upgrade\\show ldp neighbor.txt') as b:
            match = re.finditer(regex, b.read())
            for m in match:
                name = m.group(1)
                with open(os_path + '\\outputs_after_upgrade\\show ldp neighbor.txt') as a:
                    if (name + " ") in a.read():
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [result])

def dict_ldp_session():
    regex = ('(\S+)\s+(\S+)\s+\S+\s+\d+\s+\S+\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show ldp session.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                name = m.group(1)
                state = m.group(2)
                dict[name] = {state}
    return dict

def ldp_session():
    regex = ('(\S+)\s+(\S+)\s+\S+\s+\d+\s+\S+\n')
    ldp_session_table = os_path + '\\tables\\ldp session.csv'
    with open(ldp_session_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["address", "state_before", "state_after", "summary"])
        with open(os_path + '\\outputs_before_upgrade\\show ldp session.txt') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                name = m.group(1)
                state = m.group(2)
                if (name in dict_ldp_session().keys()):
                    state_after = str(dict_ldp_session()[name]).replace("{'", "").replace("'}", "")
                    if state_after == state:
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([name] + [state] + [state_after] + [result])
                else:
                    writer.writerow([name] + [state] + [""] + ["Not Ok"])

def list_mpls_lsp_ingress_before():
    list = []
    with open(os_path + '\\outputs_before_upgrade\\show mpls lsp.txt') as a:
        for n, line in enumerate(a):
            if "Ingress" in line:
                start = n+1
                list.append(start)
            elif "Egress" in line:
                end = n-2
                list.append(end)
    return list
def list_mpls_lsp_egress_before():
    list = []
    with open(os_path + '\\outputs_before_upgrade\\show mpls lsp.txt') as a:
        for n, line in enumerate(a):
            if "Egress" in line:
                start = n+1
                list.append(start)
            elif "Transit" in line:
                end = n-2
                list.append(end)
    return list
def list_mpls_lsp_transit_before():
    with open(os_path + '\\outputs_before_upgrade\\show mpls lsp.txt') as a:
        for n, line in enumerate(a):
            if "Transit" in line:
                start = n+1
    return start

def list_mpls_lsp_ingress_after():
    list = []
    with open(os_path + '\\outputs_after_upgrade\\show mpls lsp.txt') as a:
        for n, line in enumerate(a):
            if "Ingress" in line:
                start = n+1
                list.append(start)
            elif "Egress" in line:
                end = n-2
                list.append(end)
    return list

def list_mpls_lsp_egress_after():
    list = []
    with open(os_path + '\\outputs_after_upgrade\\show mpls lsp.txt') as a:
        for n, line in enumerate(a):
            if "Egress" in line:
                start = n+1
                list.append(start)
            elif "Transit" in line:
                end = n-2
                list.append(end)
    return list

def list_mpls_lsp_transit_after():
    with open(os_path + '\\outputs_after_upgrade\\show mpls lsp.txt') as a:
        for n, line in enumerate(a):
            if "Transit" in line:
                start = n+1
    return start

def dict_mpls_lsp_ingress_after():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\S+)\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show mpls lsp.txt') as a:
        for n, line in enumerate(a):
            if n > list_mpls_lsp_ingress_after()[0] and n < list_mpls_lsp_ingress_after()[1]:
                to = re.search(regex, line).group(1)
                state = re.search(regex, line).group(3)
                dict[to] = state
    return dict

def dict_mpls_lsp_egress_after():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show mpls lsp.txt') as a:
        for n, line in enumerate(a):
            if n > list_mpls_lsp_egress_after()[0] and n < list_mpls_lsp_egress_after()[1]:
                from_ip = re.search(regex, line).group(2)
                state = re.search(regex, line).group(3)
                dict[from_ip] = state
    return dict

def dict_mpls_lsp_transit_after():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show mpls lsp.txt') as a:
        for n, line in enumerate(a):
            if n > list_mpls_lsp_transit_after() and ("." in line):
                state = re.search(regex, line).group(3)
                name = re.search(regex, line).group(4)
                dict[name] = state
    return dict

def mpls_lsp_ingress():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\S+)\n')
    mpls_lsp_table = os_path + '\\tables\\mpls lsp.csv'
    with open(os_path + '\\outputs_before_upgrade\\show mpls lsp.txt') as a:
            with open(mpls_lsp_table, "w", newline='') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["to", "from", "state_before", "state_after", "summary"])
                writer.writerow(["Ingress"])
                for n, line in enumerate(a):
                    if n > list_mpls_lsp_ingress_before()[0] and n < list_mpls_lsp_ingress_before()[1]:
                        to = re.search(regex, line).group(1)
                        from_ip = re.search(regex, line).group(2)
                        state = re.search(regex, line).group(3)
                        if to in dict_mpls_lsp_ingress_after().keys():
                            state_after = str(dict_mpls_lsp_ingress_after()[to]).replace("{'", "").replace("'}", "")
                            if state_after == state:
                                result = "Ok"
                            else:
                                result = "Not Ok"
                            writer.writerow([to] + [from_ip] + [state] + [state_after] + [result])
                        else:
                            writer.writerow([to] + [from_ip] + [state] + [""] + ["Not Ok"])

def mpls_lsp_egress():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    mpls_lsp_table = os_path + '\\tables\\mpls lsp.csv'
    with open(os_path + '\\outputs_before_upgrade\\show mpls lsp.txt') as a:
            with open(mpls_lsp_table, "a", newline='') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Egress"])
                for n, line in enumerate(a):
                    if n > list_mpls_lsp_egress_before()[0] and n < list_mpls_lsp_egress_before()[1]:
                        to = re.search(regex, line).group(1)
                        from_ip = re.search(regex, line).group(2)
                        state = re.search(regex, line).group(3)
                        if from_ip in dict_mpls_lsp_egress_after().keys():
                            state_after = str(dict_mpls_lsp_egress_after()[from_ip]).replace("{'", "").replace("'}", "")
                            if state_after == state:
                                result = "Ok"
                            else:
                                result = "Not Ok"
                            writer.writerow([from_ip] + [to] + [state] + [state_after] + [result])
                        else:
                            writer.writerow([from_ip] + [to] + [state] + [""] + ["Not Ok"])

def mpls_lsp_transit():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    mpls_lsp_table = os_path + '\\tables\\mpls lsp.csv'
    with open(os_path + '\\outputs_before_upgrade\\show mpls lsp.txt') as a:
            with open(mpls_lsp_table, "a", newline='') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Transit"])
                for n, line in enumerate(a):
                    if n > list_mpls_lsp_transit_before() and ("." in line):
                        to = re.search(regex, line).group(1)
                        from_ip = re.search(regex, line).group(2)
                        state = re.search(regex, line).group(3)
                        name = re.search(regex, line).group(4)
                        if name in dict_mpls_lsp_transit_after().keys():
                            state_after = str(dict_mpls_lsp_transit_after()[name]).replace("{'", "").replace("'}", "")
                            if state_after == state:
                                result = "Ok"
                            else:
                                result = "Not Ok"
                            writer.writerow([from_ip] + [to] + [state] + [state_after] + [result])
                        else:
                            writer.writerow([from_ip] + [to] + [state] + [""] + ["Not Ok"])

def list_rsvp_ingress_before():
    list = []
    with open(os_path + '\\outputs_before_upgrade\\show rsvp session.txt') as a:
        for n, line in enumerate(a):
            if "Ingress" in line:
                start = n+1
                list.append(start)
            elif "Egress" in line:
                end = n-2
                list.append(end)
    return list

def list_rsvp_egress_before():
    list = []
    with open(os_path + '\\outputs_before_upgrade\\show rsvp session.txt') as a:
        for n, line in enumerate(a):
            if "Egress" in line:
                start = n+1
                list.append(start)
            elif "Transit" in line:
                end = n-2
                list.append(end)
    return list

def list_rsvp_transit_before():
    with open(os_path + '\\outputs_before_upgrade\\show rsvp session.txt') as a:
        for n, line in enumerate(a):
            if "Transit" in line:
                start = n+1
    return start

def list_rsvp_ingress_after():
    list = []
    with open(os_path + '\\outputs_after_upgrade\\show rsvp session.txt') as a:
        for n, line in enumerate(a):
            if "Ingress" in line:
                start = n+1
                list.append(start)
            elif "Egress" in line:
                end = n-2
                list.append(end)
    return list

def list_rsvp_egress_after():
    list = []
    with open(os_path + '\\outputs_after_upgrade\\show rsvp session.txt') as a:
        for n, line in enumerate(a):
            if "Egress" in line:
                start = n+1
                list.append(start)
            elif "Transit" in line:
                end = n-2
                list.append(end)
    return list

def list_rsvp_transit_after():
    with open(os_path + '\\outputs_after_upgrade\\show rsvp session.txt') as a:
        for n, line in enumerate(a):
            if "Transit" in line:
                start = n+1
    return start

def dict_rsvp_ingress_after():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show rsvp session.txt') as a:
        for n, line in enumerate(a):
            if n > list_rsvp_ingress_after()[0] and n < list_rsvp_ingress_after()[1]:
                to = re.search(regex, line).group(1)
                state = re.search(regex, line).group(3)
                dict[to] = state
    return dict

def dict_rsvp_egress_after():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show rsvp session.txt') as a:
        for n, line in enumerate(a):
            if n > list_rsvp_egress_after()[0] and n < list_rsvp_egress_after()[1]:
                from_ip = re.search(regex, line).group(2)
                state = re.search(regex, line).group(3)
                dict[from_ip] = state
    return dict

def dict_rsvp_transit_after():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show rsvp session.txt') as a:
        for n, line in enumerate(a):
            if n > list_rsvp_transit_after() and ("." in line):
                state = re.search(regex, line).group(3)
                name = re.search(regex, line).group(4)
                dict[name] = state
    return dict

def rsvp_ingress():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    rsvp_table = os_path + '\\tables\\rsvp.csv'
    with open(os_path + '\\outputs_before_upgrade\\show rsvp session.txt') as a:
            with open(rsvp_table, "w", newline='') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["to", "from", "state_before", "state_after", "summary"])
                writer.writerow(["Ingress"])
                for n, line in enumerate(a):
                    if n > list_rsvp_ingress_before()[0] and n < list_rsvp_ingress_before()[1]:
                        to = re.search(regex, line).group(1)
                        from_ip = re.search(regex, line).group(2)
                        state = re.search(regex, line).group(3)
                        if to in dict_rsvp_ingress_after().keys():
                            state_after = str(dict_rsvp_ingress_after()[to]).replace("{'", "").replace("'}", "")
                            if state_after == state:
                                result = "Ok"
                            else:
                                result = "Not Ok"
                            writer.writerow([to] + [from_ip] + [state] + [state_after] + [result])
                        else:
                            writer.writerow([to] + [from_ip] + [state] + [""] + ["Not Ok"])

def rsvp_egress():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    rsvp_table = os_path + '\\tables\\rsvp.csv'
    with open(os_path + '\\outputs_before_upgrade\\show rsvp session.txt') as a:
            with open(rsvp_table, "a", newline='') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Egress"])
                for n, line in enumerate(a):
                    if n > list_rsvp_egress_before()[0] and n < list_rsvp_egress_before()[1]:
                        to = re.search(regex, line).group(1)
                        from_ip = re.search(regex, line).group(2)
                        state = re.search(regex, line).group(3)
                        if from_ip in dict_rsvp_egress_after().keys():
                            state_after = str(dict_rsvp_egress_after()[from_ip]).replace("{'", "").replace("'}", "")
                            if state_after == state:
                                result = "Ok"
                            else:
                                result = "Not Ok"
                            writer.writerow([from_ip] + [to] + [state] + [state_after] + [result])
                        else:
                            writer.writerow([from_ip] + [to] + [state] + [""] + ["Not Ok"])

def rsvp_transit():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\n')
    rsvp_table = os_path + '\\tables\\rsvp.csv'
    with open(os_path + '\\outputs_before_upgrade\\show rsvp session.txt') as a:
            with open(rsvp_table, "a", newline='') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Transit"])
                for n, line in enumerate(a):
                    if n > list_rsvp_transit_before() and ("." in line):
                        to = re.search(regex, line).group(1)
                        from_ip = re.search(regex, line).group(2)
                        state = re.search(regex, line).group(3)
                        name = re.search(regex, line).group(4)
                        if name in dict_rsvp_transit_after().keys():
                            state_after = str(dict_rsvp_transit_after()[name]).replace("{'", "").replace("'}", "")
                            if state_after == state:
                                result = "Ok"
                            else:
                                result = "Not Ok"
                            writer.writerow([from_ip] + [to] + [state] + [state_after] + [result])
                        else:
                            writer.writerow([from_ip] + [to] + [state] + [""] + ["Not Ok"])

def dict_vrrp_interface():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\d+.\d+.\d+.\d+)\s+\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show vrrp summary.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                ip = m.group(5)
                interface = m.group(1)
                dict[ip] = {interface}
    return dict

def dict_vrrp_state():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\d+.\d+.\d+.\d+)\s+\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show vrrp summary.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                ip = m.group(5)
                state = m.group(2)
                dict[ip] = {state}
    return dict

def dict_vrrp_group():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\d+.\d+.\d+.\d+)\s+\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show vrrp summary.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                ip = m.group(5)
                group = m.group(3)
                dict[ip] = {group}
    return dict

def dict_vrrp_vr_state():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\d+.\d+.\d+.\d+)\s+\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show vrrp summary.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                ip = m.group(5)
                vr_state = m.group(4)
                dict[ip] = {vr_state}
    return dict

def vrrp():
    regex = ('(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+(\d+.\d+.\d+.\d+)\s+\n')
    vrrp_table = os_path + '\\tables\\vrrp.csv'
    with open(vrrp_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["interface", "group", "state_before", "state_after", "state_summary", "vr_state_before", "vr_state_after", "vr_state_summary"])
        with open(os_path + '\\outputs_before_upgrade\\show vrrp summary.txt') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                interface = m.group(1)
                state = m.group(2)
                group = m.group(3)
                vr_state = m.group(4)
                ip = m.group(5)
                if (ip in dict_vrrp_interface().keys()):
                    state_after = str(dict_vrrp_state()[ip]).replace("{'", "").replace("'}", "")
                    vr_state_after = str(dict_vrrp_vr_state()[ip]).replace("{'", "").replace("'}", "")
                    if state_after == state:
                        result_state = "Ok"
                    elif not state_after == state:
                        result_state = "Not Ok"
                    if vr_state_after == vr_state:
                        result_vr_state = "Ok"
                    elif not vr_state_after == vr_state:
                        result_vr_state = "Not Ok"
                    writer.writerow([interface] + [group] + [state] + [state_after] + [result_state] + [vr_state] + [vr_state_after] + [result_vr_state])
                else:
                    writer.writerow([interface] + [group] + [state] + [""] + ["Not Ok"] + [vr_state] + [""] + ["Not Ok"])

def dict_vpls_state():
    regex = ('    (.*)\s+rmt\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show vpls connections.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                id = m.group(1)
                state = m.group(2)
                dict[id] = {state}
    return dict

def vpls_connection():
    regex = ('    (.*)\s+rmt\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\n')
    vpls_state_table = os_path + '\\tables\\vpls state.csv'
    with open(vpls_state_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["id", "state_before", "state_after", "state_summary"])
        with open(os_path + '\\outputs_before_upgrade\\show vpls connections.txt') as a:
            match = re.finditer(regex, a.read())
            for m in match:
                id = m.group(1)
                state = m.group(2)
                if id in dict_vpls_state().keys():
                    state_after = str(dict_vpls_state()[id]).replace("{'", "").replace("'}", "")
                    if state_after == state:
                        result = "Ok"
                    else:
                        result = "Not Ok"
                    writer.writerow([id] + [state] + [state_after] + [result])
                else:
                    writer.writerow([id] + [state] + [""] + ["Not Ok"])

def dict_vpls_mac_table():
    regex = ('(\d+) MAC address learned in routing instance (\S+) bridge domain .*\n')
    dict = {}
    with open(os_path + '\\outputs_after_upgrade\\show vpls mac-table.txt') as a:
        match = re.finditer(regex, a.read())
        if match:
            for m in match:
                count_mac = m.group(1)
                name = m.group(2)
                dict[name] = count_mac
    return dict

def vpls_mac_table():
    regex = ('(\d+) MAC address learned in routing instance (\S+) bridge domain .*\n')
    vpls_mac_table = os_path + '\\tables\\vpls mac table.csv'
    with open(vpls_mac_table, "w", newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["vpls_instance", "mac_count_before", "mac_count_after", "diff", "summary"])
        with open(os_path + '\\outputs_after_upgrade\\show vpls mac-table.txt') as a:
            for line in a:
                match = re.finditer(regex, line)
                if match:
                    for m in match:
                        count_mac = m.group(1)
                        name = m.group(2)
                        if (name == k for k in dict_vpls_mac_table().keys()):
                            diff = round((1-(int(count_mac)+1)/(int((dict_vpls_mac_table()[name]))+1))*100)
                            if int(str(diff).strip("%")) > 30:
                                result = ">30%"
                            else:
                                result = ""
                            writer.writerow([name] + [dict_vpls_mac_table()[name]] + [count_mac] + [str(diff)+"%"] + [result])
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
                    'show lacp interfaces | match "Collecting distributing" | count',
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
                    'show bfd session | match up | count',
                    'show mpls lsp | no-more',
                    'show mpls lsp | match total',
                    'show vrrp summary | no-more',
                    'show vrrp summary | match Active | count',
                    'show vpls mac-table | no-more',
                    'show vpls mac-table count',
                    'show system processes extensive | match rpd'}
        with open(os_path + '\\outputs_before_upgrade\\' + "show bgp summary logical-system all" + '.txt', "w") as a:
            with open(os_path + '\\outputs_before_upgrade\\' + "show lacp interfaces" + '.txt', "w") as a:
                with open(os_path + '\\outputs_before_upgrade\\' + "show interfaces descriptions" + '.txt', "w") as a:
                    with open(os_path + '\\outputs_before_upgrade\\' + "show rsvp session" + '.txt', "w") as a:
                        with open(os_path + '\\outputs_before_upgrade\\' + "show vpls connections" + '.txt', "w") as a:
                            with open(os_path + '\\outputs_before_upgrade\\' + "show l2circuit connect" + '.txt', "w") as a:
                                with open(os_path + '\\outputs_before_upgrade\\' + "show ldp session" + '.txt', "w") as a:
                                    with open(os_path + '\\outputs_before_upgrade\\' + "show ldp neighbor" + '.txt', "w") as a:
                                        with open(os_path + '\\outputs_before_upgrade\\' + "show bfd session" + '.txt', "w") as a:
                                            with open(os_path + '\\outputs_before_upgrade\\' + "show mpls lsp" + '.txt', "w") as a:
                                                with open(os_path + '\\outputs_before_upgrade\\' + "show vrrp summary" + '.txt', "w") as a:
                                                    with open(os_path + '\\outputs_before_upgrade\\' + "show vpls mac-table" + '.txt', "w") as a:
                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show chassis" + '.txt', "w") as a:
                                                            for command in commands:
                                                                result = ssh_to_router(command)
                                                                if " | no-more" in command or "total" in command or "count" in command:
                                                                    if "bgp" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show bgp summary logical-system all" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                            with open(os_path + '\\outputs_before_upgrade\\' + "show bgp summary" + '.txt', "w") as b:
                                                                                b.write(hostname + "show bgp logical-system all | no-more | m Establ" + "\n" + ssh_to_router('show bgp summary logical-system all | no-more | m Establ') + "\n" + hostname + "\n")
                                                                    elif "show lacp interfaces" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show lacp interfaces" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "interfaces descriptions" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show interfaces descriptions" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "rsvp session" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show rsvp session" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show interfaces | " in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show interfaces" + '.txt', "w") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show vpls connections" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show vpls connections" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show l2circuit connect" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show l2circuit connect" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show configuration | display set | count" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show configuration" + '.txt', "w") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show ldp session" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show ldp session" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show ldp neighbor" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show ldp neighbor" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show bfd session" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show bfd session" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show mpls lsp" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show mpls lsp" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show vrrp" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show vrrp summary" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show vpls mac-table" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show vpls mac-table" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "chassis" in command:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + "show chassis" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    else:
                                                                        with open(os_path + '\\outputs_before_upgrade\\' + command.replace(" | no-more", "") + '.txt', "w") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                else:
                                                                    with open(os_path + '\\outputs_before_upgrade\\' + "show system processes extensive" + '.txt', "w") as a:
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
                    'show lacp interfaces | match "Collecting distributing" | count',
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
                    'show interfaces diagnostics optics | no-more',
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
                    'show bfd session | match up | no-more',
                    'show bfd session | match up | count',
                    'show mpls lsp | no-more',
                    'show mpls lsp | match total | no-more',
                    'show vrrp summary | no-more',
                    'show vrrp summary | match Active | count',
                    'show vpls mac-table | no-more',
                    'show vpls mac-table count',
                    'show system processes extensive | match rpd'}
        with open(os_path + '\\outputs_after_upgrade\\' + "show bgp summary logical-system all" + '.txt', "w") as a:
            with open(os_path + '\\outputs_after_upgrade\\' + "show lacp interfaces" + '.txt', "w") as a:
                with open(os_path + '\\outputs_after_upgrade\\' + "show interfaces descriptions" + '.txt', "w") as a:
                    with open(os_path + '\\outputs_after_upgrade\\' + "show rsvp session" + '.txt', "w") as a:
                        with open(os_path + '\\outputs_after_upgrade\\' + "show vpls connections" + '.txt', "w") as a:
                            with open(os_path + '\\outputs_after_upgrade\\' + "show l2circuit connect" + '.txt', "w") as a:
                                with open(os_path + '\\outputs_after_upgrade\\' + "show ldp session" + '.txt', "w") as a:
                                    with open(os_path + '\\outputs_after_upgrade\\' + "show ldp neighbor" + '.txt', "w") as a:
                                        with open(os_path + '\\outputs_after_upgrade\\' + "show bfd session" + '.txt', "w") as a:
                                            with open(os_path + '\\outputs_after_upgrade\\' + "show mpls lsp" + '.txt', "w") as a:
                                                with open(os_path + '\\outputs_after_upgrade\\' + "show vrrp summary" + '.txt', "w") as a:
                                                    with open(os_path + '\\outputs_after_upgrade\\' + "show vpls mac-table" + '.txt', "w") as a:
                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show chassis" + '.txt', "w") as a:
                                                            for command in commands:
                                                                result = ssh_to_router(command)
                                                                if " | no-more" in command or "total" in command or "count" in command:
                                                                    if "bgp" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show bgp summary logical-system all" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                            with open(os_path + '\\outputs_after_upgrade\\' + "show bgp summary" + '.txt', "w") as b:
                                                                                b.write(hostname + "show bgp logical-system all | no-more | m Establ" + "\n" + ssh_to_router('show bgp summary logical-system all | no-more | m Establ') + "\n" + hostname + "\n")
                                                                    elif "show lacp interfaces" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show lacp interfaces" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "interfaces descriptions" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show interfaces descriptions" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "rsvp session" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show rsvp session" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show interfaces | " in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show interfaces" + '.txt', "w") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show vpls connections" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show vpls connections" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show l2circuit connect" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show l2circuit connect" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show configuration | display set | count" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show configuration" + '.txt', "w") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show ldp session" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show ldp session" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show ldp neighbor" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show ldp neighbor" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show bfd session" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show bfd session" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show mpls lsp" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show mpls lsp" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show vrrp" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show vrrp summary" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "show vpls mac-table" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show vpls mac-table" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    elif "chassis" in command:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + "show chassis" + '.txt', "a") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                    else:
                                                                        with open(os_path + '\\outputs_after_upgrade\\' + command.replace(" | no-more", "") + '.txt', "w") as a:
                                                                            a.write(hostname + command + "\n" + result + "\n" + hostname + "\n")
                                                                else:
                                                                    with open(os_path + '\\outputs_after_upgrade\\' + "show system processes extensive" + '.txt', "w") as a:
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
    mpls_lsp_table = os_path + '\\tables\\mpls lsp.csv'
    rsvp_table = os_path + '\\tables\\rsvp.csv'
    vrrp_table = os_path + '\\tables\\vrrp.csv'
    vpls_state_table = os_path + '\\tables\\vpls state.csv'
    vpls_mac_table = os_path + '\\tables\\vpls mac table.csv'
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
    with open(mpls_lsp_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("Статус MPLS LSP:      Not Ok\n")
            else:
                a.write("Статус MPLS LSP:      Ok\n")
    with open(rsvp_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("Статус RSVP:          Not Ok\n")
            else:
                a.write("Статус RSVP:          Ok\n")
    with open(vrrp_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            list_vrrp_state = []
            list_vrrp_vr_state = []
            for line in f:
                list_vrrp_state.append(line.split(";")[4])
                list_vrrp_vr_state.append(line.split(";")[7].replace("\r\n", ""))
                if "Not Ok" in list_vrrp_state:
                    vrrp_state = "Not Ok"
                elif not "Not Ok" in list_vrrp_state:
                    vrrp_state = "Ok"
                if "Not Ok" in list_vrrp_vr_state:
                    vrrp_vr_state = "Not Ok"
                elif not "Not Ok" in list_vrrp_vr_state:
                    vrrp_vr_state = "Ok"
            a.write("Статус VRRP:          " + vrrp_state + "\n")
            a.write("VRRP Master/Backup:   " + vrrp_vr_state + "\n")
    with open(vpls_state_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("Статус VPLS:          Not Ok\n")
            else:
                a.write("Статус VPLS:          Ok\n")
    with open(vpls_mac_table, "r", newline='') as f:
        with open(os_path + '\\tables\\summary.txt', "a") as a:
            if "Not Ok" in f.read():
                a.write("VPLS MAC-table:       Not Ok\n")
            else:
                a.write("VPLS MAC-table:       Ok\n")

def function():
    if not "outputs_before_upgrade" in os.listdir(os_path):
        create_outputs_before_upgrade()
        collect_outputs_before_upgrade()
    else:
        create_outputs_after_upgrade()
        create_table()
        collect_outputs_after_upgrade()
        route_table()
        interface_state()
        interface_traffic()
        bgp_summary()
        bfd()
        isis_adjacency()
        l2circuit()
        ldp_neighbor()
        ldp_session()
        mpls_lsp_ingress()
        mpls_lsp_egress()
        mpls_lsp_transit()
        rsvp_ingress()
        rsvp_egress()
        rsvp_transit()
        vrrp()
        vpls_connection()
        vpls_mac_table()
        summary()

function()
