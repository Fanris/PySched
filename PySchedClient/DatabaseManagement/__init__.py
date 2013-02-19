# -*- coding: utf-8 -*-
'''
Created on 2012-12-04 14:54
@summary:
@author: Martin Predki
'''

from Common.Interfaces.DatabaseInterface import DatabaseInterface

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Tables import SqliteJob, SqliteProgram, Tables

from Common.DataStructures import Job, Program

import logging

class SqliteManager(DatabaseInterface):
    '''
    @summary: SQLite implementation of the base database manager.
    '''
    def __init__(self, workingDir):
        super(SqliteManager, self).__init__(workingDir)
        self.pathToDB = self.workingDir + "/PySchedClient.sqlite"
        self.engine = create_engine("sqlite:////{}".format(self.pathToDB))
        self.sessionClass = sessionmaker(bind=self.engine)
        self.tables = Tables(self.engine)
        self.tables.createAllTables()
        self.logger = logging.getLogger("PySchedClient")

        self.logger.info("Database up and running.")

    def addToDatabase(self, obj):
        self.logger.debug("Adding {} to database...".format(type(obj)))

        sqliteObject = None
        if isinstance(obj, Job):
            self.logger.debug("convert to SqliteJob".format())
            sqliteObject = SqliteJob.convertFromPySched(obj)

        if not sqliteObject:
            self.logger.error("Could not convert to SqliteObject".format())
            return

        s = self.sessionClass()
        s.add(sqliteObject)
        s.commit()
        obj = sqliteObject.convertToPySched()
        s.close()

        return obj

    def getFromDatabase(self, obj):
        self.logger.debug("Retrieving {} to database...".format(obj))

        sqliteObject = None
        if obj == Job:
            sqliteObject = SqliteJob
        elif obj == Program:
            sqliteObject = SqliteProgram

        self.logger.debug("selected SqliteObject: {}".format(sqliteObject))

        s = self.sessionClass()
        returnList = []

        query = s.query(sqliteObject)

        for item in query:
            self.logger.debug("Converting SqliteObject to PySchedObject".format())
            returnList.append(item.convertToPySched())

        s.close()

        return returnList

    def updateDatabaseEntry(self, obj):
        self.logger.debug("Updating object in database...")

        sqliteClass = None
        sqliteObject = None
        if isinstance(obj, Job):
            sqliteClass = SqliteJob
            sqliteObject = SqliteJob.convertFromPySched(obj)
        elif isinstance(obj, Program):
            sqliteClass = SqliteProgram
            sqliteObject = SqliteProgram.convertFromPySched(obj)

        s = self.sessionClass()

        self.logger.debug("Retieving {} object from database, where id={}".format(sqliteClass, sqliteObject.id))
        objectToUpdate = s.query(sqliteClass).filter(sqliteClass.id==sqliteObject.id).first()

        objectToUpdate.update(sqliteObject)

        s.flush()
        s.commit()
        returnObj = objectToUpdate.convertToPySched()
        s.close()

        return returnObj



