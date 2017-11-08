import pickle
import os


# noinspection PyBroadException
def saveRoiToFile(roi_dict,savetofile):
    temp_dict = {}
    for roiparams in roi_dict:
        roilist = roi_dict[roiparams]
        savelist=[]
        for rois in roilist:
            things_to_save = (rois.roi_x1,rois.roi_y1,rois.roi_x2, rois.roi_y2)
            savelist.append(things_to_save)
        temp_dict[roiparams]=savelist
    with open(savetofile, 'wb') as data_out:
        try:
            pickle.dump(temp_dict, data_out, pickle.HIGHEST_PROTOCOL)
            print "Saved ",temp_dict," to file %s" % savetofile
        except:
            print "Error saving to file"


def readRoiFromFile(datafile):
    try:
        with open(datafile, 'rb') as data_read:
            datain = pickle.load(data_read)
            loadfine=True
            print datain,type(datain)
    except (pickle.UnpicklingError,IOError):
            datain=None
            loadfine=False

    return loadfine,datain

def delete_data_file(datafile):
    if os.stat(datafile)!=0 :
        os.remove(datafile)
        print "File %s deleted" % str(datafile)
    else:
        print "File %s already deleted" % str(datafile)

if __name__=='__main__':
    datfile = './.data/.roidata.pkl'
    print readRoiFromFile(datfile)


