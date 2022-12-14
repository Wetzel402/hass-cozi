# hass-cozi

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Configuration](#configuration)
- [Entities](#entities)
- [Services](#services)

<a name="introduction"></a>
## Introduction
A Cozi component for [Home
Assistant](https://www.home-assistant.io/), it uses the [Cozi
Website](https://www.cozi.com) APIs to to interact with your shopping and
todo lists.  This integration uses the [py-cozi](https://github.com/Wetzel402/py-cozi) python wrapper.   

A custom [_Lovelace
Card_](https://github.com/Wetzel402/cozi-card) allows the user to
interact with their lists from the frontend. 

<a name="installation"></a>
## Installation

**You only need to use one of these installation mechanisms. I recommend HACS.** 

<a name="installation-hacs"></a>
#### HACS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

Add this repository to HACS and install.

<a name="installation-manually"></a>
#### Manually
Copy the `cozi` directory into your `/config/custom_components` directory.

<a name="configuration"></a>
## Configuration

Start the configuration flow and follow the prompts to login. 

<a name="entities"></a>
### Entities

The component creates the following entities:

`sensor.cozi_lists` - Has a `lists` attribute that contains an array of your Cozi lists.<br>
`sensor.cozi_persons` - Has a `persons` attribute that contains an array of the users and assocciated Cozi IDs. 

<a name="services"></a>
### Services

The component provides the following services:

| Service             | Parameters                                                                                      | Description           |
| :---                |    :---                                                                                       |                  :--- |
| `cozi.add_list`     | `list_title` - Title or name of your list.<br>`list_type` - The list type. `shopping` or `todo`                                               | Adds a new list       |
| `cozi.remove_list`  | `list_id` - The ID Cozi assigns to your list.                                                   | Removes a list       |
| `cozi.add_item`     | `list_id` - The ID Cozi assigns to your list.<br>`item_text` - The text or name of the item to add.<br>`item_pos` - The position of the item in the list.  Zero places it at the top.                  | Adds an item to a list       |
| `cozi.edit_item`    | `list_id` - The ID Cozi assigns to your list.<br>`item_id` - The ID Cozi assigns to your item.<br>`item_text` - The text or name of the item to add.                                              | Edits an item in a list       |
| `cozi.mark_item`    | `list_id` - The ID Cozi assigns to your list.<br>`item_id` - The ID Cozi assigns to your item.<br>`status` - Status of the item.  Whether it is checked off or not. `complete` or `incomplete`    | Marks or checks off an item in a list       |
| `cozi.remove_items` | `list_id` - The ID Cozi assigns to your list.<br>`item_ids` - A list or array of IDs Cozi assigns to your items.                                 | Removes an array of items from a list regarless of whether it is marked/checked or not.     |
| `cozi.reorder_items`| `list_id` - The ID Cozi assigns to your list.<br>`list_title` - Title or name of your list.<br>`items_list` - A list or array of Cozi items.<br>`list_type` - The list type. `shopping` or `todo`                              | Reorders items in a list.      |
| `cozi.refresh      `| NA | Refresh Cozi entities.       |

<a name="service-parameters"></a>
#### Service Parameters

`item_ids`
```
- id1
- id2
- etc...
```

`items_list`
```
- status: incomplete
  itemId: id1
  itemType: header
  text: DARIY SECTION
- status: incomplete
  itemId: id2
  itemType: null
  text: milk
- status: complete
  itemId: id3
  itemType: null
  text: eggs
- etc...
```