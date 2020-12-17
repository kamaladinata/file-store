{
  "name"                 :  "Odoo Booking & Reservation Management",
  "summary"              :  """Booking & reservation management in Odoo allows users to take appointment and ticket booking facility in Odoo website.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Portcities Ltd",
  "license"              :  "Other proprietary",
  "website"              :  "https://portcities.net",
  "description"          :  """Odoo booking & reservation management
        Odoo Subscription Management
        Odoo Website Subscription Management
        Odoo appointment management
        Odoo website Appointment Management
        Schedule bookings
        Tickets
        Reservations
        Booking Facility in Odoo
        Website booking system
        Appointment management system in Odoo
        Booking & reservation management in Odoo
        Reservation management in Odoo
        Booking
        Reservation
        Booking and reservation""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=movie_booking_system",
  "depends"              :  ['web','website_sale','pos_retail','theme_treehouse'],
  "qweb": [
        "static/src/xml/scan_ticket.xml",
        "static/src/xml/pos_screen.xml",
        "static/src/xml/notification.xml",
    ],
  "data"                 :  [
                             'data/mail_template_data.xml',
                             'security/ir.model.access.csv',
                             'views/account_asset_views.xml',
                             'views/booking_config_view.xml',
                             'views/booking_sol_view.xml',
                             'wizard/bk_qty_available_wizard_view.xml',
                             'views/product_template_view.xml',
                             'views/booking_product_cart_temp.xml',
                             'views/booking_template.xml',
                             'views/seat_book_views.xml',
                             'views/pos_order_line_view.xml',
                             'views/ticket_portal_templates.xml',
                             'views/ir_crons.xml',
                             'views/booking_setting.xml',
                             'views/point_of_sale_assets.xml',
                             'views/countdown_views.xml',
                             'report/ticket_movie.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  149,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}