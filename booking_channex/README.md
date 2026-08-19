# Introduction

This module allows Odoo to be Synced with Channex. Channex is a channel manager that serves as a mediator between applications like odoo on one side, and online travel agencies such as Booking.com on the other side. By using it, we can push rooms on Channex so they appear and can be sold on those other sites.

In Channex, we register the groups, that contains one or multiple properties. Each property contains one or multiple rooms and each room contains their different rate plans. We also need to populate the inventory of channex, which is the availabilty of each room and price of each rate plan for each upcoming day, initially 500 days in advance. With this, Channex has all it needs to start selling the rooms.

Our role in this is to populate channex records and inventory with an [initial sync](#sync-initial) and keep them up to date using [live sync](#live-sync) & [ARI sync](#aris-sync), to make sure what is published is corresponding to what we have in Odoo. We also need to capture the bookings made on those other side with the [bookings webhook](#booking-webhook), that are recorded on channex, so we can record them in odoo and adapt the availabilities accordingly.

# Lexicon

OTA : Online Travel Agency, like booking.com, airbnb...

ARI : Availability, Rates, and Inventory

# Goals

## \-> Functional Challenges of the module

- Constant Synchronization : We need to sync in real-time datas between odoo and channex. For example, if a room is not available anymore, it needs to be removed instantly from channex.

- Certification : Verify that we always comply as much as possible to the certification test : https://docs.channex.io/api-v.1-documentation/pms-certification-tests

- Http Requests in the server actions: This is an extension of \_get_eval_context, where we added the requests methods to be able to call them. Due to this, the module is unusable without this extension in place. Any DB using the module needs this.

## \-> Technical Challenges of the module

- Concurrency: Most of the time, We don't control the order in which the automations are executed. However, that is a really important and risky part of the module, as in channex we can't link a rate plan to a room that has yet to be created, or send an availability to a rate plan that is not yet in channex. Those kind of issues are dangerous and we need to find ways to enforce a non breaking order when writing our automations.

- Odoo Rollback: When a server action fails to execute in Odoo, from any error, it will rollback the code as if nothing was executed in Odoo. This means the mappings, and everything we execute will no longer exist, while the HTTP requests sent are NOT part of the rollback, and are already wrote on channex. Due to this, we need to make everything we can to not fail server actions, or at least not after sending data to channex.

- Booking Acknowledgement: We receive the bookings already validated, which means the bookings are not refusable. We need to make them fit in our planning or solve the issue if that is not possible.

# Server Actions Explained By Features

## Mapping

The model x_channex_mapping was introduced to keep track of which records in odoo corresponds to which ones in channex. This is composed of three fields only: x_model_type, x_local_id and x_remote_id. We use it everywhere in this module.

## Sync initial

There is a server action, action_button_sync, that is executed by a button from the settings to initiate the first synchronization with channex. It uses the config parameter x_channex_api_key to create the webhook on channex. Then, with the live sync server action directly called, it creates the groups, properties, room_types and rate_plans. Finally, it calls a separate server action to send the ARIs.

## Live Sync

There are a lot of different server actions used for live sync, they are called by automation to automatically send changes from odoo to channex, on any record from related model create/update/delete.

Special cases:

- The server action for create and modify rooms are grouped together, as a room in odoo is not automatically sent to channex (if does not have the guest attribute for example)
- The rate plans are either created or erased, never modified, so there's no server action for this.

## ARIs Sync

The ARIs are sent by package to channex, as to not send thousands of http requests at the same time. To do that, we have a custom model x_channex_ari_update_lines. We create new lines when we have something to send and, one minute after the lines are added, a cron sends every ARI change to channex. If other lines are added in between, they are sent together.

## Booking Webhook

A webhook set on the sale order model is used to receive the bookings notifications from channex. It is used to create/modify/delete sale orders related to channex bookings.

## Daily Synchronization Cron

This acts as a safety net for us, every day a cron will run to fetch data on channex and compare it to the data in odoo, and will create or modify records on channex to correct eventual errors. The server action can also be called directly from the button in the settings, as it replaces the initial sync button once initial sync is done.

## Util Server Actions

There are multiple server actions defined only to be reused by others in this module:

- requests_to_channex sends an http request to channex. We never send one without using this server action. Context 'method', 'endpoint', 'payload'.
- util_get_all_from_channex returns a full array of all records corresponding to 'endpoint'.
- get_or_create_mapping returns the x_channex_mapping corresponding to 'local_id' and 'model_type', or create one and returns it if it doesn't exist yet.
- util_log_message creates a ir.logging displayed in the debug menu to keep communication success/failure stored.

## Rate Plans (Odoo Custom Model)

A main server action "server_action_create_remove_rate_plans" that creates or deletes records from the custom model x_rate_plan. This new model is introduced to correspond 1 to 1 to channex Rate Plans.
The server action calculates which should be created/deleted based on the pricelists, room offers products and rate plan attributes, while comparing to already existing ones.
This main server actions is called by several other server actions, triggered in a lot of ways : create pricelist, create room, add rate plan attribute on room ... and uses context to leverage the computation.  
There is no modification, as this model is not meant to be modified at any time. It is created when needed and deleted when it is not relevant anymore.

# Useful Links

- Official Channex Documentation : https://docs.channex.io/
- Postman Documentation for Channex : https://documenter.getpostman.com/view/681982/RztkPpne#intro
