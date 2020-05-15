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
    'friches': {
        'path': './data/friches.geojson',
        'color': 'yellow',
        'prefix': '[friches] ',
        'opacity': 0.8
    },
    'icpe': {
        'path': './data/ICPE.geojson',
        'color': 'purple',
        'prefix': '[icpe] ',
        'opacity': 0.8
    },
    'zai': {
        'path': './data/ZAI.geojson',
        'color': 'green',
        'prefix': '[zai] ',
        'opacity': 0.2
    }
    # 'pig': {
    #     'path': './data/pig.geojson',
    #     'color': 'blue',
    #     'prefix': '[PIG] ',
    #     'opacity': 0.2
    # }
}

fond = {
    "positron": "https://cartodb-basemaps-c.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
    "ortho": "https://wxs.ign.fr/choisirgeoportail/geoportail/wmts?&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/jpeg&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}",
    "scan-express": "https://wxs.ign.fr/choisirgeoportail/geoportail/wmts?&REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/jpeg&LAYER=GEOGRAPHICALGRIDSYSTEMS.MAPS.SCAN-EXPRESS.STANDARD&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}",
    'opacity': 0.8
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

friches_json = compute_geojson(input_data["friches"],"act_friche","nom_friche")
icpe_json = compute_geojson(input_data["icpe"],"lib_naf","nom_ets")
zai_json = compute_geojson(input_data["zai"],"nature","toponyme")
# pig_json = compute_geojson(input_data["pig"],"OPERATEUR","NOM")


app.layout = html.Div([
    dl.Map(id='map',center=[49.3, 0], zoom=8, children=[
        dl.TileLayer(id='map_tile',url=fond["positron"],opacity=fond["opacity"]),
        dl.LayerGroup(id='zai',children=zai_json),
        # dl.LayerGroup(id='pig',children=pig_json),
        dl.LayerGroup(id='icpe',children=icpe_json),
        dl.LayerGroup(id='friches',children=friches_json)
    ],style={'width': '100%', 'height': '100%', 'position': 'absolute','opacity':0.9}),
    html.Div([
        html.Div([
            html.P('Fonds carto : '),
            dcc.RadioItems(id='fond_carto',
                options=[{'label': 'Positron', 'value': 'positron'},{'label': 'Ortho', 'value': 'ortho'}, {'label': 'Scan Express', 'value': 'scan-express'} ],
                value='positron', labelStyle={'display': 'block'}
            )
        ]),
        # html.Div([
        #     html.P('Inondations : '),
        #     dcc.Checklist(
        #         id='inondation', options=[{'label': 'EAIP sm', 'value': 'EAIPsm'},{'label': 'EAIP ce', 'value': 'EAIPce'}],
        #         value=[], labelStyle={'display': 'block'}
        #     ),
        # ]),
        html.Div([
            html.P('Zones : '),
            dcc.Checklist(
                id='donnees', options=[{'label': 'icpe', 'value': 'icpe'},{'label': 'friches', 'value': 'friches'},{'label': 'zai', 'value': 'zai'},{'label': 'PIG', 'value': 'PIG'}],
                value=['friches', 'icpe'], labelStyle={'display': 'block'}
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
        dl.LayerGroup(id='zai',children=zai_json) if "zai" in donnees else '',
        # dl.LayerGroup(id='pig',children=pig_json) if "PIG" in donnees else '',
        dl.LayerGroup(id='icpe',children=icpe_json) if "icpe" in donnees else '',
        dl.LayerGroup(id='friches',children=friches_json) if "friches" in donnees else '']
    ]


if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False,dev_tools_hot_reload=False)

