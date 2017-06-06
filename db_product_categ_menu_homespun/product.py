# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import tools
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class product_public_category(models.Model):
    _inherit = ["product.public.category"]
    _name = 'product.public.category'

    is_published = fields.Boolean(string='Published', default=True)


class product_template(models.Model):
    _inherit = "product.template"

    @api.depends("public_categ_ids","public_categ_ids.is_published")
    @api.one
    def _in_published_category(self):
        # CHECK IF PRODUCT HAVE AT LEAST ONE PUBLISHED PUBLIC CATEGORY
        one_publish = False 
        for category in self.public_categ_ids:
            one_publish = one_publish or category.is_published
        
        self.InPublishedCategory=one_publish



    InPublishedCategory = fields.Boolean(string='In Published Public Category', store=True,default=False,compute='_in_published_category')
