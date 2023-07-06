import frappe
from frappe import auth

@frappe.whitelist( allow_guest=True )
def login(usr, pwd):
    """The function is designed to retrieve the user's API key and API secret, which are required for generating headers to be used in making requests to other APIs. These credentials serve as authentication parameters, ensuring that only authorized users can access the requested APIs. """
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response['http_status_code'] = 401
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Authentication Error!"
        }

        return

    user = frappe.get_doc('User', frappe.session.user)
    if not user.api_key:
        api_key,api_secret=generate_keys(frappe.session.user)
    else:
        api_key=user.api_key
        api_secret=user.get_password("api_secret")


    frappe.response["message"] = {
        "success_key":1,
        "message":"Authentication success",
        "sid":frappe.session.sid,
        "api_key":api_key,
        "api_secret":api_secret,
        "username":user.username,
        "email":user.email
    }



def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()
    frappe.db.commit()

    return api_key,api_secret