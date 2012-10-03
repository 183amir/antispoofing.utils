#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
# Tue 01 Oct 2012 16:48:44 CEST 

"""
Abstract class that define some method for the antispoofing databases
"""
import abc
import bob
import xbob.db.casia_fasd

from antispoofing.utils.db import *

class CasiaFASD(Database):

  def __init__ (self,args):
    self.__db = xbob.db.casia_fasd.Database()

    self.__kwargs = {
      'types': args.casiaTypes,
      'fold_no': 1,
    }


  @staticmethod
  def name():
    """
    Defines the name of the object
    """
    return "casia_fasd"


  @staticmethod
  def create_subparser(subparser):
    """
    Creates a parser for the central manager taking into consideration the options for every module that can provide those
    """
    parser_casia = subparser.add_parser(CasiaFASD.name(), help='Casia FASD database')
    parser_casia.add_argument('--types', type=str, choices=('warped', 'cut', 'video', ''), default='', dest='casiaTypes', help='Defines the types of attack videos in the database that are going to be used.')

    parser_casia.set_defaults(which=CasiaFASD.name())

    return


  def get_train_data(self):
    """
    Will return the real access and the attack File objects (xbob.db.<database>.File) for training the antispoofing classifier
    """
    types, fold_no = self.__parseArguments()

    _,trainReal   = self.__db.cross_valid_foldobjects(cls='real', fold_no=fold_no)
    _,trainAttack = self.__db.cross_valid_foldobjects(cls='attack', types=types, fold_no=fold_no)

    return trainReal,trainAttack


  def get_devel_data(self):
    """
    Will return the real access and the attack File objects (xbob.db.<database>.File) for development (supposed to tune the antispoofing classifier)
    """
    types, fold_no = self.__parseArguments()

    develReal,_   = self.__db.cross_valid_foldobjects(cls='real', fold_no=fold_no)
    develAttack,_ = self.__db.cross_valid_foldobjects(cls='attack', types=types, fold_no=fold_no)

    return develReal,develAttack


  def get_test_data(self):
    """
    Will return the real access and the attack File objects (xbob.db.<database>.File) for test (supposed to report the results)
    """
    types,_ = self.__parseArguments()

    testReal    = self.__db.objects(groups='test', cls='real')
    testAttack  = self.__db.objects(groups='test', cls='attack', types=types)

    return testReal,testAttack


  def __parseArguments(self):

    #If crashes, return all objects    
    try:
      types = self.__kwargs['types']
      if types == '':
        types = ('warped', 'cut','video')
    except:
        types = ('warped', 'cut','video')

    try:
      fold_no = self.__kwargs['fold_no']
      if fold_no == '':
        fold_no = 1
    except:
      fold_no = 1

    return types, fold_no
