import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from matplotlib import dates
from matplotlib.colors import LogNorm
from sunpy.time import parse_time
from sunpy.coordinates import frames
import sunpy.map
from astropy.coordinates import SkyCoord
from astropy import units as u
import datetime
import pylab
# get all the data and adjust datetime etcs
all_data = pd.read_csv('concat_1996-2020.csv')
tt = pd.to_datetime(all_data['event_starttime'])
times = [(t - tt[0]).total_seconds() for t in tt]
all_data['times'] = times
all_data['tt'] = tt
all_data['area_arcsec'] = all_data['area_atdiskcenter']/(725**2)
# get all unique days over the solar cycle
tstart = parse_time(all_data['event_starttime'].min()).datetime
tfinal = parse_time(all_data['event_endtime'].max()).datetime
time_over = [tstart.strftime('%Y-%m-%dT%H:%M:%S')]
t0 = tstart
while t0 < tfinal:
    t0 = t0 + datetime.timedelta(days=1)
    time_over.append(t0.strftime('%Y-%m-%dT%H:%M:%S'))
all_data_test = all_data.set_index('tt')

# get number of spots etc as function of day
spots = []
no_ar = []
for i in range(len(time_over)):
    data_for_day = all_data[all_data['event_starttime'].isin([time_over[i]])]
    no_spots = data_for_day['ar_numspots'].sum()
    spots.append(no_spots)
    no_ar.append(len(data_for_day))
spots_ar = pd.Series(spots, index=parse_time(time_over).datetime)
ar_no = pd.Series(no_ar, index=parse_time(time_over).datetime)
ssn_tots = 10*ar_no+spots_ar

# get SSN data
def read_ssn():
    ssn = pd.read_csv("../SN_m_tot_V2.0.csv", names=['year', 'month', 'decimal_date', \
                                                  'ssn', 'ssn_dev', 'number_obs', 'indicator'], 
             delimiter=';')
    years = ssn['year'].values; months = ssn['month']
    tt = [datetime.datetime(ssn['year'][i], ssn['month'][i], 1) for i in range(len(ssn))]


    ssn['times'] = tt

    return ssn.set_index('times')
ssn = read_ssn()

####------------------------------------------------------#####
sc23 = all_data_test.truncate('1996-09-01', '2009-01-01')
sc24 = all_data_test.truncate('2009-01-01', '2020-08-21')



# create an empty sunpy.map.Map
data_arr = np.zeros((1200, 1200))
coord = SkyCoord(0*u.arcsec, 0*u.arcsec, frame=frames.Helioprojective(observer='Earth', obstime=time_over[i]))
header = sunpy.map.make_fitswcs_header(data_arr, coord, scale=[2, 2]*u.arcsec/u.pix)
mapy = sunpy.map.Map(data_arr, header)


num_points = 100
lat_value = [-60, -45, -30, -15, 0, 15, 30, 45, 60]*u.deg
lon_value = [-60, -45, -30, -15, 0, 15, 30, 45, 60]*u.deg
lats = []
lons = []

for l in range(len(lat_value)):
    lat0 = SkyCoord(np.ones(num_points) * lat_value[l],
                np.linspace(-90, 90, num_points) * u.deg,
                frame=frames.HeliographicStonyhurst)
    lon0 = SkyCoord(np.linspace(-80, 80, num_points) * u.deg,
                np.ones(num_points) * lon_value[l], frame=frames.HeliographicStonyhurst)
    lat00 = lat0.transform_to(mapy.coordinate_frame)
    lon00 = lon0.transform_to(mapy.coordinate_frame)
    lats.append(lat00)
    lons.append(lon00)
coords_test = []
lat_value_plot = [-45, -30, -15, 0, 15, 30, 45]
for l in lat_value_plot:
    coords = SkyCoord(90*u.deg, l*u.deg, frame=frames.HeliographicStonyhurst).transform_to(mapy.coordinate_frame)
    coords_test.append(mapy.world_to_pixel(coords))
    


def ploty(cmap='viridis', filename='ssn_viridis'):


	    
	fig = plt.figure(figsize=(8, 10))
	# two maps side by side
	ax1a = pylab.axes([0.08, 0.58, 0.43, 0.43], projection=mapy)
	ax1b = pylab.axes([0.52, 0.58, 0.43, 0.43], projection=mapy)
	# middle butterfly
	ax2 = pylab.axes([0.08, 0.305, 0.9, 0.33])
	# bottom ssn plot
	ax3 = pylab.axes([0.08, 0.05, 0.9, 0.25], sharex=ax2)
	plt.style.use('dark_background')
	# size of dots
	sizey23 = 10*sc23['area_atdiskcenter']/sc23['area_atdiskcenter'].mean()
	sizey24 = 10*sc24['area_atdiskcenter']/sc24['area_atdiskcenter'].mean()
	    
	sizey23 = 5*sc23['ar_numspots']
	sizey24 = 5*sc24['ar_numspots']

	##### FIRST SOLAR CYCLE 23 ########
	# circle1 = plt.Circle((0, 0), 960, color='k', fill=False)
	mapy.plot(axes=ax1a, alpha=0.0)
	mapy.draw_limb(color='w', lw=0.8)
	#mapy.draw_grid(color='k', lw=0.5)
	ax1a.scatter((sc23['hpc_x'].values*u.arcsec).to(u.deg),
				 (sc23['hpc_y'].values*u.arcsec).to(u.deg),
				  s=sizey23, edgecolor='k', lw=0.1,
	              c=sc23['times'], alpha=0.5,
	              transform=ax1a.get_transform('world'), cmap=cmap)

	ax1a.set_xlabel('X (arcsec)')
	ax1a.set_ylabel('Y (arcsec)')
	ax1a.tick_params(axis='both',direction='in')
	ax1a.set_title('Solar Cycle 23').set_position([.5, 1.0])
	ax1a.set_axis_off()
	for l in range(len(lats)):
	    ax1a.plot_coord(lats[l], color='w', lw=0.2)
	    ax1a.plot_coord(lons[l], color='w', lw=0.2)


	##### FIRST SOLAR CYCLE 24 ########
	# circle1 = plt.Circle((0, 0), 960, color='k', fill=False)

	mapy.plot(axes=ax1b, alpha=0.0, title='Solar Cycle 24')
	mapy.draw_limb(color='w', lw=0.8)
	#mapy.draw_grid(color='w', lw=0.5)
	ax1b.scatter((sc24['hpc_x'].values*u.arcsec).to(u.deg), 
				 (sc24['hpc_y'].values*u.arcsec).to(u.deg), 
				 s=sizey24, edgecolor='k', lw=0.1,
	             c=sc24['times'], alpha=0.5,
	            transform=ax1b.get_transform('world'), cmap=cmap)
	ax1b.set_xlabel('X (arcsec)')
	ax1b.set_ylabel(' ')
	ax1b.tick_params(which='both',direction='in')
	ax1b.tick_params(axis='y', labelleft=False)
	ax1b.set_title('Solar Cycle 24').set_position([.5, 1.0])
	ax1b.set_axis_off()
	for l in range(len(lats)):
	    ax1b.plot_coord(lats[l], color='w', lw=0.2)
	    ax1b.plot_coord(lons[l], color='w', lw=0.2)

	for c in range(len(coords_test)):
	    ax1a.text(coords_test[c].x.value+40, coords_test[c].y.value, str(lat_value_plot[c])+'$^\circ$')
	    ax1b.text(coords_test[c].x.value+40, coords_test[c].y.value, str(lat_value_plot[c])+'$^\circ$')
	    
	    ##### BUTTERFLY DIAGRAM FOR BOTH ########
	ax2.scatter(sc23.index, sc23['hgc_y'], 
	            alpha=0.5, c=sc23['times'], 
	            s=sizey23/2,
	            #s=100*all_data['ar_numspots']/all_data['ar_numspots'].mean(),
	            cmap=cmap, edgecolor='k', lw=0.1)

	ax2.scatter(sc24.index, sc24['hgc_y'], 
	            alpha=0.5, c=sc24['times'], 
	            s=sizey24/2,
	            #s=100*all_data['ar_numspots']/all_data['ar_numspots'].mean(),
	            cmap=cmap, edgecolor='k', lw=0.1)

	ax2.set_ylim(-45, 45)
	ax2.set_ylabel('Latitude ($^\circ$)')
	ax2.tick_params(which='both',direction='in', labelbottom=False)
	ax2.xaxis.set_major_locator(dates.YearLocator(4))
	ax2.xaxis.set_minor_locator(dates.YearLocator(1))  
	ax2.xaxis.set_major_formatter(dates.DateFormatter('%Y'))  
	
	##### SUNSPOT NUMBER AS A FUNCTION OF TIME ########
	ax3.plot(ssn_tots.resample('30D').mean(), color='w')
	ax3.set_ylabel('Sunspot number')
	ax3.set_xlabel('Time')
	plt.tight_layout()
	ax3.set_xlim(tstart, tfinal)
	ax3.tick_params(which='both',direction='in')

	ax1b.set_facecolor('k')
	ax1a.set_facecolor('k')
	ax2.set_facecolor('k')
	ax3.set_facecolor('k')


	plt.savefig('full_plot_{:s}.png'.format(filename), dpi=200)
	plt.close()


















