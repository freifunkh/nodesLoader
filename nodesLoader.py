#!/usr/bin/env python3

import urllib.request
import json
import datetime
import os.path

nodes_url = 'http://127.0.0.1:8079/nodes.json'
graph_url = 'http://127.0.0.1:8079/graph.json'
nodes_out = '/var/www/api/nodes.json'
graph_out = '/var/www/api/graph.json'
summary_out = '/var/www/api/summary.json'
history_out = '/var/www/api/history.csv'
history_threshold_time = 3600
history_lines = 168

summary = dict(
    nodes_online=0,
    clients_online=0
)

if __name__ == '__main__':
    nodes_content = None
    with urllib.request.urlopen( nodes_url ) as f:
        nodes_content = f.read()

    nodes_data = json.loads( nodes_content.decode() )

    for node in nodes_data['nodes'].items():
        try:
            if node[1]['flags']['online']:
                summary['nodes_online'] += 1
                summary['clients_online'] += node[1]['statistics']['clients']
        except KeyError:
            pass

        try: # Two try blocks so an empty location doesn't stop the script from counting the node
            location = node[1]['nodeinfo']['location']
            longitude = location['longitude']
            latitude = location['latitude']

            # Let's assume Europe is a rect. ;-)
            if ( latitude  <  34.30
              or latitude  >  71.85
              or longitude < -24.96
              or longitude >  39.72 ):
                del node[1]['nodeinfo']['location']
        except KeyError:
            pass

    with open( nodes_out, 'w' ) as f:
        f.write( json.dumps( nodes_data )+'\n' )

    with open(summary_out, 'w') as f:
        f.write(json.dumps(summary) + '\n')

    # history of the last 7 days (hourly)
    now = datetime.datetime.now()
    if os.path.getmtime( history_out ) + history_threshold_time < now.timestamp():
        history = []
        with open( history_out, 'r' ) as f:
            history = f.readlines()
            history.append( now.strftime('%Y-%m-%d %H:%M;') + str(summary['nodes_online']) + ';' + str(summary['clients_online']) + '\n' )
        with open( history_out, 'w' ) as f:
            f.writelines( history[(-1*history_lines):] )

    # Finally, load graph.json
    with urllib.request.urlopen( graph_url ) as f_in:
        with open( graph_out, 'w' ) as f_out:
            f_out.write( f_in.read().decode()+'\n' )
