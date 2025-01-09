# Personal Assistant Documentation

## Overview

The `PersonalAssistant` Python script is a sophisticated command-line personal assistant that leverages voice recognition and text-to-speech capabilities to interact with users. The assistant can perform a variety of tasks including handling reminders, managing tasks, providing advice, and performing web searches. It integrates several Python libraries to offer an intuitive and interactive experience for users who wish to streamline their daily activities through voice commands.

## Features

- **Voice Recognition and Synthesis**: Utilizes `speech_recognition` for converting speech to text and `pyttsx3` for text-to-speech functionality.
- **Task Management**: Supports adding, updating, deleting, searching, and viewing tasks with due dates and priority levels.
- **Reminder Management**: Allows users to set and check reminders based on specified times.
- **Web Searches**: Can perform web searches on Google, YouTube, Google Maps, and check weather updates.
- **Personalization**: Remembers and uses the user's name, and allows updates to this information.
- **Advice Generation**: Provides random pieces of advice from a predefined list.
- **Error Handling and Logging**: Uses the `logging` module to track and record errors and operational messages.

## Dependencies

The script relies on the following external Python libraries:

- `speech_recognition` - For converting spoken language into text.
- `pyttsx3` - For text-to-speech conversion.
- `gtts` - For generating speech from text using Google's Text-to-Speech service.
- `playsound` - For playing sound files.
- `webbrowser` - For opening web pages in the browser.
- `logging` - For logging operational messages and errors.
- `tempfile` - For handling temporary files used in text-to-speech.
- `json` - For reading and writing JSON files to store user data, tasks, reminders, and advice.
- `re` - For regular expression matching.
- `datetime` - For handling date and time operations.
- `sys` - For system-specific parameters and functions.

## Usage

1. **Initialization**: Create an instance of the `PersonalAssistant` class with optional parameters for text-to-speech language and voice type.
   ```python
   assistant = PersonalAssistant(tts_language='en', tts_voice='female')
   ```
2. **Running the Assistant**: Call the `run()` method to start the assistant.
   ```python
   assistant.run()
   ```
3. **Voice Commands**: Interact with the assistant using voice commands to perform various functions such as setting reminders, managing tasks, or seeking advice.

## Interactive Commands

The assistant supports various interactive commands that users can issue:

- **Greetings**: Start a conversation with greetings such as "Hey", "Hi", or "Hello".
- **Name Query**: Inquire about the assistant's name or update it with commands like "What is your name?" or "My name is [name]."
- **Time Query**: Ask for the current time with "What's the time?"
- **Task Management**: Commands to add, update, delete, search, or view tasks, e.g., "Add task [description] due on [date] at [time] with priority [low/medium/high]."
- **Reminder Management**: Set reminders with commands like "Set reminder for [text] at [time]."
- **Advice**: Request advice using "Give me advice" or "Advice."

## Special Commands

- **Search Commands**: Perform searches on specific websites:
  - Google: "Search on Google for [term]"
  - YouTube: "Search on YouTube for [term]"
  - Maps: "Find location on Google Maps for [term]"
  - Weather: "Show the weather for [location]"

- **Fallback and Error Handling**: The assistant will handle unrecognized commands with fallback responses and log errors as needed.

## Conclusion

The `PersonalAssistant` script provides a versatile and user-friendly interface for managing tasks, reminders, and other daily activities through voice commands. By leveraging advanced speech recognition and text-to-speech technologies, it offers a hands-free, interactive experience. The system is equipped with robust error handling and logging features to ensure smooth operation and maintain user data effectively. Whether for personal or professional use, this assistant aims to enhance productivity and streamline daily routines.

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## **Disclaimer:**

Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.