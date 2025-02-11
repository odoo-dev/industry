from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestUi(HttpCase):

    def test_condominium_acquisition(self):
        self.start_tour("/", 'Condominium_Acquisition_test', login="admin", watch=True)
