#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: numael
"""

from trytond.model import ModelSQL, ModelSingleton, ModelView, fields
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, Button
from trytond.transaction import Transaction
from trytond.report import Report
from trytond.pool import Pool
from datetime import datetime
import os
import hashlib

__all__ = ['ThesaModules','ThesaModulesView','ViewResultThesaStart','ViewResultThesa']

_internal_version_="1.0"

class ThesaModulesView(ModelSingleton, ModelSQL, ModelView):
    'Thesa Modules View Config'
    __name__='thesamodule.config'
    title = fields.Char('title',readonly=True)
    internal_version = fields.Char('internal version',readonly=True)
    modules = fields.One2Many('thesamodule.thesamodule', 'module', 'Modules')
    
    @classmethod
    def __setup__(cls):
        super(ThesaModulesView, cls).__setup__()
        cls._buttons.update({
            'recharge': {},
            })
        
    @staticmethod
    def default_title():
        return 'thesa modules'
    
    @staticmethod
    def default_internal_version():
        return _internal_version_

    @classmethod
    @ModelView.button_action('thesamodule.wizard_view_result_thesa')
    def recharge(cls, ids):
        pass

class ThesaModules(ModelSQL, ModelView):
    'Thesa Modules'
    __name__='thesamodule.thesamodule'
    _rec_name='filename'
    filename = fields.Char('File Name', required=True, readonly=True)
    filebinary = fields.Binary('File store Qml', required=True, readonly=True)
    checksum = fields.Char('checksum', required=True, readonly=True)
    module = fields.Many2One('thesamodule.config','Module', ondelete='CASCADE', select=True, required=True)
    
    
class ViewResultThesaStart(ModelView):
    'View Result Thesa Start'
    __name__ = 'thesamodule.config_result_thesa.start'
    resumen = fields.Text(
        'Resumen Recharge', readonly=True)
    
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
        
#    result_ok = StateView(
#        'thesamodule.config_result_thesa.start',
#        'thesamodule.config_result_thesa_start_view_form', [
#            Button('Ok', 'end', 'tryton-ok', True),
#            ])
#    def default_result_ok(self, fields):
#        return {"resumen":"bien"}
    
    #recharge = StateTransition()
    @classmethod
    def __setup__(cls):
        super(ViewResultThesa, cls).__setup__()
        cls._error_messages.update({
                'filesnot': ('There are no files in the qml directory, if you continue delete the files already loaded in bd.'),
                })
    def default_start(self, fields):
        DIR_QML = os.path.abspath(os.path.normpath(os.path.join(__file__, '..', 'qml')))
        if os.path.isdir(DIR_QML):
            qmls = os.listdir(DIR_QML)
            rec_qml_files = Pool().get('thesamodule.thesamodule').search([])
            ThesaMod=Pool().get('thesamodule.thesamodule')
            thesamod = Pool().get('thesamodule.config').search([])[0]
            id_config = Pool().get('thesamodule.config').search([])[0].id
            
            if len(rec_qml_files)>0:
                if len(qmls)<=0:
                    self.raise_user_warning(
                            'nofiles',
                            'filesnot')
                ThesaMod.delete(rec_qml_files)
            if len(qmls)>0:
                for qml in qmls:
                    qmlpath=os.path.abspath(os.path.normpath(os.path.join(DIR_QML, qml)))
                    if os.path.isdir(qmlpath) == False:
                        data=""
                        md5_returned=""
                        error=False
                        try:
                            with open(qmlpath, "rb") as binary_file:
                                data = binary_file.read()
                                md5_returned = hashlib.md5(data).hexdigest()
                                ThesaMod.create([{"filename":qml,"filebinary":data, "checksum": md5_returned, "module":id_config}])
                        except:
                            if md5_returned=="" or data =="":
                                return {"resumen":"Error, file no read bytes"}
                            
            thesamod.title="Last Update: "+str(datetime.now())
            thesamod.save()
            return {"resumen":"The load was successful"}
            
        else:
            return {"resumen":"Error, no qml directory"}


