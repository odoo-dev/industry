# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os

from odoo import api, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model
    def _get_random_barcode(self):
        """Return a barcode string that does not exist in either
        event.registration or res.partner.  Loops until a genuinely unique
        value is found.
        """

        while True:
            barcode = str(int.from_bytes(os.urandom(8), 'little'))

            if self.env['res.partner'].search_count([('barcode', '=', barcode)], limit=1):
                continue
            return barcode
