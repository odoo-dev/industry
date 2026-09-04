# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo.tests import tagged
from odoo.tests.common import HttpCase, MockHTTPClient


@tagged("post_install", "-at_install")
class BookingChannexHTTPRequestsTestCase(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['ir.config_parameter'].set_str('booking_channex.x_channex_api_key', "MyTestAPIKey")
        cls.env['ir.config_parameter'].set_str('booking_channex.x_channex_token', "MyTestWebhookSecret")

    def test_receive_booking_webhook(self):
        payload_receive_booking = {
            "event": "booking_new",
            "payload": {
                "currency": "EUR",
                "amount": "88.00",
                "channel_id": None,
                "property_id": "38149695-d95b-4c80-a7c3-34ce96efc7ba",
                "booking_id": "e868f16e-b474-4b95-af12-5b114133e670",
                "arrival_date": "2026-03-04",
                "booking_revision_id": "074cd7f9-df51-4fc6-a8f4-7658573a235d",
                "count_of_rooms": 1,
                "count_of_nights": 1,
                "customer_name": "Demo Marc",
            },
            "property_id": "38149695-d95b-4c80-a7c3-34ce96efc7ba"
        }
        booking_ack_answer = {"meta": {"message": "Success"}}
        get_revisions_answer = {
            "data": [{
                "attributes": {
                    "id": "03dd7198-c5b7-493c-a889-74d0c2211de7",
                    "status": "new",
                    "currency": "EUR",
                    "amount": "88.00",
                    "ota_name": "BookingCom",
                    "property_id": "38149695-d95b-4c80-a7c3-34ce96efc7ba",
                    "booking_id": "e868f16e-b474-4b95-af12-5b114133e670",
                    "arrival_date": "2026-03-04",
                    "arrival_hour": "15:00",
                    "customer": {
                        "name": "Demo",
                        "state": None,
                        "zip": "1000",
                        "address": "Rue de Marc",
                        "country": "BE",
                        "city": "Bruxelles",
                        "mail": "marc.demo@odootest.test",
                        "phone": None,
                        "surname": "Marc"
                    },
                    "departure_date": "2026-03-05",
                    "payment_collect": "ota",
                    "payment_type": "credit_card",
                    "rooms": [
                        {
                            "amount": "88.00",
                            "guests": [{
                                "name": "Demo",
                                "surname": "Marc"
                            }],
                            "occupancy": {
                                "children": 0,
                                "adults": 1,
                                "infants": 0
                            },
                            "rate_plan_id": "abd55f84-a02c-4593-8109-1d13b178105d",
                            "room_type_id": "28ff9c15-c4a1-4334-a259-146557838b5e",
                            "booking_room_id": "f9101f02-ab78-4afb-9841-50b23035fe81",
                        }
                    ],
                    "occupancy": {
                        "children": 0,
                        "adults": 1,
                        "infants": 0
                    },
                    "revision_id": "4ba0eeed-0cb0-4e54-971e-b00fbee0504f",
                },
                "id": "03dd7198-c5b7-493c-a889-74d0c2211de7",
                "type": "booking_revision"
            }]
        }
        booking_update_payload = {
            "event": "booking_modification",
            "payload": {
                "currency": "EUR",
                "amount": "88.00",
                "property_id": "38149695-d95b-4c80-a7c3-34ce96efc7ba",
                "booking_id": "e868f16e-b474-4b95-af12-5b114133e670",
                "arrival_date": "2026-03-03",
                "booking_revision_id": "58baf059-33d7-4df7-8234-a26b2d8eb97e",
                "count_of_rooms": 2,
                "count_of_nights": 2,
                "customer_name": "Demo Marc",
            },
            "property_id": "38149695-d95b-4c80-a7c3-34ce96efc7ba"
        }
        room = self.env['product.product'].create({
            'name': 'Test Room'
        })
        self.env['x_channex_mapping'].create({
            'x_model_type': 'room_type',
            'x_remote_id': '28ff9c15-c4a1-4334-a259-146557838b5e',
            'x_local_id': room.id,
        })
        self.env['sale.order'].create({  # Needed for the webhook to find something to operate on
            'partner_id': self.env['res.partner'].create({'name': 'Test Partner 1'}).id,
            'state': 'cancel',
        })
        response = self.url_open(
            self.env.ref("booking_channex.webhook_get_booking_create_change_or_delete").url,
            data=json.dumps(payload_receive_booking),
            headers={'Content-Type': 'application/json', 'x-channex-token': 'WrongToken'}
        )
        self.assertFalse(self.env['x_channex_mapping'].search([('x_remote_id', '=', 'e868f16e-b474-4b95-af12-5b114133e670')], limit=1), 'The sale order has been created when webhook received the payload with wrong token.')
        with (
            self.assertLogs(level="WARNING"),  # Is preventing any warning to be logged, we should replace this to ignore only the Unsafe Error
            MockHTTPClient(url="https://staging.channex.io/api/v1/booking_revisions/074cd7f9-df51-4fc6-a8f4-7658573a235d/ack", return_json=booking_ack_answer, return_status=200),
            MockHTTPClient(url="https://staging.channex.io/api/v1/booking_revisions/feed?pagination[limit]=100&pagination[page]=1", return_json=get_revisions_answer, return_status=200),
            MockHTTPClient(url="https://staging.channex.io/api/v1/booking_revisions/feed?pagination[limit]=100&pagination[page]=2", return_json={"data": []}, return_status=200),
        ):
            response = self.url_open(
                self.env.ref("booking_channex.webhook_get_booking_create_change_or_delete").url,
                data=json.dumps(payload_receive_booking),
                headers={'Content-Type': 'application/json', 'x-channex-token': 'MyTestWebhookSecret'}
            )
            self.assertEqual(response.status_code, 200, 'The creation of the booking encountered a status processing error')
            so_mapping = self.env['x_channex_mapping'].search([('x_remote_id', '=', 'e868f16e-b474-4b95-af12-5b114133e670')], limit=1)
            booking_sale_order = self.env['sale.order'].browse(so_mapping.x_local_id) if so_mapping else False
            self.assertTrue(booking_sale_order, 'The sale order has not been created when webhook received the payload with correct token.')
            self.assertEqual(len(booking_sale_order.order_line), 1, 'The created sale order has an incorrect amount of sale order lines')
            self.assertEqual(booking_sale_order.order_line.product_id.id, room.id, 'The created sale order line for the booking sale order references the incorrect product')

        get_revisions_answer['data'][0]['attributes']['arrival_date'] = '2026-03-03'
        get_revisions_answer['data'][0]['attributes']['departure_date'] = '2026-03-06'
        get_revisions_answer['data'][0]['attributes']['rooms'].append({
            "amount": "88.00",
            "guests": [],
            "occupancy": {
                "children": 0,
                "adults": 1,
                "infants": 0
            },
            "rate_plan_id": "abd55f84-a02c-4593-8109-1d13b178105d",
            "room_type_id": "28ff9c15-c4a1-4334-a259-146557838b5e",
            "booking_room_id": "f9101f02-ab78-4afb-9841-50b23035fe81",
        })
        get_revisions_answer['data'][0]['attributes']['status'] = 'modified'

        with (
            self.assertLogs(level="WARNING"),  # Is preventing any warning to be logged, we should replace this to ignore only the Unsafe Error
            MockHTTPClient(url="https://staging.channex.io/api/v1/booking_revisions/074cd7f9-df51-4fc6-a8f4-7658573a235d/ack", return_json=booking_ack_answer, return_status=200),
            MockHTTPClient(url="https://staging.channex.io/api/v1/booking_revisions/feed?pagination[limit]=100&pagination[page]=1", return_json=get_revisions_answer, return_status=200),
            MockHTTPClient(url="https://staging.channex.io/api/v1/booking_revisions/feed?pagination[limit]=100&pagination[page]=2", return_json={"data": []}, return_status=200),
        ):
            response = self.url_open(
                self.env.ref("booking_channex.webhook_get_booking_create_change_or_delete").url,
                data=json.dumps(booking_update_payload),
                headers={'Content-Type': 'application/json', 'x-channex-token': 'MyTestWebhookSecret'}
            )
            self.env.ref('booking_channex.ir_cron_change_booking_dates').method_direct_trigger()
            self.assertEqual(response.status_code, 200, 'The modification of the booking encountered a status processing error')
            self.assertTrue(len(booking_sale_order.order_line) == 2, 'The sale order modification failed to create a new line for a second room.')
            self.assertEqual(booking_sale_order.rental_start_date.strftime('%Y-%m-%d'), get_revisions_answer['data'][0]['attributes']['arrival_date'], 'The sale order modification failed to change the start date of the sale order')
            self.assertEqual(booking_sale_order.rental_return_date.strftime('%Y-%m-%d'), get_revisions_answer['data'][0]['attributes']['departure_date'], 'The sale order modification failed to change the end date of the sale order')

    def test_product_create_on_channex(self):
        create_room_type_answer = {"data": {"type": "room_type", "id": "994d1375-dbbd-4072-8724-b2ab32ce781b", "attributes": {
            "id": "994d1375-dbbd-4072-8724-b2ab32ce781b", "title": "Standard Room",
            "occ_adults": 3, "occ_children": 0, "occ_infants": 0, "default_occupancy": 2, "count_of_rooms": 20, "room_kind": "room", "capacity": None,
            "content": {"description": "Some Room Type Description Text", "photos": []}
            },
            "relationships": {"facilities": {"data": []}, "property": {"data": {"type": "property", "id": "716305c4-561a-4561-a187-7f5b8aeb5920"}}}
        }}
        with (MockHTTPClient(url="https://staging.channex.io/api/v1/room_types", return_json=create_room_type_answer, return_status=200)):  # as request_response
            new_room = self.env["product.template"].create({
                'name': 'Test room',
                'type': 'service',
                'list_price': 90.0,
            })
            self.env["x_channex_mapping"].search([
                ("x_model_type", "=", "room_type"),
                ("x_local_id", "=", new_room.id),
            ], limit=1)
            # Is failing right now as it is not yet implemented; should be here again when non-ari updates arrives
            # self.assertEqual(request_response.calls, 0, "Creating a room type in odoo did not send any requests to channex")
            # self.assertTrue(room_mapping.x_remote_id, "Creating a room did not create a mapping entry in odoo")
            # self.assertEqual(room_mapping.x_remote_id, "994d1375-dbbd-4072-8724-b2ab32ce781b", "Creating a room did not put the correct remote id in the mapping")
