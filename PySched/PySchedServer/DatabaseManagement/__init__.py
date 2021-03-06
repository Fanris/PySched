# -*- coding: utf-8 -*-
'''
Created on 2012-12-04 14:54
@summary:
@author: Martin Predki
'''

from PySched.Common.Interfaces.DatabaseInterface import DatabaseInterface
from PySched.Common.DataStructures import Job, User, Compiler, Program

from Tables import SqliteJob, SqliteUser, SqliteCompiler, SqliteProgram, Tables

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import logging

class SqliteManager(DatabaseInterface):
    '''
    @summary: SQLite implementation of the base database manager.
    '''
    def __init__(self, workingDir):
        super(SqliteManager, self).__init__(workingDir)
        self.logger = logging.getLogger("PySchedServer")

        self.pathToDB = os.path.join(self.workingDir, "PySchedServer.sqlite")
        self.logger.debug("Checking database path: {}".format(self.pathToDB))
        self.engine = create_engine("sqlite:////{}".format(self.pathToDB))
        self.sessionClass = sessionmaker(bind=self.engine)
        self.tables = Tables(self.engine)
        self.tables.createAllTables()

        self.logger.info("Database up and running.")

    def addToDatabase(self, obj):
        self.logger.debug("Adding {} to database...".format(type(obj)))

        sqliteObject = None
        if isinstance(obj, Job):
            self.logger.debug("convert to SqliteJob".format())
            sqliteObject = SqliteJob.convertFromPySched(obj)
        elif isinstance(obj, User):
            self.logger.debug("convert to SqliteUser".format())
            sqliteObject = SqliteUser.convertFromPySched(obj)
        elif isinstance(obj, Compiler):
            self.logger.debug("convert to SqliteCompiler".format())
            sqliteObject = SqliteCompiler.convertFromPySched(obj)
        elif isinstance(obj, Program):
            self.logger.debug("convert to SqliteProgram".format())
            sqliteObject = SqliteProgram.convertFromPySched(obj)

        if not sqliteObject:
            self.logger.error("Could not convert to SqliteObject")
            return

        s = self.sessionClass()
        s.add(sqliteObject)
        s.commit()
        obj = sqliteObject.convertToPySched()
        s.close()

        self.logger.debug("Done.")
        return obj

    def getFromDatabase(self, obj):
        self.logger.debug("Retrieving {} to database...".format(obj))

        sqliteObject = None
        if obj == Job:
            sqliteObject = SqliteJob
        elif obj == User:
            sqliteObject = SqliteUser
        elif obj == Compiler:
            sqliteObject = SqliteCompiler
        elif obj == Program:
            sqliteObject = SqliteProgram

        if not sqliteObject:
            self.logger.debug("Something went wrong during database adding.")
            self.logger.debug("Selected sqliteObject: {}".format(sqliteObject))
            return None            

        self.logger.debug("selected SqliteObject: {}".format(sqliteObject))

        s = self.sessionClass()
        returnList = []

        query = s.query(sqliteObject)

        for item in query:
            self.logger.debug("Converting SqliteObject to PySchedObject")
            returnList.append(item.convertToPySched())

        s.close()

        self.logger.debug("Done.")
        return returnList

    def updateDatabaseEntry(self, obj):
        self.logger.debug("Updating object in database...")

        sqliteClass = None
        sqliteObject = None
        if isinstance(obj, Job):
            sqliteClass = SqliteJob
            sqliteObject = SqliteJob.convertFromPySched(obj)
        elif isinstance(obj, User):
            sqliteClass = SqliteUser
            sqliteObject = SqliteUser.convertFromPySched(obj)
        elif isinstance(obj, Compiler):
            sqliteClass = SqliteCompiler
            sqliteObject = SqliteCompiler.convertFromPySched(obj)

        if not sqliteClass or not sqliteObject:
            self.logger.debug("Something went wrong during database updating.")
            self.logger.debug("Selected sqliteClass: {}".format(sqliteClass))
            self.logger.debug("Selected sqliteObject: {}".format(sqliteObject))
            return None

        s = self.sessionClass()

        self.logger.debug("Retrieving {} object from database, where id={}".format(sqliteClass, sqliteObject.id))
        objectToUpdate = s.query(sqliteClass).filter(sqliteClass.id==sqliteObject.id).first()

        objectToUpdate.update(sqliteObject)

        s.flush()
        s.commit()
        returnObj = objectToUpdate.convertToPySched()
        s.close()

        self.logger.debug("Object updated.".format(sqliteClass, sqliteObject.id))
        return returnObj

    def deleteFromDatabase(self, obj):
        self.logger.debug("Deleting object from database...")

        sqliteClass = None
        sqliteObject = None
        if isinstance(obj, Job):
            sqliteClass = SqliteJob
            sqliteObject = SqliteJob.convertFromPySched(obj)
        elif isinstance(obj, User):
            sqliteClass = SqliteUser
            sqliteObject = SqliteUser.convertFromPySched(obj)
        elif isinstance(obj, Compiler):
            sqliteClass = SqliteCompiler
            sqliteObject = SqliteCompiler.convertFromPySched(obj)
        elif isinstance(obj, Program):
            sqliteClass = SqliteProgram
            sqliteObject = SqliteProgram.convertFromPySched(obj)

        if not sqliteClass or not sqliteObject:
            self.logger.debug("Something went wrong during database deleting.")
            self.logger.debug("Selected sqliteClass: {}".format(sqliteClass))
            self.logger.debug("Selected sqliteObject: {}".format(sqliteObject))
            return None            

        s = self.sessionClass()

        self.logger.debug("Retrieving {} object from database, where id={}".format(sqliteClass, sqliteObject.id))
        objectToDelete = s.query(sqliteClass).filter(sqliteClass.id==sqliteObject.id).first()

        s.delete(objectToDelete)
        s.flush()
        s.commit()
        s.close()

        self.logger.debug("Done.")
