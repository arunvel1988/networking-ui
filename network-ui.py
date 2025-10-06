from flask import Flask, render_template, request
import ipaddress
import math

app = Flask(__name__)

# Default classful mask
def get_default_mask(ip):
    first_octet = int(ip.split('.')[0])
    if 0 <= first_octet <= 127:
        return 8
    elif 128 <= first_octet <= 191:
        return 16
    elif 192 <= first_octet <= 223:
        return 24
    else:
        return 24

@app.route('/')
def home():
    return render_template('index.html')

# Normal calculation
@app.route('/calculate', methods=['POST'])
def calculate():
    ip_input = request.form['ip']
    mask_input = request.form.get('mask', '')

    mask = int(mask_input) if mask_input else get_default_mask(ip_input)

    try:
        network = ipaddress.ip_network(f"{ip_input}/{mask}", strict=False)
    except ValueError as e:
        return render_template('index.html', error=f"Invalid input: {e}")

    return render_template(
        'result.html',
        mode='normal',
        ip=ip_input,
        mask=mask,
        network_bits=network.prefixlen,
        host_bits=32-network.prefixlen,
        network_address=network.network_address,
        broadcast_address=network.broadcast_address,
        total_hosts=network.num_addresses-2 if network.num_addresses>2 else 0
    )

# Subnetting via Host
@app.route('/subnet_host', methods=['POST'])
def subnet_host():
    ip_input = request.form['ip']
    hosts = int(request.form['hosts'])
    mask_input = request.form.get('mask', '')
    mask = int(mask_input) if mask_input else get_default_mask(ip_input)

    try:
        network = ipaddress.ip_network(f"{ip_input}/{mask}", strict=False)
    except ValueError as e:
        return render_template('index.html', error=f"Invalid IP: {e}")

    required_bits = math.ceil(math.log2(hosts+2))
    new_prefix = 32 - required_bits
    subnets = list(network.subnets(new_prefix=new_prefix))

    subnet_info=[]
    for s in subnets:
        subnet_info.append({
            'network': s.network_address,
            'broadcast': s.broadcast_address,
            'start_ip': s.network_address+1 if s.num_addresses>2 else s.network_address,
            'end_ip': s.broadcast_address-1 if s.num_addresses>2 else s.broadcast_address,
            'prefix': s.prefixlen,
            'total_hosts': s.num_addresses-2 if s.num_addresses>2 else 0
        })

    return render_template('result.html',
                           mode='host',
                           ip=ip_input,
                           hosts=hosts,
                           required_bits=required_bits,
                           new_prefix=new_prefix,
                           subnets=subnet_info[:10],
                           total=len(subnets))

# Subnetting via Network
@app.route('/subnet_network', methods=['POST'])
def subnet_network():
    ip_input = request.form['ip']
    networks = int(request.form['networks'])
    mask_input = request.form.get('mask', '')
    mask = int(mask_input) if mask_input else get_default_mask(ip_input)

    try:
        network = ipaddress.ip_network(f"{ip_input}/{mask}", strict=False)
    except ValueError as e:
        return render_template('index.html', error=f"Invalid IP: {e}")

    bits_needed = math.ceil(math.log2(networks))
    new_prefix = network.prefixlen + bits_needed
    subnets = list(network.subnets(new_prefix=new_prefix))

    subnet_info=[]
    for s in subnets:
        subnet_info.append({
            'network': s.network_address,
            'broadcast': s.broadcast_address,
            'start_ip': s.network_address+1 if s.num_addresses>2 else s.network_address,
            'end_ip': s.broadcast_address-1 if s.num_addresses>2 else s.broadcast_address,
            'prefix': s.prefixlen,
            'total_hosts': s.num_addresses-2 if s.num_addresses>2 else 0
        })

    return render_template('result.html',
                           mode='network',
                           ip=ip_input,
                           networks=networks,
                           bits_needed=bits_needed,
                           new_prefix=new_prefix,
                           subnets=subnet_info[:10],
                           total=len(subnets))

# Supernetting for multiple networks
@app.route('/supernet', methods=['POST'])
def supernet():
    networks_input = request.form['networks_list']  # comma-separated networks
    networks_raw = [n.strip() for n in networks_input.split(',')]
    network_objs=[]
    try:
        for n in networks_raw:
            network_objs.append(ipaddress.ip_network(n, strict=False))
    except ValueError as e:
        return render_template('index.html', error=f"Invalid input: {e}")

    start_ip = min([n.network_address for n in network_objs])
    end_ip = max([n.broadcast_address for n in network_objs])
    supernet_list = list(ipaddress.summarize_address_range(start_ip,end_ip))

    return render_template('result.html',
                           mode='supernet',
                           supernet_list=supernet_list,
                           networks=networks_raw)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
