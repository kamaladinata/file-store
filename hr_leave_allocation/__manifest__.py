# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Employee Bulk Leave Allocation",
  "summary"              :  """This apps helps a Hr manager to allocation leaves of employee in bulk.""",
  "category"             :  "Human Resources",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Employee-Bulk-Leave-Allocation.html",
  "description"          :  """Employee Bulk Leave Allocation
        Employee IDs required (versio 1.0.1)""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=hr_leave_allocation&version=13.0",
  "depends"              :  ['hr_holidays'],
  "data"                 :  [
                             'views/views.xml',
                             'security/ir.model.access.csv',
                            ],
  "demo"                 :  ['demo/demo.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  25,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}