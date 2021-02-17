# Odoo Proprietary License v1.0

# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).

# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).

# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.

# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
{
    "name" : "Freight Management",    
    "author" : "Knowledgeware",
    "version": '13.0.1.1',    
    "category" : "Operations",
    "license" : "OPL-1",
    "depends" : ['mail', 'base', 'account','base_automation'],
    "data" : [
        'views/operation_view.xml',
        'views/payable_receivable_view.xml',
        'views/service_view.xml',
        'views/smart_buttons.xml',    
        'views/routing_view.xml',
        'views/partner_view.xml',
        'views/configuration_view.xml',
        'views/billing_instruction.xml',
        'automation/on_update_master_operation.xml',
        'sequences/operation_sequence.xml',
        'sequences/route_sequence.xml',
        'sequences/master_sequence.xml',
        'sequences/shipment_sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'reporting/profit_loss.xml',
        'reporting/booking_confirmation.xml',
        'reporting/certificate_of_origin.xml',
        'reporting/bill_of_lading.xml'
        ],
        'installable': True,
        'auto_install': False,
        'application': True,
        "images":["static/description/Banner.png"],
        'price':590,
        'currency':'EUR',
}
