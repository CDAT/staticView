#!/usr/bin/env python
import vcs, cdms2, os, sys
###############################################################################
#                                                                             #
# Module:       Generate PNG files from netCDF files and the HTML file to     #
#               display the PNG files in the current directory.               #
#                                                                             #
# Authors:      Analytics and Informatics Mangement Systems (AIMS)            #
#               Software Team                                                 #
#               Lawrence Livermore NationalLaboratory:                        #
#               uv-cdat.org                                                   #
#                                                                             #
# Description:  Python script to generate PNG plots from netCDF files that    #
#               are contained in the current directory. The script will       #
#               attemp to generate a PNG file for each variable contained     #
#               within the netCDF file. It will also generate a HTML file     #
#               to display all the generated PNG files via a web browser.     #
#                                                                             #
#                                                                             #
###############################################################################
#

#############################################################################
#                                                                           #
# Determine if the PNGs directory exist. If it exists, then remove the      #
# contents of the directory and replace wih all new PNG files.              #
#                                                                           #
#############################################################################
cdir = os.getcwd()
png_dir = cdir + '/PNGs'
try:
    os.stat(png_dir)
    os.chdir(png_dir)
    lpngs = os.listdir('./')
    for l in lpngs: os.remove(l)  # remove old PNG files
    os.chdir(cdir)
except:
    os.mkdir(png_dir) 

#############################################################################
#                                                                           #
# Get the list of netCDF files in the current directory                     #
#                                                                           #
#############################################################################
dirList = os.listdir(cdir)
ncList = []
for x in dirList:
   if x.find('.nc') > 1: ncList.append(x)

#############################################################################
#                                                                           #
# Initialize VCS and set the colormap                                       #
#                                                                           #
#############################################################################
v = vcs.init()
tm = v.gettemplate('UVWG')
gm = v.getisofill('quick')
v.setcolormap('bl_to_darkred')

#############################################################################
#                                                                           #
# Open each netCDF file and create its cooresponding PNG with regards to    #
# the variables it contain.                                                 #
#                                                                           #
#############################################################################
can_list = []
sqz_list = []
not_list = []
var_dic  = {}             # dictionary used for generating the HTML file variable list
cdms2.setAutoBounds('on')  # lots of axes have no bounds (but should)
for x in ncList:
   f=cdms2.open(x)       # open netCDF file #
   vars = f.listvariables()    # list the varibles in the file #
   for var in vars:
      try:          # Generate PNGs for valid variables #
         d=f(var, longitude=(-180, 180), latitude = (-90., 90.))
         var_dic[var] = d.long_name + ' [' + d.units+ ']'
         png_filename = png_dir + '/' + x[0:x.find('.nc')] + '_' + var
         v.plot(d, tm, gm, bg = 1)
         v.png(png_filename)
         v.clear()
         can_list.append(x + ': ' + var)
      except:
          try:
             d=f(var, longitude=(-180, 180), latitude = (-90., 90.), squeeze=1 )
             var_dic[var] = d.long_name + ' [' + d.units+ ']'
             dax = [a[0] for a in d._TransientVariable__domain]
             if dax[0].isLevel() and dax[1].isLatitude() and dax[2].isLongitude():
                 # the most common case of a 3-D variable, but not the only one!
                 d = cdutil.averager(d,'('+dax[0].id+')')
             png_filename = png_dir + '/' + x[0:x.find('.nc')] + '_' + var
             v.plot(d, tm, gm, bg = 1)
             v.png(png_filename)
             v.clear()
             sqz_list.append(x + ': ' + var)
          except:       # if the variable is not valid, then skip over them #
              not_list.append(x + ': ' + var)
              pass
   f.close()        # close netCDF file #

   # used for plotting verification
   print 'Plotted as given: \n', can_list
   print 'Plotted after transformations: \n', sqz_list
   print 'Cannot plot list: \n', not_list

#############################################################################
#                                                                           #
# Modify the ACME_HTML_SRC.txt file to include the variable information     #
# for user plot selection.                                                  #
#                                                                           #
#############################################################################

fi = open("ACME_HTML_SRC.txt")         # open the source HTML file
lines = fi.readlines()
fo = open("ACME_climo.html", "w")

# modify the HTML with the appropriate variable and selection information
ct = 1
vars.sort()
create_variable_list = 0
create_month_season_list = 0
for l in lines:
   if create_month_season_list == 1:     # show the appropriate months and seasons
      for n in ncList:
         copy_n = l
         copy_n = copy_n.replace('NVAL', n[11:13])
         copy_n = copy_n.replace('NTEXT', n[11:13])
         fo.write(copy_n)
         ct += 1
      create_month_season_list = 0
   elif create_variable_list == 1:        # show the variable list
      for v in vars:
         try:
            copy_v = l
            copy_v = copy_v.replace('VNAME', v)
            copy_v = copy_v.replace('VTEXT', v + ' - ' + var_dic[v])
            fo.write(copy_v)
            ct += 1
         except:
            pass
      create_variable_list = 0
   else:
     fo.write( l )
     if l[:25]  == "<!-- CREATE VARIABLE LIST": create_variable_list=1
     if l[:29]  == "<!-- CREATE MONTH SEASON LIST": create_month_season_list=1
     ct += 1

fi.close()
fo.close()

#---------------------------------------------------------------------
# End of File
#---------------------------------------------------------------------
