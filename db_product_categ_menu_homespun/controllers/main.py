from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_product_misc_options_73lines.controllers.main import WebsiteSaleExt
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website.models.website import slug

from odoo import api, fields, models

import logging, pdb
_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row

class WebsiteSaleCategories(WebsiteSaleExt):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        
        res = super(WebsiteSaleCategories, self).shop(page, category,
                                               search, ppg, **post)

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        attrib_values = res.qcontext['attrib_values']
        tag_set = res.qcontext['tag_set']
        brand_set = res.qcontext['brand_set']
        
        #????
        price_min = res.qcontext['price_min'] 
        price_max = res.qcontext['price_max'] 

        domain = self._get_search_domain_ext(search, category, attrib_values,
                                              list(tag_set), list(brand_set),
                                              price_min, price_max)

        Product = request.env['product.template']

        # FILTER PRODUCT WITH PUBLISHED PUBLIC CATEGORIES  
        domain.append(('InPublishedCategory','=',True))

        url = "/shop"
        if category:
            category = request.env['product.public.category'].browse(
                int(category))
            url = "/shop/category/%s" % slug(category)

        product_count = Product.search_count(domain)
        
        pager = request.website.pager(url=url, total=product_count,
                                      page=page, step=ppg, scope=7,
                                      url_args=post)
        
        products = Product.search(domain, limit=ppg, offset=pager['offset'],
                                  order=self._get_search_order(post))      
        
        res.qcontext.update({
            'products': products,
            'bins': TableCompute().process(products, ppg),
            'search_count': product_count,
            'pager': pager
            })
        
        return res
