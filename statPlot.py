import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from matplotlib.ticker import MultipleLocator

# we should have this plot in Polish and English
terms = { 'pages': {'en': 'pages', 'pl': 'strony'},
          'entries': {'en': 'entries', 'pl': 'hasła'},
          'ylabel': {'en': 'number of pages and entries in thousands', 'pl': 'liczba stron i haseł w tys.'},
          'title': {'en': 'Polish Wiktionary growth', 'pl': 'Rozwój Wikisłownika'}
          }

def monthly_stat_plot(filename='stat-data.csv', lang='pl'):
    data = np.genfromtxt(filename, dtype={'names': ('date', 'pages', 'sections'),
                                       'formats': ('U7', 'i4', 'i4')}, delimiter=',')

    # convert strings to datetime
    dates = np.array([dt.datetime.strptime(d, '%m-%Y') for d in data['date']])
    
    # we are missing the data on sections
    mask = np.equal(data['sections'], -1)

    # set up the plot
    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    
    # set nice colors from ColorBrewer2
    colors = ['#67a9cf', '#ef8a62']
    
    # plot section count
    ax.plot(dates[~mask], data['sections'][~mask], lw=2.5, color=colors[1], label=terms['entries'][lang])
   
    # plot page count and fill the area below
    ax.plot(dates, data['pages'], lw=2.5, color=colors[0], label=terms['pages'][lang])
    ax.fill_between(dates, data['pages'], alpha=0.5, color=colors[0])

    # y axis label and plot title
    ax.set_ylabel(terms['ylabel'][lang])
    plt.suptitle(terms['title'][lang], fontsize=18)

    
    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks([data['sections'][-1], data['pages'][-1]])
    ax.grid(True)

    legend = ax.legend(loc='upper left')
    
    plt.savefig('Wzrost_Wikislownika.svg')

if __name__ == '__main__':
    monthly_stat_plot()
    plt.show()
