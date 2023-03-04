import altair as alt
import pandas as pd

def balancesheet(data, filter, total_label, orient='left', reverse=True, offset=5):
    selection_click = alt.selection_multi(fields=['position_name'], toggle=True, name="selection_click")
    selection_legend = alt.selection(type='multi', fields=['position_name'], bind='legend',  name='selection_legend')
    position_dropdown = alt.binding_select(
    options=[None] + list(data.moneyness.unique()), labels = ['Alle Positionen'] + list(data.moneyness.unique()), name="Positionen ")
    position_selection = alt.selection_single(fields=['moneyness'], bind=position_dropdown)
    bars = alt.Chart(data).transform_filter(
    alt.FieldOneOfPredicate(field='position_id', oneOf=filter)
    ).transform_filter(
        position_selection
    ).transform_calculate( 
        order=f"indexof({selection_legend.name}.position_name || {selection_click.name}.position_name || [], datum.position_name)"
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': 'Value_1'}],
        groupby = ['position_id']
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': 'Value_3'}],
        groupby = ['position_id']
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': 'Value_12'}],
        groupby = ['position_id']
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': 'Value_120'}],
        groupby = ['position_id']
    ).transform_window(
        Total='sum(Value)',
        groupby=['Date'],
        frame=[None, None]
    ).transform_calculate(
        MoM = (alt.datum.Value - alt.datum.Value_1) / alt.datum.Value_1,
        QoQ = (alt.datum.Value - alt.datum.Value_3) / alt.datum.Value_3,
        YoY = (alt.datum.Value - alt.datum.Value_12) / alt.datum.Value_12,
        Yo10Y = (alt.datum.Value - alt.datum.Value_120) / alt.datum.Value_120,
        Share = alt.datum.Value / alt.datum.Total
    ).mark_bar(
    ).encode(
        alt.X('Value:Q',
        scale=alt.Scale(reverse=reverse, domainMin=0), axis=alt.Axis(orient='top', title=None, ticks=True, tickSize=10, tickColor='#e6eaf1')),
        alt.Y('Date:O',
        scale=alt.Scale(reverse=True,), axis=alt.Axis(orient=orient, title=None)),
        order=alt.Order("order:N", sort='descending'),
        opacity=alt.condition(selection_click | selection_legend, alt.value(1), alt.value(0.2)),    
        color=alt.Color('position_name:N', sort=filter, legend=alt.Legend(title=" ", orient="top")),
        tooltip=[alt.Tooltip('Date:O', title='Datum'), alt.Tooltip('position_name', title='Position'), alt.Tooltip('Value:Q', format=',.0f', title='Wert'), alt.Tooltip('Share:Q', format='.1%', title='Anteil'), alt.Tooltip('MoM:Q', format='.1%'), alt.Tooltip('QoQ:Q', format='.1%'), alt.Tooltip('YoY:Q', format='.1%'), alt.Tooltip('Yo10Y:Q', format='.1%')]
    ).add_selection(
        selection_click, selection_legend 
    )

    total = alt.Chart(data).transform_filter(
        alt.FieldOneOfPredicate(field='position_id', oneOf=filter)
    ).transform_filter(
        position_selection
    ).transform_window(
        Total='sum(Value)',
        groupby=['Date'],
        frame=[None, None]
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Total', 'param': 1, 'as': 'Total_1'}],
        groupby = ['position_id']
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Total', 'param': 3, 'as': 'Total_3'}],
        groupby = ['position_id']
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Total', 'param': 12, 'as': 'Total_12'}],
        groupby = ['position_id']
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Total', 'param': 120, 'as': 'Total_120'}],
        groupby = ['position_id']
    ).transform_calculate(
        MoM = (alt.datum.Total - alt.datum.Total_1) / alt.datum.Total_1,
        QoQ = (alt.datum.Total - alt.datum.Total_3) / alt.datum.Total_3,
        YoY = (alt.datum.Total - alt.datum.Total_12) / alt.datum.Total_12,
        Yo10Y = (alt.datum.Total - alt.datum.Total_120) / alt.datum.Total_120,
        Share = alt.datum.Total / alt.datum.Total,
        Total_label = "isValid(datum['Total_label']) ? datum['Total_label'] : 'Summe'"
    ).mark_tick(
        color='black',
        thickness=3
    ).encode(
        x='Total:Q',
        y='Date:O',
        tooltip=[alt.Tooltip('Date:O', title='Datum'), alt.Tooltip('Total_label:N', title='Position'), alt.Tooltip('Total:Q', format=',.0f', title='Wert'), alt.Tooltip('Share:Q', format='.1%', title='Anteil'), alt.Tooltip('MoM:Q', format='.1%'), alt.Tooltip('QoQ:Q', format='.1%'), alt.Tooltip('YoY:Q', format='.1%'), alt.Tooltip('Yo10Y:Q', format='.1%')]
    )

    chart = (bars + total).add_selection(
        position_selection
    ).configure_legend(orient="top",
        direction='horizontal',
        columns=3,
        offset=offset,
        labelLimit=0,
        labelFontSize=10,
        columnPadding=10, 
    )

    return chart

def flow(data, filter, orient='left', reverse=True, offset=5):
    position_dropdown = alt.binding_select(
    options=[None] + list(data.moneyness.unique()), labels = ['Alle Positionen'] + list(data.moneyness.unique()), name="Positionen ")
    position_selection = alt.selection_single(fields=['moneyness'], bind=position_dropdown)

    bars = alt.Chart(data).transform_filter(
        alt.FieldOneOfPredicate(field='position_id', oneOf=filter)
    ).transform_calculate( 
        order=f"indexof({filter}, datum.position_id)"
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': 'Value_1'}],
        groupby = ['position_id']
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Value', 'param': 3, 'as': 'Value_3'}],
        groupby = ['position_id']
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Value', 'param': 12, 'as': 'Value_12'}],
        groupby = ['position_id']
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Value', 'param': 120, 'as': 'Value_120'}],
        groupby = ['position_id']
    ).transform_window(
        Total='sum(Value)',
        groupby=['Date'],
        frame=[None, None]
    ).transform_calculate(
        Flow = alt.datum.Value - alt.datum.Value_1,
        MoM = (alt.datum.Value - alt.datum.Value_1) / alt.datum.Value_1,
        QoQ = (alt.datum.Value - alt.datum.Value_3) / alt.datum.Value_3,
        YoY = (alt.datum.Value - alt.datum.Value_12) / alt.datum.Value_12,
        Yo10Y = (alt.datum.Value - alt.datum.Value_120) / alt.datum.Value_120,
        Share = alt.datum.Value / alt.datum.Total
        
    ).mark_bar(
    ).encode(
        alt.X('Flow:Q',
        scale = alt.Scale(reverse=reverse, domain=[-200000, 200000]), axis=alt.Axis(orient='top', title=None , ticks=True, tickSize=10, tickColor='#e6eaf1')),
        alt.Y('Date:O',
        scale=alt.Scale(reverse=True), axis=alt.Axis(orient='right', title=None)),
        color=alt.Color('position_name:N', sort=filter, legend=alt.Legend(title=" ", orient="top")),
        order='order:O',
        tooltip=[alt.Tooltip('Date:O', title='Datum'), alt.Tooltip('position_name', title='Position'), alt.Tooltip('Flow:Q', format=',.0f', title='Wert')]
    ).transform_filter(
        position_selection
    )

    total = alt.Chart(data).transform_filter(
        alt.FieldOneOfPredicate(field='position_id', oneOf=filter)
    ).transform_filter(
        position_selection
    ).transform_window(
        window = [{'op': 'lag', 'field': 'Value', 'param': 1, 'as': 'Value_1'}],
        groupby = ['position_id']
    ).transform_calculate(
        Flow = alt.datum.Value - alt.datum.Value_1,
        Total_label = "isValid(datum['Total_label']) ? datum['Total_label'] : 'Summe'"
    ).transform_window(
        Total='sum(Flow)',
        groupby=['Date'],
        frame=[None, None]
    ).mark_tick(
        color='black',
        thickness=3
    ).encode(
        x='Total:Q',
        y='Date:O',
        tooltip=[alt.Tooltip('Date:O', title='Datum'), alt.Tooltip('Total_label:N' , title='Position'), alt.Tooltip('Total:Q', format=',.0f', title='Wert')]
    )

    chart = alt.layer(bars, total, data=data).add_selection(
        position_selection
    ).configure_legend(orient="top",
        direction='horizontal',
        columns=3,
        offset=offset,
        labelLimit=0,
        labelFontSize=10,
        columnPadding=10, 
    )

    return chart