; Create IDL structure for a Flare event
event = struct4event('fl')
; Populate the structure with required values
event.required.OBS_Observatory = 'TRACE'
event.required.OBS_Instrument = 'TRACE'
event.required.OBS_ChannelID = 'TRACE 171'
event.required.OBS_MeanWavel = '171'
event.required.OBS_WavelUnit = 'Angstroms'
event.required.FRM_Name = 'Karel Schrijver'
event.required.FRM_Identifier = 'Karel Schrijver'
event.required.FRM_Institute ='LMSAL'
event.required.FRM_HumanFlag = 'yes'
event.required.FRM_ParamSet = 'n/a'
event.required.FRM_DateRun = '2007/01/03 12:00:00'
event.required.FRM_Contact = 'schryver at lmsal dot com'
event.required.FRM_URL = 'n/a'
event.required.Event_StartTime = '2006/10/10 23:45:13'
event.required.Event_PeakTime = '2006/10/10 23:47:54'
event.required.Event_EndTime = '2006/10/10 23:55:20'
event.required.Event_CoordSys = 'UTC-HPC-TOPO'
event.required.Event_CoordUnit = 'arcsec'
event.required.Event_Coord1 = '-400'
event.required.Event_Coord2 = '300'
event.required.Event_C1Error = '4'
event.required.Event_C2Error = '4'
event.required.BoundBox_C1LL = '-440' ;Coordinates of lower-left
event.required.BoundBox_C2LL = '260'  ;Corner of bounding box
event.required.BoundBox_C1UR = '-360' ;Coordinates of upper-right    
event.required.BoundBox_C2UR = '340'  ;Corner of bounding box 

;If you want, add a description
event.description="My first flare"

;If you want, add up to ten references
;You must provide a name, link and type for each reference
;Must choose between "html", "image" and "movie" for reference_types.

event.reference_names[0] = "Publication" 
event.reference_links[0] = "http://adswww.harvard.edu/"
event.reference_types[0] = "html"

;Now export the IDL structure to an XML file.
export_event, event, /write, outfil="Flare_example.xml"
end