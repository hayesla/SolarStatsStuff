from sunpy.net import hek
import pandas as pd 
import time
client = hek.HEKClient()

# tstart = '2010-01-01'
# #tend = '2010-02-01'
# tend = '2020-08-21'

# tstart = '1996-09-01'
# tend = '2010-01-01'

tstart = '1986-09-01'
tend = '1996-09-01'

t1 = time.time()
result = client.search(hek.attrs.Time(tstart, tend),
                       hek.attrs.EventType('AR'),
                       hek.attrs.FRM.Name == 'NOAA SWPC Observer')
t2 = time.time()
print(t2 - t1)

new_columns = ['ar_noaanum', 'event_starttime', 'event_endtime', 
               'hpc_x', 'hpc_y', 'hgs_x', 'hgs_y', 'hgc_x', 'hgc_y', 'frm_humanflag', 'frm_name',
               'frm_daterun', 'ar_mtwilsoncls', 'ar_mcintoshcls', 'SOL_standard', 
               'ar_numspots', 'area_atdiskcenter', 'area_unit']


new_table = result[new_columns]

# new_table.write('all_ar_2010-2020.csv', format='csv')

# new_table.write('all_ar_1996-2010.csv', format='csv')

new_table.write('all_ar_1986-1996.csv', format='csv')