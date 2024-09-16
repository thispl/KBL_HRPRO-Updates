import frappe

@frappe.whitelist()
def send_welcome_mail_to_user():
		user = "supriya@kblservices.in"
		from frappe.utils import get_url
		link = reset_password(user)
		subject = None
		method = frappe.get_hooks("welcome_email")
		if method:
			subject = frappe.get_attr(method[-1])()
		if not subject:
			site_name = frappe.db.get_default('site_name') or frappe.get_conf().get("site_name")
			if site_name:
				subject = _("Welcome to {0}").format(site_name)
			else:
				subject = _("Complete Registration")

		send_login_mail(user,subject, "new_user",
				dict(
					link=link,
					site_url=get_url(),
				))


def reset_password(user,send_email=False, password_expired=False):
	from frappe.utils import random_string, get_url

	user = frappe.get_doc('User',user)
	key = random_string(32)
	user.db_set("reset_password_key", key)

	url = "/update-password?key=" + key
	if password_expired:
		url = "/update-password?key=" + key + '&password_expired=true'

	link = get_url(url)
	# if send_email:
	#     self.password_reset_mail(link)

	return link


def send_login_mail(user,subject, template, add_args, now=None):
	"""send mail with login details"""
	from frappe.utils.user import get_user_fullname
	from frappe.utils import get_url

	user = frappe.get_doc('User',user)
	empid = frappe.get_value('Employee',{'user_id':user.name},["employee_number"])
	created_by = get_user_fullname(frappe.session['user'])
	if created_by == "Guest":
		created_by = "Administrator"

	args = {
		'first_name': user.first_name,
		'user': user.name,
		'empid': empid,
		'title': subject,
		'login_url': get_url(),
		'created_by': created_by
	}

	args.update(add_args)

	# sender = frappe.session.user not in STANDARD_USERS and get_formatted_email(frappe.session.user) or None
	sender = 'hr@kblservices.in'
	
	frappe.sendmail(recipients=user.email,sender=sender, subject=subject,
		template=template, args=args, header=[subject, "green"],
		delayed=(not now) if now!=None else user.flags.delay_emails, retry=3)