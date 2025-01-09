import speech_recognition as sr
import pyttsx3
import random
import playsound
import webbrowser
import os
import re
import logging
import tempfile
import json
import time
import datetime
import sys
from gtts import gTTS
from time import ctime
from collections import defaultdict

# Configure logging
logging.basicConfig(filename='personal_assistant.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom Exception for the Personal Assistant
class PersonalAssistantError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# PersonalAssistant Class that handles user interactions
class PersonalAssistant:
    def __init__(self, tts_language='en', tts_voice='female', default_name='User'):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.person_name = default_name  # Set default name here
        self.tts_language = tts_language
        self.tts_voice = tts_voice
        self.memory_file = 'assistant_memory.json'
        self.user_details_file = 'usr_info.json'
        self.advice_file = 'advice.json'
        self.reminders_file = 'reminders.json'
        self.tasks = []
        self.advice_list = []
        self.reminders = []
        self.waiting_for_response = False
        self._set_voice()
        self._load_user_details()
        self._load_memory()
        self._load_advice()
        self._load_reminders()

    def _set_voice(self):
        voices = self.engine.getProperty('voices')
        selected_voice = None
        for voice in voices:
            if self.tts_voice == 'female' and 'female' in voice.name.lower():
                selected_voice = voice
                break
            elif self.tts_voice == 'male' and 'male' in voice.name.lower():
                selected_voice = voice
                break
        if selected_voice:
            self.engine.setProperty('voice', selected_voice.id)
            logging.info(f"Selected voice: {selected_voice.name}")
        else:
            logging.warning("Requested voice not found. Using default voice.")

    def _there_exists(self, pattern, text):
        return re.search(pattern, text, re.IGNORECASE) is not None
    
    def _load_user_details(self):
        if os.path.exists(self.user_details_file):
            with open(self.user_details_file, 'r') as f:
                data = json.load(f)
                self.person_name = data.get('person_name', self.person_name)
        else:
            self.person_name = 'User'

    def _save_user_details(self):
        with open(self.user_details_file, 'w') as f:
            json.dump({
                'person_name': self.person_name
            }, f)
    
    def _load_advice(self):
        try:
            with open(self.advice_file, 'r') as f:
                self.advice_list = json.load(f)
        except FileNotFoundError:
            logging.error("Advice file not found. Please ensure the file exists.")
            self.advice_list = []
        except json.JSONDecodeError:
            logging.error("Error decoding advice file. Ensure it's properly formatted.")
            self.advice_list = []

    def _record_audio(self):
        """Record audio and return the transcribed text."""
        with sr.Microphone() as source:
            logging.info("Listening for audio...")
            audio = self.recognizer.listen(source)
            try:
                voice_data = self.recognizer.recognize_google(audio) # type: ignore
                logging.info(f"Recognized: {voice_data}")
            except sr.UnknownValueError:
                self._assistant_speak("Sorry, I didn't catch that.")
                return ""
            except sr.RequestError:
                self._assistant_speak("Sorry, my speech service is down.")
                return ""
            return voice_data.lower()

    def _assistant_speak(self, message):
        """Use text-to-speech to speak the message."""
        try:
            tts = gTTS(text=message, lang=self.tts_language)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.close()
                tts.save(temp_file.name)
                playsound.playsound(temp_file.name)
                logging.info(f"Assistant says: {message}")
                os.remove(temp_file.name)
        except Exception as e:
            logging.error(f"Error in TTS: {e}")
            self.engine.say("There was an error in generating speech.")
            self.engine.runAndWait()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                self.tasks = json.load(f).get('tasks', [])
        else:
            self.tasks = []

    def _save_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump({
                    'tasks': self.tasks
                }, f)

    def _load_reminders(self):
        """Load reminders from the JSON file."""
        if os.path.exists(self.reminders_file):
            with open(self.reminders_file, 'r') as f:
                self.reminders = json.load(f)
        else:
            self.reminders = []

    def _save_reminders(self):
        """Save reminders to the JSON file."""
        with open(self.reminders_file, 'w') as f:
            json.dump(self.reminders, f, indent=4)

    def _ask_if_more_help_needed(self):
        self._assistant_speak("Is there anything else I can assist you with?")
        self.waiting_for_response = True

    def _handle_greetings(self):
        greetings = [f"Hey, how can I help you {self.person_name}?", f"Hello {self.person_name}!", "I'm here to help. What do you need?", "How can I assist you today?"]
        self._assistant_speak(random.choice(greetings))
        self._ask_if_more_help_needed()

    def _handle_name_query(self):
        if self.person_name:
            self._assistant_speak(f"My name is Cortex. You can call me {self.person_name}.")
        else:
            self._assistant_speak("My name is Cortex. What's your name?")
        self._ask_if_more_help_needed()

    def _handle_name_update(self, name):
        self.person_name = name
        self._assistant_speak(f"Okay, I'll remember that your name is {self.person_name}.")
        self._save_user_details()
        self._ask_if_more_help_needed()

    def _handle_time_query(self):
        current_time = datetime.datetime.now().strftime("%H:%M")
        self._assistant_speak(f"The current time is {current_time}.")
        self._ask_if_more_help_needed()

    def _handle_search(self, search_term, site):
        url_map = {
            "google": f"https://google.com/search?q={search_term}",
            "youtube": f"https://www.youtube.com/results?search_query={search_term}",
            "maps": f"https://google.com/maps/place/{search_term}",
            "weather": f"https://google.com/search?q={search_term} weather"
        }
        url = url_map.get(site)
        if url:
            webbrowser.get().open(url)
            self._assistant_speak(f"Here is what I found for {search_term} on {site}.")
        else:
            self._assistant_speak("Sorry, I couldn't find the site.")
        self._ask_if_more_help_needed()

    def _handle_fallback(self):
        self._assistant_speak("I didn't understand that command.")
        self._ask_if_more_help_needed()

    def _handle_follow_up(self, voice_data):
        follow_up_patterns = {
            'yes': r'\b(yes|yeah|yep|sure|okay)\b',
            'no': r'\b(no|thanks|not at the moment|not now|nope)\b',
            'exit': r'\b(exit|quit|goodbye)\b'
        }

        for key, pattern in follow_up_patterns.items():
            if self._there_exists(pattern, voice_data):
                if key == 'yes':
                    self._ask_if_more_help_needed()  # Prompt for more assistance
                elif key == 'no':
                    self._assistant_speak("Alright, I'll be here if you need anything.")
                    self.waiting_for_response = False
                elif key == 'exit':
                    self._assistant_speak("Goodbye!")
                    exit()
                return

        self._assistant_speak("Sorry, I didn't understand that. Can you please respond with 'yes' or 'no'?")

    def _handle_task_add(self, task_details):
        try:
            match = re.match(r'(.*)\s+due\s+on\s+(\d{4}-\d{2}-\d{2})\s+at\s+(\d{2}:\d{2})\s+with\s+priority\s+(low|medium|high)', task_details)
            if match:
                task_desc = match.group(1).strip()
                due_date = f"{match.group(2)} {match.group(3)}"
                priority = match.group(4)
                self.tasks.append({
                    'task': task_desc,
                    'due_date': due_date,
                    'priority': priority,
                    'status': 'pending',
                    'created_at': str(datetime.datetime.now())
                })
                self._save_memory()
                self._assistant_speak(f"Task '{task_desc}' with due date {due_date} and priority {priority} added.")
            else:
                self._assistant_speak("Please provide the task description, due date, time, and priority level.")
        except Exception as e:
            self._assistant_speak(f"Error adding task: {e}")

    def _handle_task_update(self, task_details):
        try:
            match = re.match(r'(\d+)\s+(.*)', task_details)
            if match:
                task_id = int(match.group(1))
                updates = match.group(2)
                if task_id >= len(self.tasks) or task_id < 0:
                    raise PersonalAssistantError(f"Task ID {task_id} not found.")
                task = self.tasks[task_id]
                
                update_match = re.match(r'(due\s+on\s+(\d{4}-\d{2}-\d{2})\s+at\s+(\d{2}:\d{2}))?\s*(priority\s+(low|medium|high))?\s*(status\s+(completed|pending))?', updates)
                
                if update_match:
                    if update_match.group(2) and update_match.group(3):
                        task['due_date'] = f"{update_match.group(2)} {update_match.group(3)}"
                    if update_match.group(5):
                        task['priority'] = update_match.group(5)
                    if update_match.group(7):
                        task['status'] = update_match.group(7)
                    self.tasks[task_id] = task
                    self._save_memory()
                    self._assistant_speak(f"Task ID {task_id} updated.")
                else:
                    self._assistant_speak("Could not parse the update details.")
            else:
                self._assistant_speak("Please specify the task ID and the details to update.")
        except PersonalAssistantError as e:
            logging.error(f"Task update error: {e}")
            self._assistant_speak(str(e))
        except Exception as e:
            logging.error(f"Unexpected error updating task: {e}")
            self._assistant_speak("Error updating task.")

    def _handle_task_delete(self, task_id):
        try:
            task_id = int(task_id)
            if 0 <= task_id < len(self.tasks):
                del self.tasks[task_id]
                self._save_memory()
                self._assistant_speak(f"Task ID {task_id} deleted.")
            else:
                raise PersonalAssistantError(f"Task ID {task_id} not found.")
        except PersonalAssistantError as e:
            logging.error(f"Task delete error: {e}")
            self._assistant_speak(str(e))
        except Exception as e:
            logging.error(f"Unexpected error deleting task: {e}")
            self._assistant_speak("Error deleting task.")

    def _handle_task_search(self, keyword):
        try:
            pattern = re.compile(keyword, re.IGNORECASE)
            results = []
            for i, task in enumerate(self.tasks):
                if 'task' in task and pattern.search(task['task']):
                    task_info = f"ID {i}: {task.get('task', 'No description')}, Due: {task.get('due_date', 'No due date')}, Priority: {task.get('priority', 'No priority')}, Status: {task.get('status', 'No status')}"
                    results.append(task_info)
            
            if results:
                response = "Tasks found: " + ", ".join(results)
                self._assistant_speak(response)
            else:
                self._assistant_speak("No tasks found matching your query.")
        except Exception as e:
            logging.error(f"Error searching tasks: {e}")
            self._assistant_speak("Error searching tasks.")

    def _handle_task_view(self):
        try:
            if self.tasks:
                response = "All tasks: " + ", ".join([f"ID {i}: {task['task']}, Due: {task['due_date']}, Priority: {task['priority']}, Status: {task['status']}" for i, task in enumerate(self.tasks)])
                self._assistant_speak(response)
            else:
                self._assistant_speak("No tasks available.")
        except Exception as e:
            logging.error(f"Error viewing tasks: {e}")
            self._assistant_speak("Error viewing tasks.")

    def _handle_advice(self):
        if self.advice_list:
            advice = random.choice(self.advice_list)
            self._assistant_speak(advice)
        else:
            self._assistant_speak("I don't have any advice to offer at the moment.")
        self._ask_if_more_help_needed()

    def set_reminder(self, command):
        try:
            # Extract reminder details from the command
            match = re.search(r'\b(reminder)\b\s+for\s+(.*)\s+at\s+(\d{2}:\d{2})', command)
            if match:
                reminder_text = match.group(2)
                reminder_time = match.group(3)
                
                # Validate time format
                try:
                    reminder_time = datetime.datetime.strptime(reminder_time, "%H:%M").time()
                except ValueError:
                    self._assistant_speak("Invalid time format. Please use HH:MM.")
                    return
                
                # Create reminder datetime
                now = datetime.datetime.now()
                reminder_datetime = datetime.datetime.combine(now.date(), reminder_time)
                
                # Store the reminder in JSON format
                reminder = {
                    'reminder': reminder_text,
                    'reminder_time': reminder_datetime.strftime("%H:%M:%S"),
                    'created_at': now.strftime("%Y-%m-%d %H:%M:%S")
                }
                self.reminders.append(reminder)
                self._save_reminders()
                
                self._assistant_speak(f"Reminder set for {reminder_text} at {reminder_time}.")
            else:
                self._assistant_speak("Please specify the reminder text and time in the format 'reminder for <text> at HH:MM'.")
        except Exception as e:
            self._assistant_speak("An error occurred while setting the reminder.")
            print(f"Set reminder error: {e}")

    def check_reminders(self):
        try:
            now = datetime.datetime.now()
            reminder_count = defaultdict(int)
            reminders_to_notify = []

            for reminder in self.reminders:
                reminder_time = datetime.datetime.strptime(reminder['reminder_time'], "%H:%M:%S").time()
                reminder_datetime = datetime.datetime.combine(now.date(), reminder_time)
                
                if now >= reminder_datetime:
                    reminder_count[reminder_time] += 1
                    reminders_to_notify.append(reminder)

            # Notify about reminders
            for reminder_time, count in reminder_count.items():
                self._assistant_speak(f"Reminder: {count} tasks are due at {reminder_time}.")
            
            # Remove the reminders that have been processed
            for reminder in reminders_to_notify:
                self.reminders.remove(reminder)
                
            self._save_reminders()
        except Exception as e:
            self._assistant_speak("An error occurred while checking reminders.")
            print(f"Check reminders error: {e}")

    def check_low_priority_reminders(self, current_time, due_date):
        due_datetime = datetime.datetime.combine(due_date, datetime.time(0))
        time_remaining = due_datetime - current_time
        reminder_intervals = [datetime.timedelta(hours=5), datetime.timedelta(hours=1), datetime.timedelta(minutes=30), datetime.timedelta(minutes=5)]
        for interval in reminder_intervals:
            if time_remaining <= interval:
                self._assistant_speak(f"Reminder: Task is due soon.")
                break

    def check_medium_priority_reminders(self, current_time, due_date):
        due_datetime = datetime.datetime.combine(due_date, datetime.time(0))
        time_remaining = due_datetime - current_time
        if time_remaining <= datetime.timedelta(days=5):
            self._assistant_speak(f"Reminder: Task is due in {time_remaining.days} days.")
        elif time_remaining <= datetime.timedelta(days=1):
            hours_left = (time_remaining - datetime.timedelta(days=1)).total_seconds() // 3600
            self._assistant_speak(f"Reminder: Task is due in {int(hours_left)} hours.")

    def check_high_priority_reminders(self, current_time, due_date):
        due_datetime = datetime.datetime.combine(due_date, datetime.time(0))
        time_remaining = due_datetime - current_time
        if time_remaining <= datetime.timedelta(days=10):
            self._assistant_speak(f"Reminder: Task is due in {time_remaining.days} days.")
        elif time_remaining <= datetime.timedelta(days=3):
            hours_left = (time_remaining - datetime.timedelta(days=3)).total_seconds() // 3600
            self._assistant_speak(f"Reminder: Task is due in {int(hours_left)} hours.")
        elif time_remaining <= datetime.timedelta(hours=1):
            self._assistant_speak(f"Reminder: Task is due soon.")

    def _respond(self, voice_data):
        command_patterns = {
            'greeting': r'\b(hey|hi|hello)\b',
            'name_query': r'\b(what is your name|what\'s your name|tell me your name)\b',
            'name_update': r'\bmy name is\b\s+(.*)',
            'time_query': r'\bwhat\'s the time\?\b',
            'search_google': r'\bsearch on google for\b\s+(.*)',
            'search_youtube': r'\bsearch on youtube for\b\s+(.*)',
            'search_maps': r'\bfind location on google map for\b\s+(.*)',
            'weather_query': r'\bshow the weather for\b\s+(.*)',
            'task_add': r'\b(add|create)\b\s+task\s+(.*)',
            'task_update': r'\b(update|modify)\s+task\s+(\d+)\s+(.*)',
            'task_delete': r'\b(delete|remove)\s+task\s+(\d+)\b',
            'task_search': r'\b(search|find)\s+task\s+(.*)\b',
            'task_view': r'\b(view|show)\s+tasks\b',
            'advice_query': r'\b(give me advice|advice)\b',
            'reminder_add': r'\b(set|add|create)\b\s+reminder\s+for\s+(.*)\s+at\s+(\d{2}:\d{2})',
            'exit': r'\b(exit|quit|goodbye)\b'
        }

        for key, pattern in command_patterns.items():
            match = re.search(pattern, voice_data)
            if match:
                handler = getattr(self, f'_handle_{key}', None)
                if handler:
                    if key in ['task_update', 'task_delete', 'task_search']:
                        task_id = match.group(2) if key != 'task_search' else None
                        keyword = match.group(3) if key == 'task_search' else None
                        if task_id is not None:
                            handler(task_id)
                        elif keyword is not None:
                            handler(keyword)
                    elif key == 'reminder_add':
                        reminder_details = match.group(2)
                        reminder_time = match.group(3)
                        handler(reminder_details, reminder_time)
                    else:
                        task_details = match.group(2) if key == 'task_add' else None
                        if task_details:
                            handler(task_details)
                        else:
                            handler()
                return

        self._handle_fallback()

    def run(self):
        self._assistant_speak("Hey, How can I help you?")
        self.waiting_for_response = True

        while True:
            voice_data = self._record_audio()
            if voice_data:
                if self.waiting_for_response:
                    self._handle_follow_up(voice_data)
                else:
                    self._respond(voice_data)

            # Periodically check for reminders
            self.check_reminders()
            # Sleep for a while to avoid checking too frequently
            time.sleep(60)  # Check every 60 seconds

# Entry point for the application
if __name__ == "__main__":
    assistant = PersonalAssistant(tts_language='en', tts_voice='female')
    assistant.run()
    sys.exit(0)
