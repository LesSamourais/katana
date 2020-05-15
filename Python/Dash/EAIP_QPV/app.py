# coding: utf8
#!/usr/bin/python3

import flask
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_leaflet as dl
import json


############
# Paramètres

input_data = {
    'qpv': {
        'path': './data/qpv.geojson',
        'color': 'yellow',
        'prefix': '[QPV] ',
        'opacity': 0.8
    },
    'cucs': {
        'path': './data/cucs.geojson',
        'color': 'purple',
        'prefix': '[CUCS] ',
        'opacity': 0.8
    },
    'opah': {
        'path': './data/opah.geojson',
        'color': 'green',
        'prefix': '[OPAH] ',
        'opacity': 0.2
    },
    'pig': {
        'path': './data/pig.geojson',
        'color': 'blue',
        'prefix': '[PIG] ',
        'opacity': 0.2
    }
}

fond = {
    "positron": "https://cartodb-basemaps-c.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
    "ortho": "https://wxs.ign.fr/choisirgeoportail/geoportail/wmts?&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/jpeg&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}",
    "scan-express": "https://wxs.ign.fr/choisirgeoportail/geoportail/wmts?&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/jpeg&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.STANDARD&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}",
    'opacity': 0.8
}

wms = {
    "eaipsm": {
        'url': "https://mapsref.brgm.fr/wxs/georisques/risques", 
        'layers': 'EAIP_SM',
        'format': 'image/png',
        'transparent': True,
        'opacity': 0.4
    },
    "eaipce": {
        'url': "https://mapsref.brgm.fr/wxs/georisques/risques", 
        'layers': 'EAIP_CE',
        'format': 'image/png',
        'transparent': True,
        'opacity': 0.4
    }
}


###########
# Fonctions

def compute_geojson(gjson,commune,quartier):
    geojson = json.load(open(gjson["path"],encoding='utf8'))
    data = [
        dl.Polygon(
            positions=[list(reversed(q)) for p in feat['geometry']['coordinates'] for q in p],
            children=[
                dl.Tooltip(gjson["prefix"] + str(feat['properties'][commune]) + " : " + str(feat['properties'][quartier])),
                dl.Popup([html.P(k + " : " + str(v)) for k,v in feat["properties"].items()])
            ], color=gjson["color"], weight=0.1, fillOpacity=gjson["opacity"], stroke=True
        ) for feat in geojson['features']
    ]

    return data


#########
### Main
#########

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

qpv_json = compute_geojson(input_data["qpv"],"COMMUNE_QP","NOM_QP")
cucs_json = compute_geojson(input_data["cucs"],"COMMUNES","QUARTIER")
opah_json = compute_geojson(input_data["opah"],"OPERATEUR","NOM")
pig_json = compute_geojson(input_data["pig"],"OPERATEUR","NOM")


app.layout = html.Div([
    dl.Map(id='map',center=[49.3, 0], zoom=8, children=[
        dl.TileLayer(id='map_tile',url=fond["positron"],opacity=fond["opacity"]),
        dl.WMSTileLayer(id='eaipce',url='',layers=''),
        dl.WMSTileLayer(id='eaipsm',url='',layers=''),
        dl.LayerGroup(id='opah',children=opah_json),
        dl.LayerGroup(id='pig',children=pig_json),
        dl.LayerGroup(id='cucs',children=cucs_json),
        dl.LayerGroup(id='qpv',children=qpv_json)
    ],style={'width': '100%', 'height': '100%', 'position': 'absolute','opacity':0.9}),
    html.Div([
        html.Div([
            html.P('Fonds carto : '),
            dcc.RadioItems(id='fond_carto',
                options=[{'label': 'Positron', 'value': 'positron'},{'label': 'Ortho', 'value': 'ortho'}, {'label': 'Scan Express', 'value': 'scan-express'} ],
                value='positron', labelStyle={'display': 'block'}
            )
        ]),
        html.Div([
            html.P('Inondations : '),
            dcc.Checklist(
                id='inondation', options=[{'label': 'EAIP sm', 'value': 'EAIPsm'},{'label': 'EAIP ce', 'value': 'EAIPce'}],
                value=[], labelStyle={'display': 'block'}
            ),
        ]),
        html.Div([
            html.P('Ville : '),
            dcc.Checklist(
                id='donnees', options=[{'label': 'CUCS', 'value': 'CUCS'},{'label': 'QPV', 'value': 'QPV'},{'label': 'OPAH', 'value': 'OPAH'},{'label': 'PIG', 'value': 'PIG'}],
                value=['QPV', 'CUCS'], labelStyle={'display': 'block'}
            ),
        ]),
    ],
    style={'width': 'auto', 'border': '1px solid', 'padding': '7px','background-color':'white', 'border-radius':'25px','top':10,'right':10,'display': 'inline-block','position':'absolute'})
])


##########
# Callback

@app.callback(
    [Output('map','children')],
    [Input('inondation','value'),Input('donnees','value'),Input('fond_carto','value')]
)
def showLayer(inondation,donnees,fond_carto):
    return [
        [dl.TileLayer(id='map_tile',url=fond[fond_carto],opacity=fond["opacity"]),
        dl.WMSTileLayer(id='eaipce',url=wms["eaipce"]["url"],layers=wms["eaipce"]["layers"],format=wms["eaipce"]["format"],transparent=wms["eaipce"]["transparent"],opacity=wms["eaipce"]["opacity"]) if "EAIPce" in inondation else '',
        dl.WMSTileLayer(id='eaipsm',url=wms["eaipsm"]["url"],layers=wms["eaipsm"]["layers"],format=wms["eaipsm"]["format"],transparent=wms["eaipsm"]["transparent"],opacity=wms["eaipsm"]["opacity"]) if "EAIPsm" in inondation else '',
        dl.LayerGroup(id='opah',children=opah_json) if "OPAH" in donnees else '',
        dl.LayerGroup(id='pig',children=pig_json) if "PIG" in donnees else '',
        dl.LayerGroup(id='cucs',children=cucs_json) if "CUCS" in donnees else '',
        dl.LayerGroup(id='qpv',children=qpv_json) if "QPV" in donnees else '']
    ]


if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False,dev_tools_hot_reload=False)

