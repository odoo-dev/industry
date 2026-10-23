# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.tests.common import TransactionCase


class BookingChannexAutomationsTestCase(TransactionCase):

    def test_manipulate_product_impacts_rate_plans(self):
        self.assertEqual(self.env['x_rate_plan'].search_count([]), 0, "There are rate plans existing after installing the module while none should be there")
        product_tmpl = self.env['product.template'].create({
            'name': 'Test Room',
            'type': 'service',
            'x_is_a_room_offer': True,
            'attribute_line_ids': [
                Command.create({
                    'attribute_id': self.env.ref('booking_engine.product_attribute_22').id,
                    'value_ids': [
                        Command.link(self.env.ref('booking_engine.product_attribute_guest1').id),
                        Command.link(self.env.ref('booking_engine.product_attribute_guest2').id),
                        Command.link(self.env.ref('booking_engine.product_attribute_guest1_1').id),
                    ],
                }),
                Command.create({
                    'attribute_id': self.env.ref('booking_engine.product_attribute_1').id,
                    'value_ids': [
                        Command.link(self.env.ref('booking_engine.product_attribute_value_rate_1').id),
                        Command.link(self.env.ref('booking_engine.product_attribute_value_rate_2').id),
                    ],
                })
            ],
        })
        # There should be 3 (product variants) * 2 (rate plan attribute values) * 1 (pricelists) rate plans created
        self.assertEqual(self.env['x_rate_plan'].search_count([('x_variant_id.product_tmpl_id', '=', product_tmpl.id)]), 6, "The amount of rate plans resulting from the creation of the room is not the correct one.")

        second_pricelist = self.env['product.pricelist'].create({'name': 'test second pricelist'})
        # There should be 3 (product variants) * 2 (rate plan attribute values) * 2 (pricelists) rate plans created
        self.assertEqual(self.env['x_rate_plan'].search_count([('x_variant_id.product_tmpl_id', '=', product_tmpl.id)]), 12, "The amount of rate plans resulting from the creation of a new pricelist is not the correct one.")
        second_pricelist.x_published_on_channex = False
        # There should be 3 (product variants) * 2 (rate plan attribute values) * 1 (pricelists) rate plans created
        self.assertEqual(self.env['x_rate_plan'].search_count([('x_variant_id.product_tmpl_id', '=', product_tmpl.id)]), 6, "The amount of rate plans resulting from unpublishing a pricelist is not the correct one.")
        second_pricelist.x_published_on_channex = True
        second_pricelist.active = False
        # There should be 3 (product variants) * 2 (rate plan attribute values) * 1 (pricelists) rate plans created
        self.assertEqual(self.env['x_rate_plan'].search_count([('x_variant_id.product_tmpl_id', '=', product_tmpl.id)]), 6, "The amount of rate plans resulting from archiving a pricelist is not the correct one.")
        second_pricelist.active = True

        guest_attribute_line = product_tmpl.attribute_line_ids.filtered(lambda a: a.attribute_id.id == self.env.ref('booking_engine.product_attribute_22').id)
        guest_attribute_line.value_ids = [Command.link(self.env.ref('booking_engine.product_attribute_guest2_1').id)]
        # There should be 4 (product variants) * 2 (rate plan attribute values) * 2 (pricelists) rate plans created
        self.assertEqual(self.env['x_rate_plan'].search_count([('x_variant_id.product_tmpl_id', '=', product_tmpl.id)]), 16, "The amount of rate plans resulting from adding a variant is not the correct one.")

        guest_attribute_line.value_ids -= self.env.ref('booking_engine.product_attribute_guest1')
        # There should be 3 (product variants) * 2 (rate plan attribute values) * 2 (pricelists) rate plans created
        self.assertEqual(self.env['x_rate_plan'].search_count([('x_variant_id.product_tmpl_id', '=', product_tmpl.id)]), 12, "The amount of rate plans resulting from removing a variant is not the correct one.")

        product_tmpl.x_is_a_room_offer = False
        self.assertEqual(self.env['x_rate_plan'].search_count([('x_variant_id.product_tmpl_id', '=', product_tmpl.id)]), 0, "The amount of rate plans resulting from the removing the room offer tag of the product should be 0.")
        product_tmpl.x_is_a_room_offer = True
        # There should be 3 (product variants) * 2 (rate plan attribute values) * 2 (pricelists) rate plans created
        self.assertEqual(self.env['x_rate_plan'].search_count([('x_variant_id.product_tmpl_id', '=', product_tmpl.id)]), 12, "The amount of rate plans resulting from adding back the room offer tag of the product is not the correct one.")

        product_tmpl.active = False
        self.assertEqual(self.env['x_rate_plan'].search_count([('x_variant_id.product_tmpl_id', '=', product_tmpl.id)]), 0, "The amount of rate plans resulting from the archiving the product should be 0.")
