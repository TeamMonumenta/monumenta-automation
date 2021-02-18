
#!/usr/bin/env python3

import asyncio
import discord
import os
import json
import sys
import re
import random
import yaml
import kanboard
from functools import cmp_to_key
from collections import OrderedDict
from pprint import pprint, pformat

from interactive_search import InteractiveSearch
from common import get_list_match, datestr, split_string

# Data Schema
'''
{
    "project_id": 5,

    # Map of priorities to swimlanes
    "swimlanes": {
        "N/A": 0
        "Critical": 1
        "High": 2
        "Medium": 3
        "Low": 5
        "Zero": 5
    },

    # Labels to colors
    "colors": [
        ("Build", "Yellow"),
        ...
    ],

    # Map of complexities to column
    "columns": {
        "easy":     1,
        "moderate": 2,
        "hard":     3,
        "unknown":  4,
    }
}
'''

class TaskKanboard(object):
    def __init__(self, task_database, kanboard_client):
        """
        """
        self._task_database = task_database
        self._kanboard_client = kanboard_client
        self._cached_tags = None

        # Map of priorities to scores - not saved anywhere, currently hardcoded
        self._scores = {
            "easy":     1,
            "moderate": 2,
            "hard":     4,
            "unknown":  2,
        }

    @classmethod
    async def create_kanboard(cls, task_database, kb: kanboard.Client, title: str):
        """
        Creates a new kanboard with the proper configuration but doesn't load anything into it
        Caller probably wants to call .update_all_entries() and .save() afterwards
        """

        tk = TaskKanboard(task_database, kb)

        project_id = await kb.create_project_async(name=title)
        tk._project_id = project_id

        # Create columns, deleting originals
        columns = {}
        orig_columns = await kb.getColumns_async(project_id=project_id)
        for complexity in task_database._complexities:
            columns[complexity] = await kb.addColumn_async(project_id=project_id, title=complexity)
        for column in orig_columns:
            await kb.removeColumn_async(column_id=column["id"])
        tk._columns = columns

        swimlanes = {}
        orig_swimlanes = await kb.getAllSwimlanes_async(project_id=project_id)
        for priority in task_database._priorities:
            swimlanes[priority] = await kb.addSwimlane_async(project_id=project_id, name=priority)
        for swimlane in orig_swimlanes:
            await kb.removeSwimlane_async(project_id=project_id, swimlane_id=swimlane["id"])
        tk._swimlanes = swimlanes

        # Same sane default... can edit the save file to improve these
        tk._colors = [
            ("kaul", "green"),
            ("horseman", "lime"),
            ("server", "amber"),
            ("boss", "deep_orange"),
            ("class", "teal"),
            ("fred", "light_green"),
            ("item", "yellow"),
            ("advancement", "dark_grey"),
            ("mob", "orange"),
            ("plugin", "pink"),
            ("quest", "purple"),
            ("cmd", "red"),
            ("build", "blue"),
            ("misc", "grey"),
        ]

        return tk

    @classmethod
    def load_kanboard(cls, task_database, kb: kanboard.Client, config):
        tk = TaskKanboard(task_database, kb)

        tk._project_id = config["project_id"]
        tk._swimlanes = config["swimlanes"]
        tk._colors = config["colors"]
        tk._columns = config["columns"]

        return tk

    def save(self) -> dict:

        savedata = {
            'project_id': self._project_id,
            'swimlanes': self._swimlanes,
            'colors': self._colors,
            'columns': self._columns,
        }

        return savedata

    def get_color(self, labels: [str]) -> str:
        for label, color in self._colors:
            if label in labels:
                return color

        return self._colors[-1][1]

    # True = this changed something and need to save the database
    # False = nothing changed
    async def on_webhook_post(self, json_msg) -> bool:

        if "event_name" not in json_msg or "event_data" not in json_msg or "task" not in json_msg["event_data"]:
            print(f"Warning: Got invalid webhook request: {json_msg}", flush=True)
            return False

        task = json_msg["event_data"]["task"]

        if not "project_id" in task or int(task["project_id"]) != int(self._project_id):
            # Message meant for other project, silently ignore
            return False

        for field in ["reference", "column_id", "swimlane_id"]:
            if not field in task:
                print(f"Warning: task missing reference field {field}: {json_msg}", flush=True)
                return False

        # A str, which is the same as the key for entries
        kanboard_id = task["id"]
        index = task["reference"]
        if not index in self._task_database._entries:
            print(f"Warning: task references nonexistent entry: {json_msg}", flush=True)
            return False

        entry = self._task_database._entries[index]

        author = "unknown"
        if "event_author" in json_msg:
            author = json_msg["event_author"]

        msg = None
        if json_msg["event_name"] == "task.close":
            if "close_reason" not in entry:
                msg = f"User {author} closed {self._task_database._descriptor_single} #{index}"
                entry["close_reason"] = "Fixed"

        elif json_msg["event_name"] == "task.open":
            msg = f"User {author} reopened {self._task_database._descriptor_single} #{index}"
            if "close_reason" in entry:
                entry.pop("close_reason")

        else:
            column_id = int(task["column_id"])
            swimlane_id = int(task["swimlane_id"])

            complexity = None
            for key, value in self._columns.items():
                if value == column_id:
                    complexity = key
            if complexity is None:
                print(f"Warning: Could not determine complexity for task: {json_msg}", flush=True)
                return False


            priority = None
            for key, value in self._swimlanes.items():
                if value == swimlane_id:
                    priority = key
            if priority is None:
                print(f"Warning: Could not determine priority for task: {json_msg}", flush=True)
                return False

            complexity_changed = False

            if priority != entry["priority"] and complexity == entry["complexity"]:
                msg = f"User {author} set priority of {index} to {priority}"
                entry["priority"] = priority
            if priority == entry["priority"] and complexity != entry["complexity"]:
                msg = f"User {author} set complexity of {index} to {complexity}"
                entry["complexity"] = complexity
                complexity_changed = True
            if priority != entry["priority"] and complexity != entry["complexity"]:
                msg = f"User {author} set priority of {index} to {priority} and complexity to {complexity}"
                entry["priority"] = priority
                entry["complexity"] = complexity
                complexity_changed = True

        if msg is None:
            # Nothing changed
            return False

        if complexity_changed:
            # Update score
            result = await self._kanboard_client.updateTask_async(
                id=kanboard_id,
                score=self._scores[entry["complexity"]]
            )

            if not result:
                # Don't fail here - either way, we want to update Discord at this point
                print(f"Warning: Failed to update kanboard_id: {kanboard_id}", flush=True)
                raise ValueError(f"Failed to modify kanboard task id: {kanboard_id}")

        print(msg, flush=True)

        # Update the entry
        await self._task_database.send_entry(index, entry, kanboard_update=False)

        # Need to save after this
        return True

    async def update_entry(self, entry_id: int, entry: dict) -> bool:
        """
        Updates a kanboard entry. If the entry doesn't have a kanboard_id, one will be created.
        Returns true if the entry was modified, false otherwise (to indicate a save is needed)
        """

        kanboard_id = None
        if "kanboard_id" in entry:
            kanboard_id = entry["kanboard_id"]
            existing_task = await self._kanboard_client.getTask_async(task_id=kanboard_id)

            if not existing_task:
                print(f"Warning: Failed to find kanboard_id: {kanboard_id}", flush=True)
                kanboard_id = None


        ### Create task if it doesn't exist
        if kanboard_id is None:
            kanboard_id = await self._kanboard_client.createTask_async(title="Placeholder", project_id=self._project_id)
            if not kanboard_id:
                raise ValueError("Failed to create kanboard task")

        ### Update description, color, reference ID
        result = await self._kanboard_client.updateTask_async(
            id=kanboard_id,
            title=entry["description"],
            color_id=self.get_color(entry["labels"]),
            score=self._scores[entry["complexity"]],
            reference=str(entry_id)
        )

        if not result:
            raise ValueError(f"Failed to modify kanboard task id: {kanboard_id}")


        ### Update image if it exists
        if "image" in entry and entry["image"] is not None:
            result = await self._kanboard_client.updateTask_async(
                id=kanboard_id,
                description=entry["image"]
            )
            if not result:
                print(f"Warning: Failed to change task position for kanboard task id: {kanboard_id}", flush=True)


        ### Update tags/labels
        result = await self._kanboard_client.setTaskTags_async(project_id=self._project_id, task_id=kanboard_id, tags=entry["labels"])
        if not result:
            raise ValueError(f"Failed to change tags for kanboard task id: {kanboard_id}")


        ### Update column / swimlane
        result = await self._kanboard_client.moveTaskPosition_async(
            project_id=self._project_id,
            task_id=kanboard_id,
            column_id=self._columns[entry["complexity"]],
            position=1,
            swimlane_id=self._swimlanes[entry["priority"]]
        )

        if not result:
            print(f"Warning: Failed to change task position for kanboard task id: {kanboard_id}", flush=True)


        ### Update closed/opened status
        if "close_reason" in entry:
            result = await self._kanboard_client.closeTask_async(task_id=kanboard_id)
        else:
            result = await self._kanboard_client.openTask_async(task_id=kanboard_id)

        if not result:
            raise ValueError(f"Failed to change closed status for kanboard task id: {kanboard_id}")


        ### Save kanboard_id
        if "kanboard_id" not in entry or entry["kanboard_id"] != kanboard_id:
            entry["kanboard_id"] = kanboard_id
            return True
        return False


    async def update_all_entries(self) -> bool:
        needs_save = False
        # Iterate a shallow copy of the entries table so new reports don't break it
        for item_id in self._task_database._entries.copy():
            try:
                if await self.update_entry(int(item_id), self._task_database._entries[item_id]):
                    needs_save = True
            except Exception as ex:
                print(f"Got error, continuing anyway: {str(ex)}")

        return needs_save
