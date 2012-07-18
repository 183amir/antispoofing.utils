#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Fri Jul 13 14:30:00 CEST 2012

"""Calculates the LBPTop planes (XY,XT,YT) of the normalized faces in the videos in the REPLAY-ATTACK database. The result is the LBP histogram over all orthogonal frames of the video (XY,XT,YT). Different types of LBP operators are supported. The histograms can be computed for a subset of the videos in the database (using the protocols in REPLAY-ATTACK). The output is a single .hdf5 file for each video. The procedure is described in the paper: NAME OF THE PAPER.
"""

import os, sys
import argparse
import bob
import numpy

def main():

  import math
  
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

  INPUT_DIR = os.path.join(basedir, 'database')
  OUTPUT_DIR = os.path.join(basedir, 'lbp_features')

  protocols = bob.db.replay.Database().protocols()

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v', '--input-dir', metavar='DIR', type=str, dest='inputdir', default=INPUT_DIR, help='Base directory containing the videos to be treated by this procedure (defaults to "%(default)s")')

  parser.add_argument('-d', '--directory', dest="directory", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")

  parser.add_argument('-n', '--normface-size', dest="normfacesize", default=64, type=int, help="this is the size of the normalized face box if face normalization is used (defaults to '%(default)s')")

  parser.add_argument('--ff', '--facesize_filter', dest="facesize_filter", default=0, type=int, help="all the frames with faces smaller then this number, will be discarded (defaults to '%(default)s')")

  parser.add_argument('-l', '--lbptype', metavar='LBPTYPE', type=str, choices=('regular', 'riu2', 'uniform'), default='uniform', dest='lbptype', help='Choose the type of LBP to use (defaults to "%(default)s")')


  parser.add_argument('-nXY', '--neighborsXY', type=int, default=8, dest='nXY', help='Number of Neighbors in the XY plane (defaults to "%(default)s")')
  parser.add_argument('-nXT', '--neighborsXT', type=int, default=8, dest='nXT', help='Number of Neighbors in the XT plane (defaults to "%(default)s")')
  parser.add_argument('-nYT', '--neighborsYT', type=int, default=8, dest='nYT', help='Number of Neighbors in the YT plane (defaults to "%(default)s")')

  parser.add_argument('-rXY', '--radiusXY', type=int, default=1, dest='rXY', help='Radius of the XY plane (defaults to "%(default)s")')
  parser.add_argument('-rXT', '--radiusXT', type=int, default=1, dest='rXT', help='Radius of the XT plane (defaults to "%(default)s")')
  parser.add_argument('-rYT', '--radiusYT', type=int, default=1, dest='rYT', help='Radius of the YT plane (defaults to "%(default)s")')

  parser.add_argument('-cXY', '--circularXY', action='store_true', default=False, dest='cXY', help='Is circular neighborhood in XY plane?  (defaults to "%(default)s")')
  parser.add_argument('-cXT', '--circularXT', action='store_true', default=False, dest='cXT', help='Is circular neighborhood in XT plane?  (defaults to "%(default)s")')
  parser.add_argument('-cYT', '--circularYT', action='store_true', default=False, dest='cYT', help='Is circular neighborhood in YT plane?  (defaults to "%(default)s")')

  parser.add_argument('-vo', '--volume-face-detection', action='store_true', default=False, dest='volume_face_detection', help='With this option, only one face bounding box (the center frame) will be used for the volume analisys and the other frames will share the same bounding box. Otherwise the frames will use the respectives bounding boxes (defaults to "%(default)s")')

  parser.add_argument('--el', '--elbptype', metavar='ELBPTYPE', type=str, choices=('regular', 'transitional', 'direction_coded', 'modified'), default='regular', dest='elbptype', help='Choose the type of extended LBP features to compute (defaults to "%(default)s")')



  parser.add_argument('-b', '--blocks', metavar='BLOCKS', type=int, default=1, dest='blocks', help='The region over which the LBP is calculated will be divided into the given number of blocks squared. The histograms of the individial blocks will be concatenated.(defaults to "%(default)s")')

  parser.add_argument('-p', '--protocol', metavar='PROTOCOL', type=str, dest="protocol", default='grandtest', help='The REPLAY-ATTACK protocol type may be specified instead of the id switch to subselect a smaller number of files to operate on', choices=protocols)

  parser.add_argument('-o', dest='overlap', action='store_true', default=False, help='If set, the blocks on which the image is divided will be overlapping')

  args = parser.parse_args()

  lbphistlength = {'regular':256, 'riu2':10, 'uniform':59} # hardcoding the number of bins for the LBP variants

  from .. import spoof
  from .. import faceloc


  db = bob.db.replay.Database()

  if args.protocol:
    process = db.files(directory=args.inputdir, extension='.mov', protocol=args.protocol)
  else:
    process = db.files(directory=args.inputdir, extension='.mov')

  # where to find the face bounding boxes
  faceloc_dir = os.path.join(args.inputdir, 'face-locations')

  counter = 0

  # process each video
  for key, filename in process.items():
    counter += 1
    filename = os.path.expanduser(filename)
    input = bob.io.VideoReader(filename)
    
    # loading the face locations
    flocfile = os.path.expanduser(db.paths([key], faceloc_dir, '.face')[0])
    locations = faceloc.read_face(flocfile)
    locations = faceloc.expand_detections(locations, input.number_of_frames)
    sz = args.normfacesize # the size of the normalized face box

    sys.stdout.write("Processing file %s (%d frames) [%d/%d] " % (filename,
      input.number_of_frames, counter, len(process)))
    sys.stdout.flush()

    # start the work here...
    vin = input.load() # load the video
    
    #TODO: I SHOULD USE THAT
    #numvf = 0 # number of valid frames in the video (will be smaller then the total number of frames if a face is not detected or a very small face is detected in a frame when face lbp are calculated   
    
    volume_face_detection = args.volume_face_detection
    nXY = args.nXY
    nXT = args.nXT
    nYT = args.nYT

    rXY = args.rXY
    rXT = args.rXT
    rYT = args.rYT

    cXY = args.cXY
    cXT = args.cXT
    cYT = args.cYT

    lbptype =args.lbptype
    

    
    if(volume_face_detection):
      maxRadius = max(rXY,rXT,rYT) #Getting the max radius to extract the volume for analysis
      nFrames = vin.shape[0]
      
      #Converting all frames to grayscale
      grayFrames = numpy.zeros(shape=(nFrames,vin.shape[2],vin.shape[3]))
      for i in range(nFrames):
        grayFrames[i] = bob.ip.rgb_to_gray(vin[i,:,:,:])

      ### STARTING the video analysis
      #Analysing each sub-volume in the video
      histVolumeXY = None
      histVolumeXT = None
      histVolumeYT = None
      for i in range(maxRadius,nFrames-maxRadius):

        #Select the volume to analyse
        rangeValues = range(i-maxRadius,i+1+maxRadius)
        normalizedVolume = spoof.getNormFacesFromRange(grayFrames,rangeValues,locations,sz,args.facesize_filter)

        if(normalizedVolume==None):
          print("No frames in the volume " + filename)
          continue

        histXY,histXT,histYT = spoof.lbptophist(normalizedVolume,nXY,nXT,nYT,rXY,rXT,rYT,cXY,cXT,cYT,lbptype)

        if(histVolumeXY == None):
	  histVolumeXY = histXY
	  histVolumeXT = histXT
	  histVolumeYT = histYT
        else:
          histVolumeXY= numpy.concatenate((histVolumeXY, histXY),axis=0)
          histVolumeXT= numpy.concatenate((histVolumeXT, histXT),axis=0)
          histVolumeYT= numpy.concatenate((histVolumeYT, histXY),axis=0)
      
      #Saving the results into a file 
      histData = numpy.zeros(shape=(3,histVolumeXY.shape[0],histVolumeXY.shape[1]),dtype='float64')
      histData[0] = histVolumeXY
      histData[1] = histVolumeXT
      histData[2] = histVolumeYT

    else:
      #Extract the LBPTop of each frame using independent bounding boxes

      #Getting the gray and normalized face frames
      grayFaceNormFrameSequence = spoof.rgbVideo2grayVideo_facenorm(vin,locations,sz,bbxsize_filter=args.facesize_filter)

      histXY,histXT,histYT = spoof.lbptophist(grayFaceNormFrameSequence,nXY,nXT,nYT,rXY,rXT,rYT,cXY,cXT,cYT,lbptype)

      histData = numpy.zeros(shape=(3,histXY.shape[0],histXY.shape[1]),dtype='float64')
      histData[0] = histXY
      histData[1] = histXT
      histData[2] = histYT

    sys.stdout.write('\n')
    sys.stdout.flush()

    # saves the output
    db.save_one(key, histData, directory=args.directory, extension='.hdf5')


  return 0

if __name__ == "__main__":
  main()