#!/usr/bin/env python3

import urllib.request
import json

nodes_url = 'http://127.0.0.1:8079/nodes.json'
graph_url = 'http://127.0.0.1:8079/graph.json'
nodes_out = '/var/www/api/nodes.json'
graph_out = '/var/www/api/graph.json'

if __name__ == '__main__':
    nodes_content = None
    with urllib.request.urlopen( nodes_url ) as f:
        nodes_content = f.read()

    nodes_data = json.loads( nodes_content.decode() )

    for node in nodes_data['nodes'].items():
        try:
            location = node[1]['nodeinfo']['location']
            longitude = location['longitude']
            latitude = location['latitude']

            # Let's assume Germany is a rect. ;-)
            if ( latitude  < 47.070122
              or latitude  > 55.565922
              or longitude <  5.515137 
              or longitude > 15.161133 ):
                del node[1]['nodeinfo']['location']
        except KeyError:
            pass
    
    with open( nodes_out, 'w' ) as f:
        f.write( json.dumps( nodes_data )+'\n' )

    # Finally, load graph.json
    with urllib.request.urlopen( graph_url ) as f_in:
        with open( graph_out, 'w' ) as f_out:
            f_out.write( f_in.read().decode()+'\n' )
