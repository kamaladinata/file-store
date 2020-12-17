# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
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
  "name"                 :  "Email Verification",
  "summary"              :  "This module allows to send token based email for verification of accounts and restricts checkout for non verified accounts.",
  "category"             :  "Website",
  "version"              :  "2.0.1",
  "sequence"             :  10,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  """https://store.webkul.com""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=email_verification&version=11.0",
  "depends"              :  [
                             'mail',
                             'website_webkul_addons',
                            ],
  "data"                 :  ['data/data.xml',
                             'data/email_template.xml',
                             'views/templates_view.xml',
                             'views/res_config_view.xml',
                             'views/res_users_view.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'wizard/wizard_view.xml',
                            ],
  "demo"                 :  ['data/data.xml'],
  "images"               :  ['static/description/banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  29,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}