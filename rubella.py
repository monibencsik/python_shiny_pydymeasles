import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 


cases_month = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-06-24/cases_month.csv')
measles = cases_month[['region', 'country', 'iso3', 'year', 'month', 'measles_suspect', 'measles_clinical', 'measles_epi_linked', 'measles_lab_confirmed', 'measles_total']]
rubella = cases_month[['region', 'country', 'iso3', 'year', 'month', 'rubella_clinical', 'rubella_epi_linked', 'rubella_lab_confirmed', 'rubella_total']]

#print(measles.columns)

rubella_cols_to_plot = [
    "rubella_clinical", 
    "rubella_epi_linked", 
    "rubella_lab_confirmed", 
    "rubella_total"
]

region_sum = rubella.groupby('region', as_index=False)[rubella_cols_to_plot].sum()

for col in rubella_cols_to_plot:      
    ax = sns.barplot(data = region_sum, x = 'region', y = col)
    plt.ticklabel_format(style='plain', axis='y')
    for container in ax.containers:
        ax.bar_label(container, labels=[f'{v.get_height():.0f}' for v in container], padding=3)
    plt.title(f'{col} by Region')
    plt.tight_layout()
    plt.show()

# measles_plot_metadata = pd.DataFrame({
#     'feature': cols_to_plot,
#     'explanation':['Suspected measles cases: A suspected case is one in which a patient with fever and maculopapular (non-vesicular) rash, or in whom a health-care worker suspects measles', 'Clinically-compatible measles cases: A suspected case with fever and maculopapular (non-vesicular) rash and at least one of cough, coryza or conjunctivitis, but no adequate clinical specimen was taken and the case has not been linked epidemiologically to a laboratory-confirmed case of measles or other communicable disease', 'Epidemiologically-linked measles cases: A suspected case of measles that has not been confirmed by a laboratory, but was geographically and temporally related with dates of rash onset occurring 7–23 days apart from a laboratory-confirmed case or another epidemiologically linked measles case', 'Laboratory-confirmed measles cases: A suspected case of measles that has been confirmed positive by testing in a proficient laboratory, and vaccine-associated illness has been ruled out', 'Total measles cases: the sum of clinically-compatible, epidemiologically linked and laboratory-confirmed cases']
# })

# print(measles_plot_metadata)