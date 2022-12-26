# Schema for the task database

{
    "entries" = {
        # Key is entry number - fixed forever. Key is a string representation of an integer... for reasons.
        "42" : {
            "author": 302298391969267712, # Must be non-empty and a valid discord user
            "assignee": 302298391969267712, # Optional - who is currently assigned to this bug
            "description": "Stuff", # Must be non-empty, escape input strings/etc.
            "labels": ["misc"], # Must be non-empty
            # Automatically set to "N/A" on creation
            "priority": "High", # Case sensitive for matching, do case insensitive compare for input

            # Optional. If set, the corresponding kanboard database ID
            "kanboard_id": 5

            # Automatically set to "unknown" on creation
            "complexity": "easy",

            # Optional:
            "image": None, # Might be None OR not present at all

            # If this is present, the item is closed
            "close_reason": "string"

            # Automatically added/managed
            "message_id": <discord message ID>

            # Pending notification
            # True if there has been an update to this item that the poster needs to be pinged about
            "pending_notification": True/False
        },
    },

    "kanboard": {
        # Kanboard stuff defined in task_kanboard
    }


    "next_index": 985,
    "labels": [
        "...",
        "misc"
    ],
    "complexities": {
        "easy":     ":green_circle:",
        "moderate": ":orange_circle:",
        "hard":     ":red_circle:",
        "unknown":  ":white_circle:"
    },
    "priorities": [
        "N/A",
        "Critical",
        "High",
        "Medium",
        "Low",
        "Zero"
    ],
    "notifications_disabled": [
        "302298391969267712",
        ...
    ]
}
