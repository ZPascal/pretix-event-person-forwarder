Pretix Event Person Forwarder
=============================

A Python library for forwarding event, order, and question data from Pretix to external systems via HTTP.

Installation
------------

Install the package via pip::

    pip install pretix-event-person-forwarder

Quick Start
-----------

Get started in just a few lines::

    from pretix_event_person_forwarder import Forwarder

    forwarder = Forwarder(
        api_url="https://your-pretix-instance.com/api/",
        api_token="your-api-token"
    )

API Documentation
-----------------

.. toctree::
   :maxdepth: 2

   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
