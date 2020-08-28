from sunpy.net import hek
client = hek.HEKClient()

def get_ar_data(tstart, tend):
	"""
	Fucntion to get the active region data from NOAA SPWC by
	querying the HEK.

	Parameters
	----------
	tstart : ~str
		the start time of the query
	tend : ~str
		the end time of the query

	Returns
	-------
	astropy.table.Table
		an astropy table with the data
	"""

	result = client.search(hek.attrs.Time(tstart, tend),
	                       hek.attrs.EventType('AR'),
	                       hek.attrs.FRM.Name == 'NOAA SWPC Observer')

	# only interested in these columns from the HEK query
	new_columns = ['ar_noaanum', 'event_starttime', 'event_endtime', 
	               'hpc_x', 'hpc_y', 'hgs_x', 'hgs_y', 'hgc_x', 'hgc_y', 
	               'frm_humanflag', 'frm_name',
	               'frm_daterun', 'ar_mtwilsoncls', 'ar_mcintoshcls', 'SOL_standard', 
	               'ar_numspots', 'area_atdiskcenter', 'area_unit']


	new_table = result[new_columns]

	return new_table


# get the data
ar_data = get_ar_data('2010-01-01', '2020-08-21')
# save the data as a csv file so that it can be read in again. 
ar_data.write('all_ar_2010-2020.csv', format='csv')



