# [Food Vendor API][docs]

# Overview

Food Vendor is an API ready for consumption between vendors and customers.


----

# Requirements

* Python (3.6)
* Django (3.0)


# Installation

Install using `pip`...

    pip install -r requirments.txt

Seed database...

    python manage.py loaddata fixtures


# Example

Let's take a look at a quick example of using REST framework to build a simple model-backed API for accessing users and groups.

Startup up a new project like so...

    pip install django
    pip install djangorestframework
    django-admin startproject example .
    ./manage.py migrate
    ./manage.py createsuperuser


That's it, we're done!

    python manage.py runserver

You can now open the API in your browser at `http://127.0.0.1:8000/`, and view your new 'users' API. If you use the `Login` control in the top right corner you'll also be able to add, create and delete users from the system.



# Documentation & Support

Full documentation for the project is available at [https://documenter.getpostman.com/view/8806253/SztBa7TL?version=latest#64f8e2f7-353e-4931-9594-442970a1b59f][docs].

For questions and support, You may also want to [follow me on Twitter][twitter].
