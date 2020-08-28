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
import subprocess
import pylab

all_data = pd.read_csv('all_ar_2010-2020.csv')
tt = pd.to_datetime(all_data['event_starttime'])
times = [(t - tt[0]).total_seconds() for t in tt]
all_data['times'] = times
all_data['tt'] = tt
tstart = parse_time(all_data['event_starttime'].min()).datetime
tfinal = parse_time(all_data['event_endtime'].max()).datetime
time_over = [tstart.strftime('%Y-%m-%dT%H:%M:%S')]
t0 = tstart
while t0 < tfinal:
    t0 = t0 + datetime.timedelta(days=1)
    time_over.append(t0.strftime('%Y-%m-%dT%H:%M:%S'))

all_data['area_arcsec'] = all_data['area_atdiskcenter']/(725**2)



def ploty(i, savedir='./plots/'):
    # for testing i = 600


    all_prev_data = all_data[all_data['event_starttime'].isin(time_over[0:i])]
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
    fig = plt.figure(figsize=(6,5))
    ax = fig.add_subplot(projection=mapy)
    mapy.plot(alpha=0)
    mapy.draw_limb(color='k')

    ax.scatter((all_prev_data['hpc_x'].values*u.arcsec).to(u.deg),
                (all_prev_data['hpc_y'].values*u.arcsec).to(u.deg), 
                 transform=ax.get_transform('world'), cmap='viridis',
                 c=all_prev_data['times'], alpha=0.1,
                 s=np.sqrt(all_prev_data['area_arcsec'])) 

    # plot the AR for the day
    if len(data_for_day)>0:
      ax.scatter((data_for_day['hpc_x'].values*u.arcsec).to(u.deg),
                 (data_for_day['hpc_y'].values*u.arcsec).to(u.deg), 
                 transform=ax.get_transform('world'), 
                 c='k', marker='o',
                 s=np.sqrt(data_for_day['area_arcsec']))

    if len(data_for_past)>0:
    # plot the AR for the past daus
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
    plt.savefig(savedir + 'test_{:04d}.png'.format(i), dpi=200)
    plt.close()


def make_movie():

  for i in range(len(time_over)):
    ploty(i)
    print(i)

  import subprocess

  subprocess.call(['ffmpeg','-r', '10' ,'-f', 'image2', '-s', 
                '1920x1080', '-i', './plots/test_%04d.png', 
                '-vcodec', 'libx264', '-crf', '25',  '-pix_fmt', 'yuv420p', 'test_mov.mp4'])





def plot_no_map(i, savedir='./plots/'):
    # for testing i = 600


    if i < 10:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    else:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[i-10:i])]
        
        
    data_for_day = all_data[all_data['event_starttime'].isin([time_over[i]])]
    

def test_for(i, savedir='./plots/'):


    if i < 10:
        data_for_days = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    else:
        data_for_days = all_data[all_data['event_starttime'].isin(time_over[i-10:i])]


    # all previous data upto date for butterfly diagram
    if i < 100:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    else:
        data_for_past = all_data[all_data['event_starttime'].isin(time_over[i-100:i])]

    data_all_past = all_data[all_data['event_starttime'].isin(time_over[0:i])]
    # data for the day
    data_for_day = all_data[all_data['event_starttime'].isin([time_over[i]])]


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



    circle1 = plt.Circle((0, 0), 960, color='k', fill=False)
    ax1.add_artist(circle1)
    ax1.set_aspect('equal', adjustable='box')
    ax1.set_xlim(-1101, 1101)
    ax1.set_ylim(-1101, 1101)
    ax1.set_xlabel('Helioprojective Longitude (arcsec)')
    ax1.set_ylabel('Helioprojective Latitude (arcsec)')
    ax1.tick_params(which='both', direction='in')


    # plotting hist!
    na, bins, patches = ax2.hist(data_all_past['hpc_y'], bins=100, orientation='horizontal', color='darkred')
    # fracs = np.arange(0, 200, 1)
    # norm = colors.Normalize(fracs.min(), fracs.max())

    # for thisfrac, thispatch in zip(fracs, patches):
    #     color=plt.cm.get_cmap('viridis')(norm(thisfrac))
    #     thispatch.set_facecolor(color)

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
    plt.savefig(savedir + 'test_{:04d}.png'.format(i), dpi=200)
    plt.close()


def make_movie2():
    for i in range(len(time_over)):
        print(i)
        test_for(i)


    subprocess.call(['ffmpeg','-r', '10' ,'-f', 'image2', '-s', 
                '1920x1080', '-i', './plots/test_%04d.png', 
                '-vcodec', 'libx264', '-crf', '25',  '-pix_fmt', 'yuv420p', 'test_mov2.mp4'])

subprocess.call(['ffmpeg', '-r', '1/5', '-i', './plots/test_%04d.png', '-c:v', 'libx264', '-vf', 'fps=25',
                '-pix_fmt', 'yuv420p', 'out.mp4'])


def testt():
    # make the plot
    fig, ax = plt.subplots()


    # plot the AR for the day
    if len(data_for_day)>0:
      ax.scatter(data_for_day['hpc_x'],
                 data_for_day['hpc_y'], 
                 c='k', marker='x',
                 s=np.sqrt(data_for_day['area_arcsec']))
      
    if len(data_for_past)>0:
    # plot the AR for the past daus
      ax.scatter(data_for_past['hpc_x'],
                 data_for_past['hpc_y'], 
                 c=data_for_past['times'], 
                 s=np.sqrt(data_for_past['area_arcsec']),
                 cmap='Reds')

    ax.set_xlim(-1000, 1000)
    ax.set_ylim(-1000, 1000)
    ax.set_title(time_over[i][0:10])
    plt.savefig(savedir + 'test2_{:04d}.png'.format(i), dpi=200)
    plt.close()