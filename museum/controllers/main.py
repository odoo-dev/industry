# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError
from odoo.http import route, request

from odoo.addons.frontdesk_partnership.controllers.main import FrontdeskMembers


class MuseumFrontdesk(FrontdeskMembers):
    """Extend the Members kiosk scanner to also handle Event Ticket barcodes."""

    @route()
    def get_visitor_data(self, frontdesk_id, token, barcode, **kwargs):
        event_checkin_enabled = request.env.company.sudo().x_museum_frontdesk_event_checkin

        try:
            return super().get_visitor_data(frontdesk_id, token, barcode, **kwargs)
        except UserError:
            if not event_checkin_enabled:
                raise

        reg_data = request.env['event.registration'].sudo().register_attendee(
            barcode=barcode,
            event_id=None,  # multi-event mode: accept tickets for any active event
        )
        if reg_data.get('error') == 'invalid_ticket':
            raise UserError(
                request.env._(
                    "No member or event ticket matching this barcode was found."
                )
            )

        reg_data['event_checkin'] = True
        return reg_data
