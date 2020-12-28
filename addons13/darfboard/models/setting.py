# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
import logging
# from fingerprint import Fingerprint
from dateutil import relativedelta
from datetime import datetime as dt
from dateutil import parser
import xlsxwriter
# import StringIO
from io import BytesIO
import base64
import hashlib
import xmltodict
from math import modf
from lxml import etree
from xml.etree.ElementTree import fromstring
from json import dumps
import json
import requests
import base58
from subprocess import call
import subprocess
import os
import ast
from odoo.exceptions import UserError
from web3.auto import w3
from web3 import Web3, HTTPProvider, IPCProvider
import ipfsapi
import io
# from odoo.report.preprocess import report

_logger = logging.getLogger(__name__)


class SettingOfJournals(models.Model):
    
    _name = 'setting.journals'
    
    name = fields.Char(string="Name of report for analysis")
    list_of_parameters = fields.One2many('list.of.parameters','parameter_id') 
    ethereum_pk = fields.Char(string="Ethereum smart contract address")   
    ethereum_node_address = fields.Char(string="Ethereum node address")
    ethereum_address = fields.Char(string="Smart Contract Interface")
    gas_limit = fields.Float(string='Gas limit',compute='_gas_limit')
    gas_spent = fields.Float(string='Gas will be spent',compute='_gas_spent')
    send_period = fields.Selection([
            ('day', 'Every day'),
            ('week', 'Weekly'),
            ('month','Monthly'),
            ('Period','Time period of synchronization')],string="Period of synchronization")
    week_day = fields.Selection([
            ('0', 'Mn'),
            ('1', 'Tu'),
            ('2', 'We'),
            ('3', 'Th'),
            ('4', 'Fr'),
            ('5', 'Sd'),
            ('6', 'Sun')
        ],
        string="Day of week")
    send_time = fields.Float(string="Time")
    time_period = fields.Float(string="Time period")
    send_date = fields.Integer(string='Day of month')
    last_send_date = fields.Date(string="Date of last synchronization")
    last_send_time = fields.Float(string="Time of last synchronization")
    xml_for_synchronization = fields.Text(string="XML for synchronization")
    
    def _gas_limit(self):
        address_node = self.ethereum_node_address
        web3 = Web3(HTTPProvider(address_node))
        abi_json = self.ethereum_address
        ethereum_contract_address = self.ethereum_pk
        print(ethereum_contract_address)
        contract =  web3.eth.contract(abi = json.loads(abi_json), address=ethereum_contract_address)
        try:
            result_of_gas_limit = contract.call().getGasLimit()
        except:
            result_of_gas_limit = 0
        self.gas_limit = result_of_gas_limit
    
    def _gas_spent(self):
        date_of_synchronization = dt.now()
        address_node = self.ethereum_node_address
        web3 = Web3(HTTPProvider(address_node))
        abi_json = self.ethereum_address
        ethereum_contract_address = self.ethereum_pk
        print(ethereum_contract_address)
        contract = web3.eth.contract(abi=json.loads(abi_json), address=ethereum_contract_address)
        hash_of_synchronaze = '"'+ str(base58.b58encode(str(date_of_synchronization))) +'"'
        print(hash_of_synchronaze)
        try:
            result_of_gas_estimate = contract.estimateGas().setData(str(hash_of_synchronaze))
        except:
            result_of_gas_estimate = 0
        self.gas_spent = result_of_gas_estimate
    
    def sand_report(self):
        print("test sand report")
        date_of_synchronization = dt.now()
        general_info_text = str(date_of_synchronization)
        root = etree.Element("data")
        general_info = etree.SubElement(root,'general_info')
        general_info.text=general_info_text
        #------------------------------------------ create subelement for report
        report = etree.SubElement(root, 'report')
        report.set("name",self.name)
        
        for item_list in self.list_of_parameters:
            parameter = etree.SubElement(report,'parameter')
            parameter.set("name",item_list.name)
            
            journals = etree.SubElement(parameter,'journals')
            
            for item_journal in item_list.journal_list:
                journal = etree.SubElement(journals,'journal')
                journal.set("name",item_journal.name)
                if item_journal.default_debit_account_id.code:
                    debit = etree.SubElement(journal,'debit')
                    debit.set("code",item_journal.default_debit_account_id.code)
                    debit.set("name",item_journal.default_debit_account_id.name)
                for item_account_move in self.env['account.move'].search([('journal_id','=',item_journal.id)]):
                    entry = etree.SubElement(journal, 'entry')
                    entry.set("number",item_account_move.name)
                    date = etree.SubElement(entry,'date')
                    date.text = item_account_move.date
                    for item_entry in item_account_move.line_ids:
                        entry_item = etree.SubElement(entry,'entry_item')
                        entry_item.set("name",item_entry.name)
                        account_code = etree.SubElement(entry_item,'code')
                        account_code.text = item_entry.account_id.code
                        account_name = etree.SubElement(entry_item,'name')
                        account_name.text = item_entry.account_id.name
                        debit_item = etree.SubElement(entry_item,'dabit')
                        debit_item.text = str(item_entry.debit)
                        credit_item = etree.SubElement(entry_item,'credit')
                        credit_item.text = str(item_entry.credit)
                        quantity_item = etree.SubElement(entry_item,'quantity')
                        quantity_item.text = str(item_entry.quantity)
                        
                        
                    
        self.xml_for_synchronization = etree.tostring(root, pretty_print=True)
        xml_result = etree.tostring(root)
        apifs_node_api = ipfsapi.Client('localhost',5001)
        with io.open('tmp.json', 'w', encoding='utf-8') as f:
            result_of_file = f.write(str(xml_result))
        print("test of save ipfs")
        res = apifs_node_api.add('tmp.json')
        print('Address of IPFS')
        print(res)
        result_save_address = str(res['Hash']) 
        _logger.info('ethereum')
        address_node = self.ethereum_node_address
        web3 = Web3(HTTPProvider(address_node))
        abi_json = self.ethereum_address
        ethereum_contract_address = self.ethereum_pk
        contract = web3.eth.contract(abi = json.loads(abi_json), address=ethereum_contract_address)
        hash_of_synchronaze = '"'+ str(base58.b58encode(general_info_text)) +'"'
        print(hash_of_synchronaze)
        result_save_address = '"'+result_save_address+'"'
        #TransactionHashEthereum = contract.transact().setData(str(hash_of_synchronaze))
        address_of_file = contract.transact().setDocumentIPFSAddress(result_save_address)
        
        
class ListOfParameter(models.Model):
    
    _name='list.of.parameters'
    
    name = fields.Char()
    parameter_id = fields.Many2one('setting.journal',default=lambda self: self._context.get('parameter_id', self.env['setting.journals']))
    journal_list = fields.Many2many('account.journal',string="Select Journal for analysis")

