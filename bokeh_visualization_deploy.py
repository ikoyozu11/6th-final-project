import os
import pandas as pd
from collections import Counter
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Select, Slider, Div, TabPanel, Tabs, HoverTool, Panel
from bokeh.layouts import column, row
from bokeh.io import curdoc

# Load dataset
df = pd.read_csv("survey_results_public_2023.csv")

# Preprocessing
df_viz = df[['Country', 'YearsCodePro', 'ConvertedCompYearly', 'LanguageHaveWorkedWith', 'RemoteWork', 'DevType']].dropna()
df_viz = df_viz[df_viz['YearsCodePro'].apply(lambda x: str(x).isdigit())]
df_viz['YearsCodePro'] = df_viz['YearsCodePro'].astype(int)
df_viz = df_viz[df_viz['ConvertedCompYearly'] < 500000]

# Top countries
top_countries = df_viz['Country'].value_counts().head(5).index.tolist()
initial_country = top_countries[0]

# Widget
country_select = Select(title="Pilih Negara:", value=initial_country, options=top_countries, width=300)
remote_options = sorted(df_viz['RemoteWork'].dropna().unique().tolist())
remote_filter = Select(title="Pilih Preferensi Kerja:", value=remote_options[0] if remote_options else '', options=remote_options, width=300)
slider_years = Slider(start=0, end=30, value=5, step=1, title="Pilih Tahun Pengalaman", width=300)

# VISUAL 1
remote_fig = figure(height=500, width=900, title="", x_range=[])
remote_src = ColumnDataSource(data=dict(x=[], y=[]))
remote_fig.vbar(x='x', top='y', source=remote_src, width=0.5)

def update_remote(c):
    data = filter_by_devtype(df_viz[df_viz['Country'] == c], devtype_select.value)
    counts = data['RemoteWork'].value_counts()
    remote_src.data = dict(x=counts.index.tolist(), y=counts.values)
    remote_fig.x_range.factors = counts.index.tolist()
    remote_fig.title.text = f"Jumlah Programmer Berdasarkan Preferensi Kerja di {c}"

# VISUAL 2: Bahasa Populer (dengan filter remote work)
lang_fig = figure(height=500, width=900, title="", x_range=[])
lang_src = ColumnDataSource(data=dict(x=[], y=[]))
lang_fig.vbar(x='x', top='y', source=lang_src, width=0.5)
lang_fig.xaxis.major_label_orientation = 1.2

def update_language(c, r):
    data = filter_by_devtype(df_viz[(df_viz['Country'] == c) & (df_viz['RemoteWork'] == r)], devtype_select.value)
    langs = data['LanguageHaveWorkedWith'].str.split(";")
    flat = [l.strip() for sub in langs for l in sub]
    counts = Counter(flat)
    top = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True)[:10])
    lang_src.data = dict(x=list(top.keys()), y=list(top.values()))
    lang_fig.x_range.factors = list(top.keys())
    lang_fig.title.text = f"Bahasa Pemrograman Terpopuler Berdasarkan Preferensi Kerja di {c} ({r})"

# VISUAL 3
scatter_fig = figure(height=500, width=900, title="", x_axis_label="Tahun Pengalaman", y_axis_label="Gaji")
scatter_src = ColumnDataSource(data=dict(YearsCodePro=[], ConvertedCompYearly=[]))
scatter_fig.circle('YearsCodePro', 'ConvertedCompYearly', source=scatter_src, size=5, alpha=0.3)

def update_scatter(c, y):
    data = filter_by_devtype(df_viz[(df_viz['Country'] == c) & (df_viz['YearsCodePro'] >= y)], devtype_select.value)
    if len(data) == 0:
        scatter_src.data = dict(YearsCodePro=[], ConvertedCompYearly=[])
        scatter_fig.title.text = f"Tidak ada data untuk {c} dengan ≥{y} tahun pengalaman"
    else:
        sample = data.sample(min(1000, len(data)), random_state=42)
        scatter_src.data = sample[['YearsCodePro', 'ConvertedCompYearly']].to_dict('list')
        scatter_fig.title.text = f"Keterkaitan Gaji Dengan Pengalaman Kerja Programmer di {c} (≥ {y} tahun)"


# Dropdown DevType (Tipe Developer)
devtypes = df_viz['DevType'].dropna().str.split(';').explode().str.strip()
top_devtypes = devtypes.value_counts().head(6).index.tolist()
top_devtypes.insert(0, "Semua")  # opsi semua
devtype_select = Select(title="Pilih Tipe Developer:", value="Semua", options=top_devtypes, width=300)



def filter_by_devtype(data, devtype):
    if devtype == "Semua":
        return data
    return data[data['DevType'].str.contains(devtype, na=False)]


# Tambahkan kolom kelompok pengalaman ke df_viz
bins = [0, 5, 10, 15, 20, 25, 30, 50]
labels = ['0-5', '6-10', '11-15', '16-20', '21-25', '26-30', '30+']
df_viz['exp_group'] = pd.cut(df_viz['YearsCodePro'], bins=bins, labels=labels, right=True)

# VISUAL 4: Line Plot Preferensi vs Pengalaman
line_fig = figure(height=500, width=900, title="", x_range=labels)
line_src = ColumnDataSource(data=dict(exp_group=[], hybrid=[], in_person=[], remote=[]))

line_fig.line(x='exp_group', y='hybrid', source=line_src, color='orange', legend_label='Hybrid', line_width=2)
line_fig.line(x='exp_group', y='in_person', source=line_src, color='red', legend_label='In-person', line_width=2)
line_fig.line(x='exp_group', y='remote', source=line_src, color='green', legend_label='Remote', line_width=2)

line_fig.scatter(x='exp_group', y='hybrid', source=line_src, size=6, color='orange')
line_fig.scatter(x='exp_group', y='in_person', source=line_src, size=6, color='red')
line_fig.scatter(x='exp_group', y='remote', source=line_src, size=6, color='green')

line_fig.legend.location = "top_left"

hover_line = HoverTool(tooltips=[
    ("Kelompok", "@exp_group"),
    ("Remote", "@remote{0.0%}"),
    ("Hybrid", "@hybrid{0.0%}"),
    ("In-person", "@in_person{0.0%}")
])
line_fig.add_tools(hover_line)
line_fig.title.text_font_size = "10pt"

line_fig.legend.click_policy = "hide"
line_fig.title.text_font_size = "10pt"
line_fig.xaxis.axis_label = "Kelompok Tahun Pengalaman"
line_fig.yaxis.axis_label = "Proporsi Preferensi Kerja"

def update_line(c):
    data = filter_by_devtype(df_viz[df_viz['Country'] == c], devtype_select.value)
    if data.empty:
        line_src.data = dict(exp_group=[], hybrid=[], in_person=[], remote=[])
        line_fig.title.text = f"Tidak ada data tren preferensi di {c}"
        return

    pivot = data.pivot_table(index='exp_group', columns='RemoteWork', aggfunc='size', fill_value=0)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0).reset_index()

    line_src.data = dict(
        exp_group=pivot_pct['exp_group'].astype(str).tolist(),
        hybrid=pivot_pct.get("Hybrid (some remote, some in-person)", [0]*len(pivot_pct)).tolist(),
        in_person=pivot_pct.get("In-person", [0]*len(pivot_pct)).tolist(),
        remote=pivot_pct.get("Remote", [0]*len(pivot_pct)).tolist()
    )
    line_fig.title.text = f"Preferensi Kerja Berdasarkan Tahun Pengalaman ({c})"

# Update semua visual
def update_all(attr, old, new):
    update_line(country_select.value)
    d = devtype_select.value
    c = country_select.value
    r = remote_filter.value
    y = slider_years.value
    update_remote(c)
    update_language(c, r)
    update_scatter(c, y)

country_select.on_change("value", update_all)
remote_filter.on_change("value", update_all)
slider_years.on_change("value", update_all)
update_all(None, None, None)

header = Div(text="""
<div style='padding:20px 30px; border-radius:12px;
            text-align:center; margin:0 auto 30px auto; max-width:900px;'>
    <h1 style='margin-bottom:5px;'>📊 Mini Dashboard Developer StackOverflow 2023</h1>
    <p style='margin:0;'>Visualisasi interaktif: tipe developer, negara, preferensi kerja, bahasa populer, tahun pengalaman dan gaji</p>
</div>
""")

curdoc().title = "Mini Dashboard StackOverflow"

hover = HoverTool(tooltips=[
    ("Pengalaman", "@YearsCodePro tahun"),
    ("Gaji", "@ConvertedCompYearly{$0,0}")
])
scatter_fig.add_tools(hover)

remote_fig.add_tools(HoverTool(tooltips=[("Mode", "@x"), ("Jumlah", "@y")]))
lang_fig.add_tools(HoverTool(tooltips=[("Bahasa", "@x"), ("Jumlah", "@y")]))


tab1 = TabPanel(title="Preferensi Kerja", child=remote_fig)
tab2 = TabPanel(title="Bahasa Populer", child=lang_fig)
tab3 = TabPanel(title="Gaji vs Pengalaman", child=scatter_fig)
tab4 = TabPanel(title="Preferensi Kerja vs Pengalaman", child=line_fig)
tabs = Tabs(tabs=[tab1, tab2, tab3, tab4], sizing_mode="stretch_width")

layout = column(
    header,
    row(devtype_select, country_select, remote_filter, sizing_mode="stretch_width"),
    slider_years,
    tabs,
    sizing_mode="stretch_width"
)

curdoc().add_root(layout)

devtype_select.on_change("value", update_all)