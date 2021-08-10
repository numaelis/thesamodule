# -*- coding: utf-8 -*-
# This file is part of the thesa nodule module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
__author__ = "Numael Garay"
__license__ = "GPL"
__version__ = "1.3" 
__maintainer__ = "Numael Garay" 
__email__ = "mantrixsoft@gmail.com"


from trytond.model import ModelSQL, ModelSingleton, ModelView, fields
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, Button
from trytond.transaction import Transaction
from trytond.report import Report
from trytond.pool import Pool
from trytond.pyson import Eval, Or
from trytond.exceptions import UserError, UserWarning
from datetime import datetime
import os
import hashlib

__all__ = ['ThesaModules','ThesaModulesView','ThesaUsersFolder','ThesaGroupUsers','ViewResultThesaStart','ViewResultThesa']
           # 'ThesaUpdateLine', 'ThesaUpdate']

_internal_version_="1.3"

# _tryton50=True

class ThesaUsersFolder(ModelSQL, ModelView):
    'Thesa Users Folder'
    __name__='thesamodule.usersfolder'
    activefolder = fields.Boolean('Active Folder', select=True)
    type = fields.Selection([
        ('group', 'Group'),
        ('default', 'Default'),
        ], 'Type', required=True)
    configuser = fields.Many2One('thesamodule.config','User Config',  required=True)
    users = fields.One2Many('thesamodule.groupusers', 'userfolder' ,'Users',states={
            'readonly': Eval('type') == 'default',
            })
    
    foldername = fields.Char('Folder Name', required=True, states={
            'readonly': Eval('type') == 'default',
            })
    qmlfiles = fields.One2Many('thesamodule.thesamodule', 'qmlfile', 'Qml Files', readonly=True)
    
    @classmethod
    def __setup__(cls):
        super(ThesaUsersFolder, cls).__setup__()
        # if _tryton50 == False:
        #     cls._error_messages.update({
        #             'multiuser': ' the user: %s is already assigned in: folder %s',
        #             })
    @staticmethod
    def default_activefolder():
        return True
    
    @fields.depends('type','foldername')
    def on_change_type(self):
        if self.type == 'default':
            self.foldername = 'default'
            
    @classmethod
    def write(cls, *args):
        alluserbd=[]
        mapname={}
        allufs = Pool().get('thesamodule.usersfolder').search([])
        for alluf in allufs:
            if alluf.users:                
                for user in alluf.users:
                    alluserbd.append(user.user.id) 
                    mapname[user.user.id] = user.user.name
        actions = iter(args)
        for UserForders, values in zip(actions, actions):    
            if "users" in values:
                for value in values["users"]:
                    if value[0]=='create':
                        for user in value[1]:
                            if 'user' in user:
                                if user['user'] in alluserbd:
                                    Folder  = Pool().get('thesamodule.usersfolder').search([
                                            ["users.user.id","=",user['user']]
                                        ])
                                    folder = Folder[0].foldername
                                    #gettext(#
                                    raise UserError(' the user: %s is already assigned in: folder %s'%(mapname[user['user']], folder))
        super(ThesaUsersFolder, cls).write(*args)
        
        
class ThesaModulesView(ModelSingleton, ModelSQL, ModelView):
    'Thesa Modules View Config'
    __name__='thesamodule.config'
    title = fields.Char('title',readonly=True)
    internal_version = fields.Function(fields.Char('internal version'),'get_internal_version')
    modules = fields.One2Many('thesamodule.thesamodule', 'module', 'Modules')
    deletecache = fields.Boolean('Delete Cache Qml On Load')
    configusers = fields.One2Many('thesamodule.usersfolder', 'configuser', 'Users Config')
    @classmethod
    def __setup__(cls):
        super(ThesaModulesView, cls).__setup__()
        cls._buttons.update({
            'rechargeAll': {},
            })
        
    @staticmethod
    def default_title():
        return 'thesa modules'
            
    def get_internal_version(self, name):
        return _internal_version_
    
    @classmethod
    @ModelView.button_action('thesamodule.wizard_view_result_thesa')
    def rechargeAll(cls, ids):
        pass

class ThesaModules(ModelSQL, ModelView):
    'Thesa Modules'
    __name__='thesamodule.thesamodule'
    _rec_name='filename'
    filename = fields.Char('File Name', required=True, readonly=True)
    filebinary = fields.Binary('File store Qml', required=True, readonly=True)
    checksum = fields.Char('checksum', required=True, readonly=True)
    module = fields.Many2One('thesamodule.config','Module',required=False)
    qmlfile = fields.Many2One('thesamodule.usersfolder','Qml File',  select=True, required=True, readonly=True, ondelete='CASCADE')#ondelete='CASCADE',

#only one default
#only one user for folder

class ThesaGroupUsers(ModelSQL, ModelView):
    'Thesa Group Users'
    __name__='thesamodule.groupusers'
    userfolder = fields.Many2One('thesamodule.usersfolder', 'Folder', required = True, ondelete='CASCADE')
    user = fields.Many2One('res.user','User', required = True)

# class ThesaUpdateLine(ModelSQL, ModelView):
#     'Thesa Update Lines'
#     __name__='thesamodule.updateline'
#     _rec_name='filename'
#     filename = fields.Char('File Name', required=True, readonly=True)
#     filebinary = fields.Binary('File store Qml', required=True, readonly=True)
#     checksum = fields.Char('checksum', required=True, readonly=True)
#     update = fields.Many2One('thesamodule.update','Update', required = True)
    
# class ThesaUpdate(ModelSQL, ModelView):
#     'Thesa Update'
#     __name__='thesamodule.update'
#     type = fields.Selection([
#         ('core', 'Core'),
#         ('tools', 'Tools'),
#         ('locale', 'Locale'),
#         ], 'Type', required=True)
#     date = fields.Date('Date', required=True)
#     lines = fields.One2Many('thesamodule.updateline', 'update' ,'Files Update')
    
#     @staticmethod
#     def default_type():
#         return 'tools'
    
class ViewResultThesaStart(ModelView):
    'View Result Thesa Start'
    __name__ = 'thesamodule.config_result_thesa.start'
    resumen = fields.Text('Resumen Recharge', readonly=True)
    
    @staticmethod
    def default_resumen():
        result="init recharge..."
        return result
    
class ViewResultThesa(Wizard):
    'View Result Thesa'
    __name__ = 'thesamodule.config_result_thesa'
    start_state = 'start'
    start = StateView(
        'thesamodule.config_result_thesa.start',
        'thesamodule.config_result_thesamod_start_view_form', [
           # Button('Cancel', 'end', 'tryton-cancel'),
            Button('Ok', 'end', 'tryton-ok', True),
            ])
    
    def end(self):
        return 'reload'
    
    @classmethod
    def __setup__(cls):
        super(ViewResultThesa, cls).__setup__()
        #     cls._error_messages.update({
        #             'nofiles': (' There are no files in the qml directory, if you continue delete the files already loaded in bd.'),
        #             'nofolder': ' qml folder: %s does not exist for this user group',
        #             })
    def default_start(self, fields):
        DIR_QML = os.path.abspath(os.path.normpath(os.path.join(__file__, '..', 'qml')))
        if os.path.isdir(DIR_QML):
            rec_qml_files = Pool().get('thesamodule.thesamodule').search([])
            ThesaMod=Pool().get('thesamodule.thesamodule')
            thesaconfig = Pool().get('thesamodule.config').search([])[0]
            if len(rec_qml_files)>0:
                # if len(qmls)<=0:
                #     self.raise_user_warning(self.id,
                #             'nofiles',
                #             'nofiles')
                ThesaMod.delete(rec_qml_files)
            usersFolder = Pool().get('thesamodule.usersfolder').search([])
            allok=True
            qmls=[]
            warnings = ""
            for userfolder in usersFolder:
                pathfolder = os.path.join(DIR_QML, userfolder.foldername)
                if os.path.isdir(pathfolder):
                    qmls = os.listdir(pathfolder)
                    for qml in qmls:
                        qmlpath=os.path.join(pathfolder, qml)#os.path.abspath(os.path.normpath(os.path.join(pathfolder, qml)))
                        if os.path.isdir(qmlpath) == False:# is file!
                            data=""
                            md5_returned=""
                            try:
                                with open(qmlpath, "rb") as binary_file:
                                    data = binary_file.read()
                                    md5_returned = hashlib.md5(data).hexdigest()                                        
                                    ThesaMod.create([{"filename":qml,"filebinary":data, "checksum": md5_returned, "module":1 ,"qmlfile":userfolder.id}])
                                    userfolder.save()
                            except:
                                allok=False
                                if md5_returned=="" or data =="":
                                    return {"resumen":"Error, file no read bytes"}
                else:
                    warnings+= " " + userfolder.foldername
            if allok == True and len(qmls)>0:
                thesaconfig.title="Last Update: "+str(datetime.now())
                thesaconfig.save()
                if warnings!="":
                    warnings = "\nWARNING! qml folders: %s , not found!"%(warnings)
                return {"resumen":"The load was successful, may have to reload to see the changes"+warnings}
            else:
                return {"resumen":"Error, read files"}
        else:
            return {"resumen":"Error, no qml directory"}


