from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        user = request.env.user

        SeatBook = request.env['seat.book'].sudo()
        ticket_count = SeatBook.search([
            ('user_id','=',user.id)
        ])
        count = 0
        for t in ticket_count:
            if t.order_reference and (t.sale_line_id.order_id.state == 'sale' or t.pos_line_id):
                count+=1

        values.update({
            'ticket_movie_count': count,
        })
        return values
    
    @http.route(['/my/attraction/ticket', '/my/attraction/ticket/page/<int:page>'], type='http', auth='portal_user', website=True)
    def portal_my_ticket(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        SeatBook = request.env['seat.book']

        domain = [
            ('user_id','=',user.id)
        ]

        searchbar_sortings = {
            'name': {'label': _('Seat Name'), 'order': 'name asc'},
            'order_ref': {'label': _('Order Reference'), 'order': 'order_reference asc'},
        }
        # default sortby order
        if not sortby:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('seat.book', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        domain += [('order_reference','!=',False),'|',('sale_line_id.order_id.state','=','sale'),('pos_line_id','!=',False)]
        # count for pager
        ticket_count = SeatBook.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/attraction/ticket",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=ticket_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        seats = SeatBook.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset']).sudo()
        
        # seats = seats_all.filtered(lambda r: r.order_reference and (r.sale_line_id.order_id.state == 'sale' or r.pos_line_id))
        
        values.update({
            'date': date_begin,
            'seats': seats.sudo(),
            'page_name': 'seat',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/attraction/ticket',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("portal.portal_my_home", values)

    @http.route(['/my/attraction/ticket/<int:ticket_id>'], type='http', auth="public", website=True)
    def tickets_followup(self, ticket_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            SeatBook = request.env['seat.book']
            seat_sudo = SeatBook.browse(ticket_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if download == 'True':
            download = True
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=seat_sudo, report_type=report_type, report_ref='movie_booking_system.ticket_movie_book', download=download)

        values = {
            'seat_book': seat_sudo.sudo(),
            'message': message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'report_type': 'html',
            'page_name': 'seat',
        }

        return request.render('movie_booking_system.booking_ticket_portal_template', values)
