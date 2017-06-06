# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import tools
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)



class product_template(models.Model):
    _inherit = 'product.template'

    public_categ_ids = fields.Many2many('product.public.category', 'product_category_product_product','product_id','product_category_id',string='Related product', readonly=True,copy=False,store=True)

class product_public_category(models.Model):
    _inherit = 'product.public.category'

    @api.model 
    def update_all(self):
        
        # Update product in category with domain
        category_domain_ids = self.env['product.public.category'].search([('domain_on_child','=',False),('domain','!=',False)])
        
        for category in category_domain_ids:
            #_logger.warning('update public category - %s', category.name)
            domainList = eval(category.domain)
            domainList = [x for x in domainList]
            product_ids = self.env['product.template'].search(domainList)
            category.update({'product_ids' : [[6,0,product_ids.ids]]})
        
        # Update product in category with domain on child
        category_domain_ids = self.env['product.public.category'].search([('domain_on_child','=',True)])
        for category in category_domain_ids:
            child_category_ids = self.env['product.public.category'].search([('id','child_of',category.id)])
            product_ids = []
            
            for child_category in child_category_ids:
                if not child_category.domain_on_child:
                    product_ids = product_ids + child_category.product_ids.ids
                    
            #Delete double
            product_ids=list(set(product_ids)) 
            category.update ({'product_ids' : [[6,0,product_ids]]})

    @api.multi
    def refresh_category(self):
        _logger.warning('update public category - %s', self.name)
        
        child_category_ids = self.env['product.public.category'].search([('id','child_of',self.id)])
        product_ids = []
        
        for child_category in child_category_ids:
            if not child_category.domain_on_child:
                product_ids = product_ids + child_category.product_ids.ids
                
        #Delete double
        product_ids=list(set(product_ids))        
        
        vals = {'product_ids' : [[6,0,product_ids]]}
        return super(product_public_category, self).write(vals)
        
    @api.multi
    def write(self, vals):

        #  UPDATE CURRENT CATEGORY
        #--------------------------
                
        _logger.warning('update public category - %s', self.name)
        if 'domain_on_child' in vals:
            on_child = vals['domain_on_child']
        else:
            on_child= self.domain_on_child

        if 'domain' in vals:
            new_domain = vals['domain']
        else:
            new_domain= self.domain
        
        #if domain on child
        if on_child:
            child_category_ids = self.env['product.public.category'].search([('id','child_of',self.id)])
            product_ids = []
            
            for child_category in child_category_ids:
                if not child_category.domain_on_child:
                    product_ids = product_ids + child_category.product_ids.ids
                    
            #Delete double
            product_ids=list(set(product_ids)) 
            vals.update ({'product_ids' : [[6,0,product_ids]]})
                   
            
        else:
            if new_domain:
                domainList = eval(new_domain)
                domainList = [x for x in domainList]
                product_ids = self.env['product.template'].search(domainList)
                vals.update ({'product_ids' : [[6,0,product_ids.ids]]})
                #self.product_ids=product_ids
            else:
                product_ids=[]
                vals.update ({'product_ids' :[[6,0,product_ids]]})
                #self.product_ids=False
        
        super(product_public_category, self).write(vals)
        
        #  UPDATE PARENT CATEGORY
        #--------------------------
        parent_category_ids = self.env['product.public.category'].search([('id','parent_of',self.parent_id.id)])

        for parent_category in parent_category_ids:
            if parent_category.domain_on_child:
                parent_category.refresh_category()
        
        return True
        
    domain_on_child = fields.Boolean('Domain on child')
    domain = fields.Char('Domain')
    product_ids =   fields.Many2many('product.template', 'product_category_product_product','product_category_id','product_id',string='Related product', copy=False,store=True)


