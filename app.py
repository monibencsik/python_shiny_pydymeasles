import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shiny import App, ui, render, reactive

cases_month = pd.read_csv(
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-06-24/cases_month.csv"
)

measles = cases_month[
    [
        "region",
        "country",
        "iso3",
        "year",
        "month",
        "measles_suspect",
        "measles_clinical",
        "measles_epi_linked",
        "measles_lab_confirmed",
        "measles_total",
    ]
]

rubella = cases_month[
    [
        "region", 
        "country", 
        "iso3", 
        "year", 
        "month", 
        "rubella_clinical", 
        "rubella_epi_linked", 
        "rubella_lab_confirmed", 
        "rubella_total"
    ]
]

measles_cols_to_plot = [
    "measles_suspect",
    "measles_clinical",
    "measles_epi_linked",
    "measles_lab_confirmed",
    "measles_total",
]

rubella_cols_to_plot = [
    "rubella_clinical", 
    "rubella_epi_linked", 
    "rubella_lab_confirmed", 
    "rubella_total"
]


measles_region_sum = measles.groupby("region", as_index=False)[measles_cols_to_plot].sum()
rubella_region_sum = rubella.groupby("region", as_index=False)[rubella_cols_to_plot].sum()

measles_year_sum = measles.groupby("year", as_index=False)[measles_cols_to_plot].sum()
rubella_year_sum = rubella.groupby("year", as_index=False)[rubella_cols_to_plot].sum()

year_min = int(cases_month['year'].min())
year_max = int(cases_month['year'].max())

css_styles = """
table {
    width: 100% !important;
    table-layout: fixed !important;
}
th, td {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
.dataframe-container {
    overflow-x: auto;
    width: 100%;
    height: auto;
}
"""

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons(
            "disease_type",
            "Select Disease:",
            choices={"measles": "Measles", "rubella": "Rubella"},
            selected="measles"
        ),
        ui.input_selectize(
            "disease_column",
            "Select metric:",
            choices=[], 
            selected=None,
        ),
        ui.hr(),
        ui.input_slider(
            "year_range",
            "Year Range:",
            min=year_min,
            max=year_max,
            value=[year_min, year_max],
            step=1,
            sep=""
        ),
        width=200
    ),
    ui.tags.style(css_styles),
    ui.markdown(
        """
        #### About this analysis

        The aim of this project is to visualise the WHO Diseases dataset from 2012-2025 for the submission of the #PyDyTuesday 
        """
    ),
    ui.hr(),
    ui.h3(ui.output_text("plot_title")),
    
    ui.layout_columns(
        ui.card(
            ui.card_header("Cases by Region"),
            ui.output_plot("region_barplot"),
        ),
        ui.card(
            ui.card_header("Cases by Year"),
            ui.output_plot("year_barplot"),
        ),
        col_widths=[6, 6]
    ),
    
    ui.h3("Explanation of features:"),
    ui.div(ui.output_data_frame("show_disease_plot_metadata"), class_="dataframe-container"),
)


def server(input, output, session):
    @reactive.effect
    def _():
        disease = input.disease_type()
        if disease == "measles":
            choices = measles_cols_to_plot
        else:
            choices = rubella_cols_to_plot
        
        ui.update_selectize(
            "disease_column", 
            choices=choices, 
            selected=choices[0]
        )
    
    @output
    @render.text
    def plot_title():
        disease = input.disease_type()
        return f"{disease.capitalize()} cases analysis"
    
    @output
    @render.plot(width=600, height=400)
    def region_barplot():
        disease = input.disease_type()
        disease_column = input.disease_column()
        
        if not disease_column: 
            return plt.figure()
        
        if disease == "measles":
            data = measles_region_sum
        else:
            data = rubella_region_sum
            
        fig, ax = plt.subplots()
        sns.barplot(data=data, x="region", y=disease_column, ax=ax)
        plt.ticklabel_format(style="plain", axis="y")
        for container in ax.containers:
            ax.bar_label(container, labels=[f"{v.get_height():.0f}" for v in container], padding=3)
        plt.title(f"{disease_column} by region")
        plt.tight_layout()
        return fig

    @output
    @render.plot(width=600, height=400)
    def year_barplot():
        disease = input.disease_type()
        disease_column = input.disease_column()
        year_range = input.year_range()
        
        if not disease_column:
            return plt.figure()
        
        if disease == "measles":
            data = measles_year_sum
        else:
            data = rubella_year_sum
        
        filtered_data = data[(data['year'] >= year_range[0]) & (data['year'] <= year_range[1])]
            
        fig, ax = plt.subplots()
        sns.barplot(data=filtered_data, x="year", y=disease_column, ax=ax)
        plt.ticklabel_format(style="plain", axis="y")
        for container in ax.containers:
            ax.bar_label(container, labels=[f"{v.get_height():.0f}" for v in container], padding=3)
        plt.title(f"{disease_column} by year ({year_range[0]}-{year_range[1]})")
        plt.tight_layout()
        return fig

    @output
    @render.data_frame
    def show_disease_plot_metadata():
        disease = input.disease_type()
        
        if disease == "measles":
            return pd.DataFrame(
                {
                    "feature": measles_cols_to_plot,
                    "explanation": [
                        "Suspected measles cases: A suspected case is one in which a patient with fever and maculopapular (non-vesicular) rash, or in whom a health-care worker suspects measles",
                        "Clinically-compatible measles cases: A suspected case with fever and maculopapular (non-vesicular) rash and at least one of cough, coryza or conjunctivitis, but no adequate clinical specimen was taken and the case has not been linked epidemiologically to a laboratory-confirmed case of measles or other communicable disease",
                        "Epidemiologically-linked measles cases: A suspected case of measles that has not been confirmed by a laboratory, but was geographically and temporally related with dates of rash onset occurring 7–23 days apart from a laboratory-confirmed case or another epidemiologically linked measles case",
                        "Laboratory-confirmed measles cases: A suspected case of measles that has been confirmed positive by testing in a proficient laboratory, and vaccine-associated illness has been ruled out",
                        "Total measles cases: the sum of clinically-compatible, epidemiologically linked and laboratory-confirmed cases",
                    ],
                }
            )
        else:  # rubella
            return pd.DataFrame(
                {
                    "feature": rubella_cols_to_plot,
                    "explanation": [
                        "Clinically-compatible rubella cases: A suspected case with fever and maculopapular rash and at least one of lymphadenopathy, arthralgia or conjunctivitis, but no adequate clinical specimen was taken",
                        "Epidemiologically-linked rubella cases: A suspected case of rubella that has not been confirmed by a laboratory, but was geographically and temporally related with dates of rash onset occurring 12–23 days apart from a laboratory-confirmed case",
                        "Laboratory-confirmed rubella cases: A suspected case of rubella that has been confirmed positive by testing in a proficient laboratory, and vaccine-associated illness has been ruled out",
                        "Total rubella cases: the sum of clinically-compatible, epidemiologically linked and laboratory-confirmed cases",
                    ],
                }
            )


app = App(app_ui, server)