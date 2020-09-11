import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from sunpy.time import parse_time
import sunpy.map
from sunpy.coordinates import frames
from astropy.coordinates import SkyCoord
from astropy import units as u
import datetime
import subprocess
import pylab


# read in the data as a pandas DataFrame
all_data = pd.read_csv('all_ar_2010-2020.csv')
# get the time as datetime objects
tt = pd.to_datetime(all_data['event_starttime'])
# get the time in seconds from initial time (for plotting)
times = [(t - tt[0]).total_seconds() for t in tt]
# make these columns of DataFrame
all_data['times'] = times
all_data['tt'] = tt

# we want to make a list of all the dates from 2010-2020 for
# plotting, this will allow us to pull out the active regions 
# for each day (or not if none on a certain day) for plotting.
tstart = parse_time(all_data['event_starttime'].min()).datetime
tfinal = parse_time(all_data['event_endtime'].max()).datetime
time_over = [tstart.strftime('%Y-%m-%dT%H:%M:%S')]
t0 = tstart
while t0 < tfinal:
    t0 = t0 + datetime.timedelta(days=1)
    time_over.append(t0.strftime('%Y-%m-%dT%H:%M:%S'))

# this is a rough conversion for area of active region at disk
# center in km to area in arcsec (as observed from Earth). If you 
# want to be more precise you would calculate for each day, but
# its grand for this purpose.
all_data['area_arcsec'] = all_data['area_atdiskcenter']/(725**2)


def plot_as_datapoints(i, savedir='./plots/'):
    """
    This function plots the Sun with the daily active regions, the butterfly diagram, 
    and histogram for the data up to the date time_over[i].

    The plot will be saved in ./plots with the name test_i.png. 
    To make the movie, the plots needs to be sequentially ordered. 

    Parameters
    ----------
    i : ~int
        the index of the `time_over` list for which to plot. 

    """


    # find the active region data for the day from the dataframe
    data_for_day = all_data[all_data['event_starttime'].isin([time_over[i]])]

    # get the daya for the past 10 days previous to timestep i. This is to plot the previous
    # active regions with a colormap to highlight the active region evolution.
    if i < 10:
        data_for_days = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    else:
        data_for_days = all_data[all_data['event_starttime'].isin(time_over[i-10:i])]

    # get the data for the past 100 days from i for faint active region plot
    if i < 100:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    else:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[i-100:i])]
   
    # all previous data up to date (i) for butterfly diagram.
    data_all_past = all_data[all_data['event_starttime'].isin(time_over[0:i])]

    #########################################
    # where plot happens

    # define axes
    fig = plt.figure(figsize=(7, 8))
    ax1 = pylab.axes([0.12, 0.02, 0.62, 0.62])
    ax2 = pylab.axes([0.75, 0.0595, 0.22, 0.542], sharey=ax1)
    ax3 = pylab.axes([0.12, 0.66, 0.62, 0.33])

    # plotting on disk!

    # for all past
    if len(data_for_past)>0:

        ax1.scatter(data_for_past['hpc_x'], data_for_past['hpc_y'], c=data_for_past['times'], 
                    s=2*np.sqrt(data_for_past['area_arcsec']),  alpha=0.1, cmap='Reds',
                    edgecolor='k', lw=0.4)

    # for day
    if len(data_for_day)>0:
        ax1.scatter(data_for_day['hpc_x'], data_for_day['hpc_y'], 
                    s=2*np.sqrt(data_for_day['area_arcsec']),
                    color='k')

    # for days previous
    if len(data_for_days)>0:
        ax1.scatter(data_for_days['hpc_x'], data_for_days['hpc_y'], c=data_for_days['times'], 
                    s=2*np.sqrt(data_for_days['area_arcsec']), cmap='Reds',
                    edgecolor='k', lw=0.4)        


    # approximate radius of Sun in arcsecs
    circle1 = plt.Circle((0, 0), 960, color='k', fill=False)
    ax1.add_artist(circle1)
    ax1.set_aspect('equal', adjustable='box') # make square
    ax1.set_xlim(-1101, 1101) 
    ax1.set_ylim(-1101, 1101)
    ax1.set_xlabel('Helioprojective Longitude (arcsec)')
    ax1.set_ylabel('Helioprojective Latitude (arcsec)')
    ax1.tick_params(which='both', direction='in')


    # plotting histogram to right of Sun
    na, bins, patches = ax2.hist(data_all_past['hpc_y'], bins=100, orientation='horizontal', color='darkred')
    ax2.set_ylim(-1101, 1101)
    ax2.tick_params(labelleft=False, which='both', direction='in')
    ax2.set_xlabel('No. active regions')
    ax2.set_xlim(0, 300)

    # plotting butterfly diagram
    ax3.scatter(data_all_past['tt'], data_all_past['hgc_y'], c=data_all_past['times'], alpha=0.3, 
              s=np.sqrt(data_all_past['area_arcsec']), 
              edgecolor='k', lw=0.4, cmap='Reds')
    ax3.axvline(time_over[i], color='k', ls='dashed')
    ax3.set_xlabel('Time (UT)')
    ax3.set_ylabel('Latitude (deg)')
    ax3.tick_params(which='both', direction='in')
    ax3.set_xlim(all_data['tt'].min(), all_data['tt'].max())
    ax3.set_ylim(-45, 45)
    

    # save the plot
    plt.savefig(savedir + 'test_{:04d}.png'.format(i), dpi=200)
    plt.close()


def make_movie_final():
    for i in range(len(time_over)):
        print(i)
        test_for(i)

    subprocess.call(['ffmpeg','-r', '10' ,'-f', 'image2', '-s', 
                '1920x1080', '-i', './plots/test_%04d.png', 
                '-vcodec', 'libx264', '-crf', '25',  '-pix_fmt', 'yuv420p', 'test_mov2.mp4'])


########-----------------------------------------------##########
#   Below is the same but plotting the points probably a bit more
#   accuratly using wcsaxes and a sunpy.map.Map.
########-----------------------------------------------##########


def plot_as_sunpy_map(i, savedir='./plots/'):

    all_prev_data = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    
    if i < 10:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    else:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[i-10:i])]
        
        
    data_for_day = all_data[all_data['event_starttime'].isin([time_over[i]])]
    
    # create an empty sunpy.map.Map
    data_arr = np.zeros((1500, 1500))
    coord = SkyCoord(0*u.arcsec, 0*u.arcsec, frame=frames.Helioprojective(observer='Earth', obstime=time_over[i]))
    header = sunpy.map.make_fitswcs_header(data_arr, coord, scale=[2, 2]*u.arcsec/u.pix)
    mapy = sunpy.map.Map(data_arr, header)


    # make the plot
    fig = plt.figure(figsize=(6,5))
    ax = fig.add_subplot(projection=mapy)
    mapy.plot(alpha=0)
    mapy.draw_limb(color='k')

    ax.scatter((all_prev_data['hpc_x'].values*u.arcsec).to(u.deg),
                (all_prev_data['hpc_y'].values*u.arcsec).to(u.deg), 
                 cmap='viridis',
                 c=all_prev_data['times'], alpha=0.1,
                 s=np.sqrt(all_prev_data['area_arcsec']), 
                 transform=ax.get_transform('world')) 

    # plot the AR for the day
    if len(data_for_day)>0:
        ax.scatter((data_for_day['hpc_x'].values*u.arcsec).to(u.deg),
                   (data_for_day['hpc_y'].values*u.arcsec).to(u.deg), 
                    c='k', marker='o',
                    s=np.sqrt(data_for_day['area_arcsec']),
                    transform=ax.get_transform('world'))

    # plot the AR for the past days
    if len(data_for_past)>0:
        ax.scatter((data_for_past['hpc_x'].values*u.arcsec).to(u.deg),
                  (data_for_past['hpc_y'].values*u.arcsec).to(u.deg), 
                  transform=ax.get_transform('world'), 
                  c=data_for_past['times'], 
                  s=np.sqrt(data_for_past['area_arcsec']),
                  cmap='viridis_r')

    # xlims etc
    lims_arcsec = ((-1101, 1100) * u.arcsec, (-1100, 1100) * u.arcsec)
    lims_pix = mapy.world_to_pixel(SkyCoord(*lims_arcsec, frame=mapy.coordinate_frame))
    ax.set_xlim(lims_pix[0].value)
    ax.set_ylim(lims_pix[1].value)
    ax.set_title(mapy.date.strftime('%Y-%m-%d'))
    plt.savefig(savedir + 'mapplots_{:04d}.png'.format(i), dpi=200)
    plt.close()


def make_movie_maps():

  for i in range(len(time_over)):
    ploty(i)
    print(i)

  subprocess.call(['ffmpeg','-r', '10' ,'-f', 'image2', '-s', 
                '1920x1080', '-i', './plots/mapplots_%04d.png', 
                '-vcodec', 'libx264', '-crf', '25',  '-pix_fmt', 'yuv420p', 'test_mov_map.mp4'])

