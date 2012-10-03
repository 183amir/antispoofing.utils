#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
# Tue 01 Oct 2012 16:48:44 CEST 

"""
Abstract class that define some method for the antispoofing databases
"""
import abc
import bob
import xbob.db.replay

from antispoofing.utils.db import *

class Replay(Database):

  def __init__ (self,args):
    self.__db = xbob.db.replay.Database()

    self.__kwargs = {
      'protocol': args.replayProtocol,
      'support':  args.replaySupport,
      'light': args.replayLight,
    }


  @staticmethod
  def name():
    """
    Defines the name of the object
    """
    return "replay"


  @staticmethod
  def create_subparser(subparser):
    """
    Creates a parser for the central manager taking into consideration the options for every module that can provide those
    """
    protocols = xbob.db.replay.Database().protocols()
    protocols = [p.name for p in protocols]


    parser_replay = subparser.add_parser(Replay.name(), help='Replay attack database')
    parser_replay.add_argument('--protocol', type=str, dest="replayProtocol", default='grandtest', help='The REPLAY-ATTACK protocol type may be specified   instead of the id switch to subselect a smaller number of files to operate on', choices=protocols)

    parser_replay.add_argument('--support', type=str, choices=('fixed', 'hand'), default='', dest='replaySupport', help='One of the valid supported attacks (fixed, hand) (defaults to "%(default)s")')

    parser_replay.add_argument('--light', type=str, choices=('controlled', 'adverse'), default='', dest='replayLight', help='Types of illumination conditions (controlled,adverse) (defaults to "%(default)s")')

  
    parser_replay.set_defaults(which=Replay.name()) #Help to choose which subparser was selected
        
    return


  def get_train_data(self):
    """
    Will return the real access and the attack File objects (xbob.db.<database>.File) for training the antispoofing classifier
    """

    trainReal   = self.__db.objects(groups='train', cls='real',**self.__kwargs)
    trainAttack = self.__db.objects(groups='train', cls='attack',**self.__kwargs)

    return trainReal,trainAttack


  def get_devel_data(self):
    """
    Will return the real access and the attack File objects (xbob.db.<database>.File) for development (supposed to tune the antispoofing classifier)
    """
    develReal   = self.__db.objects(groups='devel', cls='real',**self.__kwargs)
    develAttack = self.__db.objects(groups='devel', cls='attack',**self.__kwargs)

    return develReal,develAttack


  def get_test_data(self):
    """
    Will return the real access and the attack File objects (xbob.db.<database>.File) for test (supposed to report the results)
    """

    testReal    = self.__db.objects(groups='test', cls='real',**self.__kwargs)
    testAttack  = self.__db.objects(groups='test', cls='attack',**self.__kwargs)

    return testReal,testAttack


