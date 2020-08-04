# ginos-pizza #
Harvard CS50 Web Programming with Python and JavaScript

# Use the app #
See the live web app [here](https://ginos-pizza.herokuapp.com/).

# Features # 
- *Sign up*, *Sign in*, *Sign out*: Site users are able to register with a username, password, first name, last name, and email address. Then they are able to sign in and sign out of the web app.
- *Adding Items*: Using Django Admin UI, administrators are able to add, update, and remove items on the menu.
- *Change Order Status*: Using Django Admin UI, administrators are able to change order status to finished when the order is completed. 
- *Menu*: A dynamic menu allows admin to maintain a good format while adding, updating, and removing items.
- *Shopping cart*: Once sign in, users allows to use shopping cart, they can update items' quatity, remove items, remove all items, view total quantity, view total price, and check out in shopping cart. Even though they closes the window and signs out their items will be saved and when they signs back in the items still in their shopping cart.
- *Placing an Order*: Once there is at least one item in the shopping cart, user are able to check out through Stripe API.
- *Change Email*: Once sign in, user can use change email form to change their email address.
- *Change Password*: Once sign in, user can use change password form to change their email address.
- *History Order*: Once sign in, users are allowed to check their history order and check their order status.