import pandas as pd
import plotly.express as px

historical_data_cee = pd.read_csv('./cee_historical_data.csv')
cee_3y = historical_data_cee[(historical_data_cee.index >= '01/01/2020') & (historical_data_cee.index < '01/10/2023')]

fig = px.line(cee_3y, 
              x=cee_3y.index, 
              y="Prix Moyen pondéré (en €/MWh)", 
              color='Type CEE',
              color_discrete_map={
                 "Classique": "#456987",
                 "Précarité": "#147852"
             })

fig.update_layout(
    xaxis=dict(
        showline=True,
        showgrid=False,
        showticklabels=True,
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=False,
        showticklabels=False,
    ),
    autosize=False,
    width=1000,
    height=600,
    margin=dict(
        autoexpand=False,
        l=100,
        r=20,
        t=110,
    ),
    showlegend=False,
    plot_bgcolor='white'
)

fig.update_layout(annotations=[dict(xref='paper', yref='paper', x=0.0, y=1.05,
                              xanchor='left', yanchor='bottom',
                              text='Prix pondéré des CEE',
                              font=dict(family='Arial',
                                        size=30,
                                        color='rgb(37,37,37)'),
                              showarrow=False),
                              dict(xref='paper', yref='paper', x=0.5, y=-0.13,
                              xanchor='center', yanchor='top',
                              text='Gaël PENESSOT - Data Decision | Source : EMMY (https://www.emmy.fr)',
                              font=dict(family='Arial',
                                        size=12,
                                        color='rgb(150,150,150)'),
                              showarrow=False)])

fig.write_image("prix_cee.png") 