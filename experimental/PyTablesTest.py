#from tables import *
#import unittest
#
## Describe a water class
#class Water(IsDescription):
#    waterbody_name = StringCol(16, pos=1) # 16-character String
#    lati = Int32Col(pos=2) # integer
#    longi = Int32Col(pos=3) # integer
#    airpressure = Float32Col(pos=4) # float (single-precision)
#    temperature = Float64Col(pos=5) # double (double-precision)
#
#
## Open a file in "w"rite mode
#fileh = openFile("myadd-column.h5", mode = "w")
## Create a new group
#group = fileh.createGroup(fileh.root, "newgroup")
#
## Create a new table in newgroup group
#table = fileh.createTable(group, 'table', Water, "A table", Filters(1))
#
## Append several rows
#table.append([("Atlantic", 10, 0, 10*10, 10**2),
#              ("Pacific", 11, -1, 11*11, 11**2),
#              ("Atlantic", 12, -2, 12*12, 12**2)])
#
#print "Contents of the original table:", fileh.root.newgroup.table[:]
#
## Create another table but this time in the root directory
#tableroot = fileh.createTable(fileh.root, 'root_table', Water, "A table at root", Filters(1))
#
## Append data...
#tableroot.append([("Mediterranean", 10, 0, 10*10, 10**2),
#                  ("Mediterranean", 11, -1, 11*11, 11**2),
#                  ("Adriatic", 12, -2, 12*12, 12**2)])
#
## close the file
#
## close the file
#fileh.close()
#
## Open it again in append mode
#fileh = openFile("myadd-column.h5", "a")
#group = fileh.root.newgroup
#table = group.table
#
## Get a description of table in dictionary format
#descr = table.description._v_colObjects
#descr2 = descr.copy()
#
## Add a column to description
#descr2["hot"] = BoolCol(dflt=False)
#
## Create a new table with the new description
#table2 = fileh.createTable(group, 'table2', descr2, "A table", Filters(1))
#
## Copy the user attributes
#table.attrs._f_copy(table2)
#
## Fill the rows of new table with default values
#for i in xrange(table.nrows):
#    table2.row.append()
## Flush the rows to disk
#table2.flush()
#
## Copy the columns of source table to destination
#for col in descr:
#    getattr(table2.cols, col)[:] = getattr(table.cols, col)[:]
#
## Fill the new column
#table2.cols.hot[:] = [ row["temperature"] > 11**2 for row in table ]
#
## Remove the original table
#table.remove()
#
## Move table2 to table
#table2.move('/newgroup','table')
#
## Print the new table
#print "Contents of the table with column added:", fileh.root.newgroup.table[:]
#
## Finally, close the file
#fileh.close()
#
#
#class PyTablesTest(unittest.TestCase):
#    def testWriteHdf(self):
#        filename = "tutorial1.h5"
#        h5file = openFile(filename, mode = "w", title = "Test file")
#        group = h5file.createGroup("/", 'detector', 'Detector information')
#        table = h5file.createTable(group, 'readout', Particle, "Readout example")
#        particle = table.row
#        for i in xrange(10):
#            particle['name']  = 'Particle: %6d' % (i)
#            particle['TDCcount'] = i % 256
#            particle['ADCcount'] = (i * 256) % (1 << 16)
#            particle['grid_i'] = i
#            particle['grid_j'] = 10 - i
#            particle['pressure'] = float(i*i)
#            particle['energy'] = float(particle['pressure'] ** 4)
#            particle['idnumber'] = i * (2 ** 34)
#            particle.append()
#        table.flush()
#        h5file.close()
#
## Define a user record to characterize some kind of particles
#class Particle(IsDescription):
#    name      = StringCol(16)   # 16-character String
#    idnumber  = Int64Col()      # Signed 64-bit integer
#    ADCcount  = UInt16Col()     # Unsigned short integer
#    TDCcount  = UInt8Col()      # unsigned byte
#    grid_i    = Int32Col()      # integer
#    grid_j    = Int32Col()      # integer
#    pressure  = Float32Col()    # float  (single-precision)
#    energy    = Float64Col()    # double (double-precision)