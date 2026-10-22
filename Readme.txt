LITTLE LEMON RESTAURANT API Project Documentation / README
================================

1. PROJECT OVERVIEW

Little Lemon Restaurant API is a Django REST Framework project for
managing restaurant menu items, table bookings, customer carts, and
orders. It includes Djoser-based user registration and token
authentication, plus group-based permissions for Managers and Delivery
Crew members.

This README documents the endpoints implemented during the project
setup. Before submission, verify every endpoint against the actual code
and run the automated tests.

2. TECHNOLOGY STACK

-   Python
-   Django
-   Django REST Framework (DRF)
-   Djoser
-   Django REST Framework Token Authentication
-   SQLite by default (unless settings.py has been configured for
    another database)
-   Insomnia for API testing

3. PROJECT STRUCTURE

little-lemon-capstone/ |– littlelemon/ | |– settings.py | |– urls.py |–
restaurant/ | |– models.py | |– serializers.py | |– views.py | |–
permissions.py | |– order_permissions.py | |– urls.py | |– tests.py | |–
management/ | |– commands/ | |– create_groups.py |– manage.py |–
Readme.txt

Some files may be absent if the related features have not yet been
created.

4. SETUP INSTRUCTIONS

Prerequisites: - Python installed and available through the Windows
Python launcher (py). - VS Code or another code editor. - Git (for
GitHub submission). - Insomnia (optional, for API testing).

A. Open the project folder in VS Code and open its terminal.

B. Create and activate a virtual environment if one does not already
exist:

py -m venv .venv ..venv.ps1

C. Install the project dependencies:

py -m pip install Django djangorestframework djoser mysqlclient

D. Apply database migrations:

py manage.py makemigrations py manage.py migrate

E. Run Django’s system check:

py manage.py check

F. Create the Manager and Delivery Crew groups, if the custom management
command exists in the project:

py manage.py create_groups

G. Start the development server:

py manage.py runserver

The local API base URL is:

http://127.0.0.1:8000/

Stop the development server with Ctrl+C.

DATABASE NOTE: Django uses SQLite by default unless DATABASES in
littlelemon/settings.py has been configured for MySQL. Installing
mysqlclient alone does not configure or connect the project to a MySQL
database. If the course requires MySQL, configure and test the
connection before submission.

5. AUTHENTICATION

The project is configured for token authentication and session
authentication.

Register a user: POST /auth/users/

Example JSON body: { “username”: “exampleuser”, “password”:
“Use-A-Strong-Local-Test-Password!”, “email”: “example@example.com” }

Obtain a token: POST /auth/token/login/

Example JSON body: { “username”: “exampleuser”, “password”:
“Use-A-Strong-Local-Test-Password!” }

Use the returned token on authenticated requests:

Authorization: Token YOUR_AUTH_TOKEN Content-Type: application/json

Log out: POST /auth/token/logout/

Do not commit passwords, authentication tokens, or other secrets to
GitHub.

6. API ENDPOINT REFERENCE

A. MENU ITEMS

Method Endpoint Description GET /api/menu-items List menu items (public
read) POST /api/menu-items Create a menu item (Manager/staff) GET
/api/menu-items/ Retrieve one menu item PUT /api/menu-items/ Replace a
menu item (Manager/staff) PATCH /api/menu-items/ Partially update a menu
item (Manager/staff) DELETE /api/menu-items/ Delete a menu item
(Manager/staff)

Menu item fields: - title - price - inventory

B. TABLE BOOKINGS

Method Endpoint Description GET /api/bookings List bookings
(authentication rules depend on view) POST /api/bookings Create a
booking (authentication rules depend on view) GET /api/bookings/
Retrieve a booking PUT/PATCH /api/bookings/ Update a booking DELETE
/api/bookings/ Delete a booking

Booking fields: - name - no_of_guests - booking_date

C. MANAGER AND DELIVERY CREW GROUPS

Method Endpoint Description GET /api/groups/manager/users List users in
Manager group (Manager/staff) POST /api/groups/manager/users Add an
existing user to Manager group GET /api/groups/delivery-crew/users List
users in Delivery Crew group (Manager/staff) POST
/api/groups/delivery-crew/users Add an existing user to Delivery Crew
group

Example POST body for adding an existing user: { “username”:
“existingusername” }

D. CART

Method Endpoint Description GET /api/cart/menu-items View the
authenticated user’s cart POST /api/cart/menu-items Add a menu item to
the cart DELETE /api/cart/menu-items Clear the authenticated user’s cart

Example POST body: { “menuitem”: 1, “quantity”: 2 }

E. ORDERS

Method Endpoint Description GET /api/orders List orders visible to the
authenticated role POST /api/orders Create an order from the user’s cart
GET /api/orders/ Retrieve an order if the user has access PATCH
/api/orders/ Update permitted order fields/status

Order status values: 0 = Pending 1 = In progress 2 = Completed

Expected access rules in the current implementation: - Customers can
view their own orders and create orders from their carts. - Delivery
Crew members can view assigned orders and update their status. -
Managers/staff can view all orders, assign Delivery Crew members, and
update status.

F. DJOSER USER ENDPOINTS

POST /auth/users/ Register a user POST /auth/token/login/ Obtain an
authentication token POST /auth/token/logout/ Invalidate the current
token

Djoser may expose additional user endpoints depending on its
configuration.

7. TESTING

Run the automated tests:

py manage.py check py manage.py test restaurant

Use Insomnia to test endpoints with the appropriate HTTP method, URL,
JSON body, and Authorization header. Verify both successful requests and
denied requests for unauthenticated users or users without the required
role.

Example menu item JSON: { “title”: “Greek Salad”, “price”: “12.50”,
“inventory”: 20 }

Example cart JSON: { “menuitem”: 1, “quantity”: 2 }

The numeric menu item ID must exist in the database before adding it to
a cart.

8. GITHUB SUBMISSION CHECKLIST

Before submission: - Run py manage.py check successfully. - Run py
manage.py test restaurant and resolve failures. - Test the documented
routes in Insomnia. - Confirm database settings match the assignment
requirements. - Verify that Manager, Delivery Crew, and Customer
permissions behave correctly. - Do not upload the .venv directory,
secret keys, passwords, tokens, or local database files containing
personal/test data. - Add a suitable .gitignore file. - Upload the
project to GitHub. - Submit the repository URL in Coursera’s My
submission section. - Complete the required peer reviews.

9. IMPORTANT NOTES

This document reflects the starter implementation described during
development. The exact route behavior depends on the current code in
restaurant/views.py, restaurant/permissions.py,
restaurant/order_permissions.py, and restaurant/urls.py. Confirm these
files match this documentation before treating the project as final.

The project is not considered complete until all required features are
implemented, tested, documented accurately, and checked against the
current Coursera assignment instructions.
