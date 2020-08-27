import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from matplotlib import dates
from matplotlib.colors import LogNorm
from sunpy.time import parse_time
import sunpy.map
from sunpy.coordinates import frames
from astropy.coordinates import get_body, SkyCoord, solar_system_ephemeris
from astropy import units as u
import datetime

all_data = pd.read_csv('all_ar_2010-2020.csv')
tt = pd.to_datetime(all_data['event_starttime'])
times = [(t - tt[0]).total_seconds() for t in tt]
all_data['times'] = times

tstart = parse_time(all_data['event_starttime'].min()).datetime
tfinal = parse_time(all_data['event_endtime'].max()).datetime
time_over = [tstart.strftime('%Y-%m-%dT%H:%M:%S')]
t0 = tstart
while t0 < tfinal:
    t0 = t0 + datetime.timedelta(days=1)
    time_over.append(t0.strftime('%Y-%m-%dT%H:%M:%S'))

all_data['area_arcsec'] = all_data['area_atdiskcenter']/(725**2)



def ploty(i, savedir='/Users/lahayes/space_weather_stuff/SolarStatsStuff/ar_analysis/plots/'):
    # for testing i = 600


    if i < 10:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    else:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[i-10:i])]
        
        
    data_for_day = all_data[all_data['event_starttime'].isin([time_over[i]])]
    

    # create an empty map
    data_arr = np.zeros((1500, 1500))
    coord = SkyCoord(0*u.arcsec, 0*u.arcsec, frame=frames.Helioprojective(observer='Earth', obstime=time_over[i]))
    header = sunpy.map.make_fitswcs_header(data_arr, coord, scale=[2, 2]*u.arcsec/u.pix)
    mapy = sunpy.map.Map(data_arr, header)


    # make the plot
    fig = plt.figure()
    ax = fig.add_subplot(projection=mapy)
    mapy.plot(alpha=0)
    mapy.draw_limb(color='k')

    # plot the AR for the day
    ax.scatter((data_for_day['hpc_x'].values*u.arcsec).to(u.deg),
               (data_for_day['hpc_y'].values*u.arcsec).to(u.deg), 
               transform=ax.get_transform('world'), 
               c='k', marker='x',
               s=np.sqrt(data_for_day['area_arcsec']))

    # plot the AR for the past daus
    ax.scatter((data_for_past['hpc_x'].values*u.arcsec).to(u.deg),
               (data_for_past['hpc_y'].values*u.arcsec).to(u.deg), 
               transform=ax.get_transform('world'), 
               c=data_for_past['times'], 
               s=np.sqrt(data_for_past['area_arcsec']),
               cmap='Reds')

    # xlims etc
    lims_arcsec = ((-1001, 1000) * u.arcsec, (-1000, 1000) * u.arcsec)
    lims_pix = mapy.world_to_pixel(SkyCoord(*lims_arcsec, frame=mapy.coordinate_frame))
    ax.set_xlim(lims_pix[0].value)
    ax.set_ylim(lims_pix[1].value)
    ax.set_title(mapy.date.strftime('%Y-%m-%d'))
    plt.savefig(savedir + 'test_{:04d}.png'.format(i), dpi=200)
    plt.close()



def plot_for_date(i, savedir='/Users/lahayes/space_weather_stuff/SolarStatsStuff/ar_analysis/plots/'):
    """
    datey should be str in format "YYYY-mm-ddTHH:MM:SS"
    """
    if i < 10:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    else:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[i-10:i])]
        
        
    data_for_day = all_data[all_data['event_starttime'].isin([time_over[i]])]
    
    fig, ax = plt.subplots(figsize=(5,5))
    circle1 = plt.Circle((0, 0), 960, color='k', fill=False)
    if len(data_for_day) > 0:
        ax.scatter(data_for_day['hpc_x'], data_for_day['hpc_y'], 
                   s=5*np.sqrt(data_for_day['area_arcsec'], 
                   alpha=0.7, color='k', marker='x')
        
    if len(data_for_past)>0:
        ax.scatter(data_for_past['hpc_x'], data_for_past['hpc_y'], 
                   s=5*np.sqrt(data_for_day['area_arcsec'], 
                   c=data_for_past['times'],
                   cmap='Reds',
                   alpha=0.7)        
    ax.set_xlim(-1000, 1000)
    ax.set_ylim(-1000, 1000)

    
    ax.set_xlabel('X arcsec')
    ax.set_ylabel('Y arscec')
    ax.set_title(time_over[i])
    ax.add_artist(circle1)
    ax.set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.savefig(savedir + 'test_{:04d}.png'.format(i), dpi=200)
    plt.close()
