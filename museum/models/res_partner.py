# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import choice
from string import digits

from odoo import _, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        res = super().write(vals)
        if 'barcode' in vals:
            for partner in self:
                if not partner.barcode:
                    continue
                conflict = self.env['event.registration'].search_count(
                    [('barcode', '=', partner.barcode)], limit=1
                )
                if conflict:
                    raise ValidationError(_(
                        'The barcode "%(barcode)s" is already used by an event '
                        'registration.  Please use a different barcode.',
                        barcode=partner.barcode,
                    ))
        return res

    def _generate_unique_partner_barcode(self):
        """Return a barcode string that does not exist inevent.registration.
        Loops until a genuinely unique value is found.
        """

        while True:
            barcode = '042' + ''.join(choice(digits) for _ in range(9))
            if self.env['event.registration'].search_count([('barcode', '=', barcode)], limit=1):
                continue
            return barcode

    def generate_barcode(self):
        for record in self:
            if record.grade_id and not record.barcode:
                record.write({'barcode': self._generate_unique_partner_barcode()})
