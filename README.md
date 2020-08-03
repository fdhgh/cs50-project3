# Project 3

Web Programming with Python and JavaScript
"# cs50-project3" 

Pizza restaurant orders portal, designed to meet the requirements:

* Menu: The web application should support all of the available menu items for Pinnochio’s Pizza & Subs (a popular pizza place in Cambridge).
* Adding Items: Using Django Admin, site administrators (restaurant owners) should be able to add, update, and remove items on the menu. Add all of the items from the Pinnochio’s menu into your database using either the Admin UI or by running Python commands in Django’s shell.
* Registration, Login, Logout: Site users (customers) should be able to register for the web application with a username, password, first name, last name, and email address. Customers should then be able to log in and log out of your website.
* Shopping Cart: Once logged in, users should see a representation of the restaurant’s menu, where they can add items (along with toppings or extras, if appropriate) to their virtual “shopping cart.” The contents of the shopping should be saved even if a user closes the window, or logs out and logs back in again.
* Placing an Order: Once there is at least one item in a user’s shopping cart, they should be able to place an order, whereby the user is asked to confirm the items in the shopping cart, and the total before placing an order.
* Viewing Orders: Site administrators should have access to a page where they can view any orders that have already been placed.


Future improvements:
* General UX such as Javascript enhancements, modernised components, stronger branding, and accessibility
 * Menu layout could be displayed as tiles
 * More customisation options on the product page, moving these off the menu page and tidying it up
* Performance - currently the menu is noticeably sluggish due to use of nested loops
* Security - Django provides XSS protection as standard but could this be improved?
* Django version upgrade
