import os
import re
import datetime
import pandas
import numpy as np
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import mpld3
import requests
import io

pandas.set_option('display.max_rows', 500)


class Plots:
    @staticmethod
    def get_date(date_s):
        date_d = {k: int(i) + (2000 if k == 'year' else 0) for i, k in zip(date_s.split('/'), ('month', 'day', 'year'))}
        date_o = datetime.datetime(**date_d)
        return int(mdates.date2num(date_o) + 0.5), date_s, date_o

    @staticmethod
    def fmt_axis(ax):
        now = int(mdates.date2num(datetime.datetime.now()) + 0.5)
        ax.set_xlim(now - 100, now)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        xy = [a.get_xydata() for a in ax.get_children() if hasattr(a, 'get_xydata')]
        if len(xy):
            xy = np.vstack(xy)
            ax.set_ylim(Plots.getylim(xy[:, 1], xy[:, 0], ax.get_xlim(), log=ax.get_xscale() == 'log'))

    @staticmethod
    def getylim(y, x=None, xlim=None, margin=0.05, log=False):
        """ get limits for plots according to data
            copied from matplotlib.axes._base.autoscale_view

            y: the y data
            optional, for when xlim is set manually on the plot
                x: corresponding x data
                xlim: limits on the x-axis in the plot, example: xlim=(0, 100)
                margin: what fraction of white-space to have at all borders
            y and x can be lists or tuples of different data in the same plot

            wp@tl20191220
        """
        y = np.array(y).flatten()
        if log:
            y = np.log(y)
        if x is not None and xlim is not None:
            x = np.array(x).flatten()
            y = y[(np.nanmin(xlim) < x)*(x < np.nanmax(xlim))*(np.abs(x) > 0)]
            if not np.any(np.isfinite(y)):
                return 0, 1
            if len(y) == 0:
                return -margin, margin
        y0t, y1t = np.nanmin(y), np.nanmax(y)
        if np.isfinite(y1t) and np.isfinite(y0t):
            delta = (y1t - y0t) * margin
            if y0t == y1t:
                delta = 0.5
        else:  # If at least one bound isn't finite, set margin to zero
            delta = 0
        if log:
            return np.exp(y0t - delta), np.exp(y1t + delta)
        else:
            return y0t - delta, y1t + delta

    @staticmethod
    def transform(a, b, x, xlim):
        return np.polyval(np.polyfit(Plots.getylim(a, x, xlim), Plots.getylim(b, x, xlim), 1), a)


class Corona:
    def __init__(self):
        self.home = os.path.dirname(__file__)
        self.update()

    def update(self):
        self.last_update = datetime.datetime.now()
        self.confirmed_global = self.get_data(
            'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
        self.deaths_global = self.get_data(
            'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
        self.regions = sorted(self.confirmed_global['Province/State'].tolist())

    @staticmethod
    def get_data(url):
        with requests.get(url, allow_redirects=True) as r:
            with io.BytesIO(r.content) as b:
                p = pandas.read_csv(b)

        null = p['Province/State'].isnull()
        p.loc[null, 'Province/State'] = p.loc[null, 'Country/Region']

        # make series searchable by region
        countries = p['Country/Region'].unique()
        states = p['Province/State'].unique()
        for country in countries:
            if country not in states:
                ca = p.query('`Country/Region`=="{}"'.format(country))
                cb = ca.sum(axis=0)
                cb['Province/State'] = country
                cb['Country/Region'] = country
                cb['Lat'] /= len(ca)
                cb['Long'] /= len(ca)
                p.loc[p.index.max() + 1] = cb

        # make World entry by summing
        w = np.sum(p)
        w.name = p.index.max() + 1
        w['Province/State'] = 'World'
        w['Country/Region'] = 'World'
        w['Lat'] = 0
        w['Long'] = 0
        return pandas.concat((p, pandas.DataFrame(w).T))

    @staticmethod
    def plot_series(fig, ax, dates_number, dates_obj, cum, llabel=None, rlabel=None):
        ax.plot(dates_obj, cum, 'ro-')
        Plots.fmt_axis(ax)
        ax.set_ylim(Plots.getylim(cum, dates_number, ax.get_xlim()))

        dcum = cum - np.interp(dates_number, dates_number + 1, cum)
        bx = ax.twinx()
        p, = bx.plot(dates_obj, Plots.transform(cum, dcum, dates_number, ax.get_xlim()), 'o', color='none')
        mpld3.plugins.connect(fig, mpld3.plugins.PointLabelTooltip(p, labels=[f'{n:.2g}' for n in cum]))
        p, = bx.plot(dates_obj, dcum, 'ko-')
        bx.patch.set_alpha(0.0)
        mpld3.plugins.connect(fig, mpld3.plugins.PointLabelTooltip(p, labels=[f'{n:.2g}' for n in dcum]))
        Plots.fmt_axis(bx)
        if llabel is not None:
            ax.set_ylabel(llabel, color='r')
        if rlabel is not None:
            bx.set_ylabel(rlabel, color='k')

    def plot_cases(self, place, sicktime=14):
        if datetime.datetime.now() - self.last_update > datetime.timedelta(hours=1):
            self.update()

        n = self.confirmed_global.query(f'`Province/State`=="{place}"')
        d = self.deaths_global.query(f'`Province/State`=="{place}"')
        if n.empty:
            n = self.confirmed_global.query(f'`Country/Region`=="{place}"')
            d = self.deaths_global.query(f'`Country/Region`=="{place}"')
        n = pandas.DataFrame(n.sum()).T
        d = pandas.DataFrame(d.sum()).T

        dates = [Plots.get_date(c) for c in n.columns if re.match('[\d/]+', c) is not None]

        dates_number, dates_str, dates_obj = zip(*sorted(dates))
        sick_cum = np.array([int(n[date]) for date in dates_str])
        death_cum = np.array([int(d[date]) for date in dates_str])
        dates_number = np.array(dates_number)
        sick_now = sick_cum - np.interp(dates_number, dates_number + sicktime, sick_cum)

        fig = Figure(figsize=(16, 8), dpi=100)
        ax = fig.add_subplot(4, 1, 1)
        self.plot_series(fig, ax, dates_number, dates_obj, sick_cum, 'sick cumulative', 'daily new cases')
        ax.set_title('cumulative and new daily cases')

        ax = fig.add_subplot(4, 1, 2)
        self.plot_series(fig, ax, dates_number, dates_obj, sick_now, 'sick now', 'daily change')
        ax.set_title('current sick and daily change')

        ax = fig.add_subplot(4, 1, 3)
        reproduction_rate = sick_now / np.clip(np.interp(dates_number, dates_number + 4, sick_now), 1e-15, np.inf)
        p, = ax.plot(dates_obj, np.clip(reproduction_rate, 0, 3), 'ro-')
        ax.plot((np.nanmin(dates_number), np.nanmax(dates_number)), (1, 1), '--k')
        mpld3.plugins.connect(fig, mpld3.plugins.PointLabelTooltip(p, labels=[f'{n:.2f}' for n in reproduction_rate]))
        Plots.fmt_axis(ax)
        ax.set_ylim(0.5, 1.5)
        ax.set_title('reproduction rate')
        ax.set_ylabel('reproduction rate', color='r')

        ax = fig.add_subplot(4, 1, 4)
        self.plot_series(fig, ax, dates_number, dates_obj, death_cum, 'diseased cumulative', 'daily diseased')
        ax.set_title('cumulative and new deaths')

        fig.autofmt_xdate()
        fig.tight_layout(h_pad=2)

        return mpld3.fig_to_html(fig)
