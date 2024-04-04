# %%
import datetime
import tkinter as tk
from tkinter import ttk, font, simpledialog, messagebox
import json
import random
import re
import os
import sys
from pymongo import MongoClient
import threading
import traceback
import re


def compare_norm_texts(text1, text2):
    """
    Compare two normalized texts and return True if they are equal, False otherwise.
    
    Parameters:
    text1 (str): The first text to compare.
    text2 (str): The second text to compare.
    
    Returns:
    bool: True if the normalized texts are equal, False otherwise.
    """
    def normalize_string(input_string):
        # Remove symbols using regular expression
        normalized_string = re.sub(r'[^\w\s]', '', input_string)
        
        # Convert to lowercase
        normalized_string = normalized_string.lower()
        
        # Remove spaces
        normalized_string = normalized_string.replace(' ', '')
        
        return normalized_string

    if normalize_string(text1) == normalize_string(text2):
        return True
    
    else: 
        return False

class LabelSeparator(tk.Frame):
    """
    A custom tkinter frame that combines a separator and a label.

    Parameters:
        parent (tk.Widget): The parent widget.
        text (str): The text to be displayed in the label.

    Attributes:
        separator (ttk.Separator): The separator widget.
        label (ttk.Label): The label widget.

    Usage:
        label_separator = LabelSeparator(parent, text="Hello, World!")
    """
    def __init__(self, parent, text="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # The separator is stretched across the entire width of the frame
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.separator.grid(row=0, column=0, sticky="ew", pady=0)

        # The label is placed above the separator
        self.label = ttk.Label(self, text=text)
        self.label.grid(row=0, column=0)

        # Configure the frame to expand the column, allowing the separator to fill the space
        self.grid_columnconfigure(0, weight=1)

        # Adjust label placement using the 'sticky' parameter to center it
        # 'ns' means north-south, which centers the label vertically in the grid cell
        self.label.grid_configure(sticky="ns")

class FontSizeChanger():
    """A class that represents a font size changer widget in a tkinter application.

    Args:
        position (object): The position of the widget.
        root (object): The root frame of the tkinter application.
        font_size (int, optional): The initial font size. Defaults to 12.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    def __init__(self, position, root, font_size=12):
        self.root = root
        self.font_size = font_size

        # "+" button to increase font size
        increase_font_button = tk.Button(position, text="+", command=self.increase_font_size)
        increase_font_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        # "-" button to decrease font size
        decrease_font_button = tk.Button(position, text="-", command=self.decrease_font_size)
        decrease_font_button.pack(side=tk.LEFT, padx=(0, 10), pady=10)

    def increase_font_size(self):
        """Increases the font size by 1 if it's less than 30.
        Also updates the font size and window size.
        """
        if self.font_size < 30:
            self.font_size += 1
            self.update_font_size(self.root)
            self.update_window_size(enlarge=True)

    def decrease_font_size(self):
        """Decreases the font size by 1 if it's greater than 10.
        Also updates the font size and window size.
        """
        if self.font_size > 10:
            self.font_size -= 1
            self.update_font_size(self.root)
            self.update_window_size(enlarge=False)

    def update_font_size_wrapper(self):
        """Prepares to update the whole program using a recursive function that takes the root frame and updates all the child widgets.
        """
        self.update_font_size(self.root)

    def update_font_size(self, widget):
        """A recursive function to update the font size of a widget and its child widgets.

        Args:
            widget (object): The tkinter object to update the font size for.
        """
        new_font = font.Font(size=self.font_size)

        try:
            widget.configure(font=new_font)
        except:
            pass

        for child in widget.winfo_children():
            self.update_font_size(child)

    def update_window_size(self, enlarge):
        """Updates the window size to accommodate the text with the new font size.

        Args:
            enlarge (boolean): If True, makes the window bigger. If False, makes the window smaller.
        """
        if enlarge:
            num = 40
        else:
            num = -40

        # Get the current size of the window
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()

        # Calculate a new height, but ensure it's within the screen's limits
        screen_height = self.root.winfo_screenheight()
        new_height = min(current_height + num, screen_height)

        # Calculate a new Width, but ensure it's within the screen's limits
        screen_width = self.root.winfo_screenwidth()
        new_width = min(current_width + num*2, screen_width)

        # Update the window size using geometry
        self.root.geometry(f"{new_width}x{new_height}")
        self.root.update()

class RequireRewrite():
    def __init__(self, position, root):
        """
        Initializes an instance of the RequireRewrite class.

        Args:
            position: The position to add the rewrites_frame_base widget.
            root: The root tkinter object.

        Returns:
            None
        """
        self.root = root
        
        # Frame for Rewrite widgets
        self.rewrites_frame_base = tk.Frame(root)
        position.add(self.rewrites_frame_base, stretch="always", height=30)
        LabelSeparator(self.rewrites_frame_base, text="Requires Rewrites").pack(fill=tk.X)


        # Entry for "requires_rewrite"
        self.requires_rewrite_frame = tk.Frame(self.rewrites_frame_base)
        self.requires_rewrite_frame.pack(fill=tk.BOTH, padx=10, pady=10)

        self.requires_rewrite_label = tk.Label(self.requires_rewrite_frame, text="Question Requires Rewrite:")
        self.requires_rewrite_label.grid(row=0, column=0, sticky='w', padx=5, pady=0)
        self.requires_rewrite_entry = tk.Entry(self.requires_rewrite_frame, width = 3)
        self.requires_rewrite_entry.grid(row=0, column=1, sticky='wn', padx=5, pady=0)
        

        self.requires_rewrite_entry.bind("<KeyRelease>", lambda event: self.handle_require_rewrite_input())
        self.requires_rewrite_entry.bind("<FocusIn>", self.select_text)

    def update_entry_text(self, dialog_id, turn_num, json_data):
        """
        Updates the text inside requires_rewrite Entry widget.

        Args:
            dialog_id: The ID of the dialog.
            turn_num: The turn number.
            json_data: The JSON data.

        Returns:
            None
        """
        # Clear the Entry widget
        self.requires_rewrite_entry.delete(0, tk.END)

        # Fetch and insert text into the Entry widget
        count_turns = len(json_data[dialog_id]['annotations'])
        if turn_num >= count_turns: 
            raise Exception(f"The turn is not in the annotations list, it has {count_turns}, but the turn is {turn_num}")
        
        entry_text = json_data[dialog_id]['annotations'][int(turn_num)].get('requires_rewrite', '')
        if entry_text is not None and entry_text != -1:
            self.requires_rewrite_entry.insert(0, entry_text)
        
        # Select all text in the Entry widget
        self.requires_rewrite_entry.select_range(0, tk.END)
                   
    def handle_require_rewrite_input(self, allowed_values=[0,1]):
        """
        Checks if the input inside the requires_rewrite Entry widget is valid.

        Args:
            allowed_values: A list of allowed values.

        Returns:
            bool: True if the input is valid, False otherwise.
        """
        
        # Retrieve text from the Entry widget
        new_value = self.get_requires_rewrite()
        
        if allowed_values is None:
            return True
        
        if new_value in allowed_values :
            return True
        
        elif new_value == None:
            self.set_requires_rewrite(None)
            return True

        else:
            self.requires_rewrite_entry.delete(0, tk.END)
            tk.messagebox.showwarning("Invalid Score", f"Invalid input '{str(new_value)}'. Allowed values are: 0 or 1")
            return False
        
    def update_json_data(self, dialog_id, turn_id, json_data):
        """
        Updates the JSON data with the new value from the requires_rewrite Entry widget.

        Args:
            dialog_id: The ID of the dialog.
            turn_id: The turn ID.
            json_data: The JSON data.

        Returns:
            dict: The modified JSON data.
        """
        new_value = self.requires_rewrite_entry.get()
        
        if new_value == '':
            new_value = None
            json_data[dialog_id]['annotations'][turn_id]['requires_rewrite'] = new_value
            
        else:
            json_data[dialog_id]['annotations'][turn_id]['requires_rewrite'] = int(new_value)
        
        return json_data
        
    def is_empty(self):
        """
        Checks if the requires_rewrite Entry widget is empty.

        Returns:
            bool: True if empty, False otherwise.
        """
        if self.get_requires_rewrite() == None:
            return True
        return False

    def select_text(self, event=None):
        """
        Highlights all the text when selecting the requires_rewrite Entry widget.

        Args:
            event: The event when someone presses the Entry widget.

        Returns:
            None
        """
        event.widget.select_range(0,tk.END)

    def requires_rewrite_positive(self):
        """
        Checks if the requires_rewrite Entry widget is 1.

        Returns:
            bool: True if 1, False otherwise.
        """
        if self.get_requires_rewrite() == 1:
            return True
        return False
    
    def get_requires_rewrite(self):
        """
        Gets the value of the requires_rewrite Entry widget.

        Returns:
            string: The value of the requires_rewrite Entry widget.
        """
        if self.requires_rewrite_entry.get() == '':
            return None
        
        elif self.requires_rewrite_entry.get().isdigit():
            return int(self.requires_rewrite_entry.get())
        
        else:
            return self.requires_rewrite_entry.get()
        
    def set_requires_rewrite(self, value):
        """
        Sets the value of the requires_rewrite Entry widget.

        Args:
            value (string): The value to set the requires_rewrite Entry widget to.

        Returns:
            None
        """
        if value is None:
            self.requires_rewrite_entry.delete(0, tk.END)
            return
        
        self.requires_rewrite_entry.delete(0, tk.END)
        self.requires_rewrite_entry.insert(0, value)
    
class DialogFrame():
    def __init__(self, position, root):
        """
        Initializes the DialogFrame class.

        Args:
            position: The position of the frame.
            root: The root window.
            
        """
        self.root = root

        # Frame for Dialog widgets
        self.dialog_frame_base = tk.Frame(root, height=1)
        position.add(self.dialog_frame_base, stretch="always", height=200)
        LabelSeparator(self.dialog_frame_base, text="Dialog Text").pack(fill=tk.X, side=tk.TOP)

        # tk.Text for dialog
        self.dialog_text = tk.Text(self.dialog_frame_base, wrap=tk.WORD, state='disabled')
        self.dialog_text.pack(fill=tk.BOTH, padx=10, pady=10)  

    def update_dialog_text(self, new_text):
        """
        Updates the DialogFrame window with new text.

        Args:
            new_text (string): The new text to update.
        """
        # Enable the widget to modify text
        self.dialog_text.config(state='normal')

        # Update the text
        self.dialog_text.delete(1.0, tk.END)
        self.dialog_text.insert(tk.END, new_text)

        # Disable the widget to prevent user edits
        self.dialog_text.config(state='disabled')

        # Scroll to the end of the dialog text
        self.dialog_text.see(tk.END)

    def display_dialog(self, dialog_id, turn_num, json_data):
        """
        Displays a specific dialog in the DialogFrame window.

        Args:
            dialog_id (int): The ID of the dialog to access.
            turn_num (int): The turn number until which to create the text.
            json_data (string): The JSON data to use.
        """
        dialog_text_content = ""
        
        turn_num_real = json_data[dialog_id]['annotations'][turn_num]['turn_num']
          
        for dialog in json_data[dialog_id]['dialog']:
            if dialog['turn_num'] <= turn_num_real:
                # Format each turn
                turn_text = f"Turn {dialog['turn_num']}:\n"
                turn_text += f"Q: {dialog['original_question']}\n"
                if dialog['turn_num'] != turn_num_real:
                    turn_text += f"A: {dialog['answer']}\n"
                turn_text += "-" * 40 + "\n"  # Separator line

                # Append this turn's text to the dialog text content
                dialog_text_content += turn_text 

        # Update the dialog text widget using the new method
        self.update_dialog_text(dialog_text_content)

class ProgressIndicator():
    def __init__(self, position):
        """
        Initializes a ProgressIndicator object.

        Args:
            position (tkinter.Tk): The position where the labels will be placed.
        """
        # Current dialog and turn labels
        self.current_dialog_label = tk.Label(position, text="")
        self.current_dialog_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.current_turn_label = tk.Label(position, text="")
        self.current_turn_label.pack(side=tk.LEFT, padx=10, pady=10)
       
    def update_current_turn_dialog_labels(self, dialog_num, turn_num, json_data, count_turns):
        """Updates the indicator of where the annotator is (in what dialog and what turn).

        Args:
            dialog_num (int): The dialog the annotator is on.
            turn_num (int): The turn the annotator is on.
            json_data (string): The json data.
            count_turns (int): The number of turns in the dialog.
        """
        # Updates the dialog progress label
        self.current_dialog_label.config(text=f"Dialog: {dialog_num + 1}/{len(json_data)}")

        # Updates the turn progress label
        self.current_turn_label.config(text=f"Turn: {turn_num + 1}/{count_turns}")
    
class AnnotatorId():
    def __init__(self, position, root):
        """
        Initializes an instance of the AnnotatorId class.

        Args:
            position (tkinter.Position): The position of the button.
            root (tkinter.Root): The root window.

        Attributes:
            annotator_id (str): The annotator's ID.
            root (tkinter.Root): The root window.
            update_id_button (tkinter.Button): The button used to update the annotator's ID.
        """
        self.annotator_id = ''
        self.root = root
        self.update_id_button = tk.Button(position, text="Update Full Name")
        self.update_id_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def handle_annotatorId(self, json_data):
        """
        Checks if the json_data has an annotator_name inside it. If it doesn't, calls a function to ask the user for a name.

        Args:
            json_data (str): The JSON data being annotated.

        Returns:
            str: The json_data after being updated with an annotator_name.
        """
        first_dialog_id = next(iter(json_data))  # Get the first key in the JSON data
        if 'annotator_name' not in json_data[first_dialog_id] or json_data[first_dialog_id]['annotator_name'] is None or json_data[first_dialog_id]['annotator_name'] == '':
            json_data = self.update_annotator_id_dialog(json_data)
        return json_data
            
    def annotator_id_empty(self, json_data):
        """
        Checks if the annotator_name field in the json data is empty or not.

        Args:
            json_data (str): The JSON data.

        Returns:
            bool: True if the annotator_name field is empty, False otherwise.
        """
        first_dialog_id = next(iter(json_data))  # Get the first key in the JSON data
        if 'annotator_name' not in json_data[first_dialog_id] or json_data[first_dialog_id]['annotator_name'] is None:
            return True
        return False
    
    def update_annotator_id_dialog(self,json_data):
        """
        The dialog that is used to ask the annotator to give their name.

        Args:
            json_data (str): The JSON data, to check if there is already a name and if there is, present it as the entry placeholder.

        Returns:
            str: The json_data after being updated with an annotator name.
        """
        first_dialog_id = next(iter(json_data))  # Get the first key in the JSON data
        current_id = json_data[first_dialog_id].get('annotator_name')  # Get current annotator_id

        new_id = simpledialog.askstring("Input", "Enter annotator's *full* name:", initialvalue=current_id, parent=self.root)
        if new_id is None: 
                self.root.destroy()
                return
        
        def contains_english_letter(s):
            if s is None:
                return False
            return bool(re.search('[a-zA-Z]', s))
        
        if contains_english_letter(new_id):
            self.annotator_id = new_id
            json_data = self.update_annotator_id(json_data)
            return json_data
        
        else:
            json_data = self.update_annotator_id_dialog(json_data)
            return json_data

             
    def update_annotator_id(self, json_data):
        """
        Goes through all the dialogs in the batch and changes their annotator_name field to the annotator's name that was given through the dialog.

        Args:
            json_data (str): The JSON data with the field annotator name to be changed.

        Returns:
            str: The json_data after the field annotator_name has been changed.
        """
        for dialog_id in json_data:
            json_data[dialog_id]['annotator_name'] = self.annotator_id

        return json_data
    
class MongoData():
    def __init__(self, root, connection_string):
        """
        Initializes an instance of the MongoData class.

        Args:
            root (object): The root object of the Tkinter application.
            connection_string (str): The connection string for the MongoDB database.
        """
        self.client = MongoClient(connection_string)
        self.db = self.client.require_rewrite_b
        self.username = None
        self.usercode = None
        self.batch_id_list_index = None
        self.temp_batch_id_list_index = None
        self.count_batches = None
        self.root = root
        self.sign_in()
        self.json_data = self.load_json()
          
    def sign_in(self):
        """
        Asks the user for a special code to be identified by the MongoDB database, so they will send back their current json_file in progress.

        Raises:
            Exception: Raises when the user's current working batch num is not found in the database.
        """
        usercode = simpledialog.askstring("Input", "Please sign in using your code", parent=self.root)
        if usercode is None: 
            self.root.destroy()
            return
        collection = self.db.annotators
        query = {"usercode": usercode}
        result = collection.find_one(query)
        if result != None:
            self.username = result['username']
            self.usercode = usercode
            self.count_batches = len(result['batches_order'])
            try:
                self.batch_id_list_index = result['batches_order'][result['batch_id_list_index']]
            except:
                raise Exception(f"The user batch is {result['batch_id_list_index']}, and it is not in the DB")
            return
        else:
            messagebox.showerror("Error", "username doesn't exist, please try again. (if you dont know your username ask Ori)")
            self.sign_in()

    def get_batch_num(self):
        """
        Returns the current user batch number.

        Returns:
            int: The current batch number.
        """
        if self.temp_batch_id_list_index != None:
            return self.temp_batch_id_list_index
        return self.batch_id_list_index
    
    def is_temp_active(self):
        """
        Checks if a temporary batch is active.

        Returns:
            bool: True if a temporary batch is active, False otherwise.
        """
        if self.temp_batch_id_list_index != None:
            return True
        return False
         
    def increase_annotator_batch_id_list_index(self):
        """
        Called when a user finishes working on a batch and asks MongoDB to increase the user's current batch number by one.

        Returns:
            dict: The response from MongoDB.
        """
        
        if not self.is_temp_active():
            collection = self.db.annotators
            query = {"usercode": self.usercode}
            update = {"$inc": {"batch_id_list_index": 1}}  # Increment batch_id_list_index by 1
            result = collection.update_one(query, update)
            self.batch_id_list_index += 1
            
            if result.matched_count > 0:
                print(f"User {self.username}'s batch_id_list_index increased by 1.")
            else:
                raise Exception("Username doesn't exist.")
            
        else: 
            if self.temp_batch_id_list_index + 1 == self.batch_id_list_index:
                self.temp_batch_id_list_index = None
            
            else:
                self.temp_batch_id_list_index += 1
                
    def decrease_annotator_batch_id_list_index(self):
        """
        Called when a user finishes working on a batch and asks MongoDB to decrease the user's current batch number by one.
        """
        
        if not self.is_temp_active():
            self.temp_batch_id_list_index = self.batch_id_list_index - 1
            
        else: 
            self.temp_batch_id_list_index -= 1
    
    def check_next_batch_exist(self):
        """
        Checks if there is a batch with the number of (current_user_batch_num + 1).

        Returns:
            bool: False if there isn't, True if there is.
        """
        if self.get_batch_num() + 1 > self.count_batches:
            print("No more batches available.")
            return False
        return True
      
    def check_prev_batch_exist(self):
        """
        Checks if there is a batch with the number of (current_user_batch_num - 1) when the user tries to go to their previous batches.

        Returns:
            bool: False if there isn't, True if there is.
        """
        if self.get_batch_num() - 1 < 1:
            print("No previous batches available.")
            return False
        
        return True
    
    def next_batch(self):
        """
        Sets the property of the self.json_data to the next batch.

        Returns:
            bool: True if the operation was successful, False if it wasn't.
        """
        if not self.check_next_batch_exist():
            return False
        
        self.increase_annotator_batch_id_list_index()
        self.json_data = self.load_json()  # Assuming this method loads the next batch of JSON data
        return True

    def prev_batch(self):
        """
        Sets the property of the self.json_data to the previous batch.

        Returns:
            bool: True if the operation was successful, False if it wasn't.
        """
        if not self.check_prev_batch_exist():
            return False
        
        self.decrease_annotator_batch_id_list_index()
        self.json_data = self.load_json()  # Assuming this method loads the next batch of JSON data
        return True

    def load_json(self, test=False):
        """
        Asks the MongoDB for the json_file the user is working on.

        Args:
            test (bool, optional): True when the function is called inside the test_if_annotation_updated_in_mongo. Defaults to False.

        Returns:
            string: The json file as a string.
        """
        data = None
        collection = self.db.json_annotations
        query = { "batch_id": self.get_batch_num(), "username": self.username, "usercode": self.usercode}
        result = collection.find_one(query)
        
        if result != None:
            if test == False:
                print(f"batch_{self.get_batch_num()} loaded successfully")
            data = result['json_string']
                
        else:
            query = {'batch_id': self.batch_id_list_index}
            collection = self.db.json_batches
            result = collection.find_one(query)
            if result == None:
                print('No more batches to annotate')
                return 'done'
            else:
                data = result['json_string']
        
        # Shuffling and storing rewrites
        self.shuffled_rewrites = {}
        self.identical_rewrites = {}
        for dialog_id, dialog_data in data.items():
            
            for turn_id, turn_data in dialog_data.items():
                # Check if turn_id is a digit
                if turn_id.isdigit():

                    # Select keys that contain 'rewrite' and do not contain 'annotator'
                    rewrites = []
                    
                    for key, value in turn_data.items():
                        if isinstance(value, dict) and 'score' in value.keys() and 'optimal' in value.keys():
                            exist = False
                            for rewrite in rewrites:
                                if value['text'] == rewrite[1]['text']:
                                    self.identical_rewrites[(dialog_id, turn_id, rewrite[0])].append(key)
                                    exist = True
                                    
                            if not exist:
                                rewrites.append((key,value))
                                self.identical_rewrites[(dialog_id, turn_id, key)] = []
                            
                    
                    random.shuffle(rewrites)
                    self.shuffled_rewrites[(dialog_id, turn_id)] = rewrites
        return data

    def save_json(self, draft=False):
        """
        Opens a thread and sends the user's progress to the MongoDB.
        """
        
        # Wrap the save_json logic in a method that can be run in a thread
        thread = threading.Thread(target=self.save, args=(draft,))
        thread.start()
        # Optionally, you can join the thread if you need to wait for it to finish
        # thread.join()
                
    def save(self, draft=False):
        """
        Sends the json_file (that is saved in the program memory as a string) back to MongoDB to be saved.
        """
        collection = self.db.json_annotations
        query = {'usercode': self.usercode, 'batch_id': self.get_batch_num()}
        my_values = {"$set": {'username': self.username, 'usercode': self.usercode, 'batch_id': self.get_batch_num(), 'json_string': self.json_data}}
        
        if draft:
            collection = self.db.json_annotations_draft
            query['timestamp'] = datetime.datetime.now()
            my_values["$set"]['timestamp'] = datetime.datetime.now()
            
        update_result = collection.update_one(query, my_values, upsert=True)
        if update_result.matched_count > 0:
            print(f"Document with annotator_id: {self.username} and batch_id: {self.get_batch_num()} updated.")
        elif update_result.upserted_id is not None:
            if draft == False:
                print(f"New document inserted with id {update_result.upserted_id}.")
        else:
            raise Exception("Failed to save the JSON data.")

    def test_if_annotation_updated_in_mongo(self):
        """opens a thread for a function that checks if the annotation the user did was saved inside mongoDB
        """
        thread = threading.Thread(target=self.test_if_annotation_updated_in_mongo_thread)
        thread.start()
    
    def test_if_annotation_updated_in_mongo_thread(self):
        temp_data = self.load_json(test=True)

        collection = self.db.json_annotations

        query = { "batch_id": self.get_batch_num(), "username": self.username, "usercode": self.usercode}
        result = collection.find_one(query)

        if result != None:
            temp_data = result['json_string']
            if temp_data == self.json_data:
                return True
            else:
                return False
            
        return None

    def save_annotation_draft(self):
        self.save_json(draft=True)

class JsonData():
    def __init__(self, root):
        """
        Initializes a JsonData object.

        Args:
            root: The root Tkinter object.

        Attributes:
            filename (str): The path to the target.json file.
            root: The root Tkinter object.
            json_data (dict): The loaded JSON data from target.json.
            shuffled_rewrites (dict): A dictionary to store shuffled rewrites.
            identical_rewrites (dict): A dictionary to store identical rewrites.
        """
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = ''
        
        self.filename = os.path.join(application_path, 'target.json')
        self.root = root
        self.json_data = self.load_json()

    def load_json(self):
        """
        Searches for a file named target.json, reads its contents, and saves it to the json_data property.

        Returns:
            dict: The loaded JSON data.

        Raises:
            FileNotFoundError: If target.json is not found, displays an error message and destroys the root Tkinter object.
        """
        data = None
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            tk.messagebox.showerror("Annotation File Not Found", f"Please place target.json inside the same folder with the program")
            self.root.destroy()

        self.shuffled_rewrites = {}
        self.identical_rewrites = {}
        for dialog_id, dialog_data in data.items():
            for turn_id, turn_data in dialog_data.items():
                if turn_id.isdigit():
                    rewrites = []
                    for key, value in turn_data.items():
                        if isinstance(value, dict) and 'score' in value.keys() and 'optimal' in value.keys():
                            exist = False
                            for rewrite in rewrites:
                                if value['text'] == rewrite[1]['text']:
                                    self.identical_rewrites[(dialog_id, turn_id, rewrite[0])].append(key)
                                    exist = True
                            if not exist:
                                rewrites.append((key,value))
                                self.identical_rewrites[(dialog_id, turn_id, key)] = []
                    random.shuffle(rewrites)
                    self.shuffled_rewrites[(dialog_id, turn_id)] = rewrites
        return data
 
    def save_json(self):
        """
        Export the progress the annotator has made back inside the target.json file.
        """
        with open(self.filename, 'w') as file:
            json.dump(self.json_data, file, indent=4)
            
class LoadingScreen():
    def __init__(self, root):
        """
        Initializes a LoadingScreen object.

        Parameters:
        - root: The root Tkinter window.

        """
        self.root = root
        self.loading_screen = None

    def show_loading_screen(self):
        """
        Displays the loading screen.

        This method creates a new Toplevel window and displays a loading screen
        with a label showing "Loading batch...". The loading screen prevents the
        user from interacting with the main window.

        """
        self.loading_screen = tk.Toplevel(self.root)
        self.loading_screen.title("Loading...")
        self.loading_screen.geometry("200x100")
        self.loading_screen.transient(self.root)
        self.loading_screen.grab_set()

        # Center the loading screen relative to the main window
        self.loading_screen.geometry("+%d+%d" % (
            self.root.winfo_rootx() + (self.root.winfo_width() - 200) // 2,
            self.root.winfo_rooty() + (self.root.winfo_height() - 100) // 2
        ))

        # Make the loading screen appear on top of other windows
        self.loading_screen.attributes("-topmost", True)

        loading_label = tk.Label(self.loading_screen, text="Loading batch...")
        loading_label.pack(pady=20)

        self.root.update()

    def close_loading_screen(self):
        """
        Closes the loading screen.

        This method destroys the loading screen window, allowing the user to
        continue interacting with the main window.

        """
        if self.loading_screen:
            self.loading_screen.destroy()
            self.loading_screen = None
    
class Rewrites():
    """
    Represents a collection of rewrites for a dialog turn.

    Attributes:
    - rewrites (list): The list of rewrites.
    - root (tk.Tk): The root Tkinter window.
    - rewrites_frame_base (tk.Frame): The base frame for rewrites.
    - rewrite_table_grid (tk.Frame): The frame for rewrites annotation entries.
    - no_rewrites_label (tk.Label): The label that appears if there are no rewrites.

    Methods:
    - __init__(self, position, root): Initializes the Rewrites object.
    - get_rewrites(self, json_data, dialog_id, turn_num): Retrieves the rewrites from the given JSON data for a specific dialog and turn.
    - get_rewrite_list(self): Returns the list of rewrites.
    - update_rewrites(self, dialog_id, turn_num, json_data, original_question): Updates the rewrites based on the provided parameters.
    - update_json_data(self, dialog_id, turn_num, json_data): Updates the JSON data with the scores and optimal values for rewrites.
    - get_score_by_rewrite_key(self, rewrite_key): Returns the score for a rewrite with the given key.
    - get_optimal_by_rewrite_key(self, rewrite_key): Returns the optimal value for a rewrite with the given key.
    - get_score_list(self): Returns a list of scores for all rewrites.
    - get_max_score(self): Returns the maximum score among all rewrites.
    - all_scores_filled(self): Checks if all rewrites have a score assigned.
    - clean_optimals(self): Clears the optimal values for all rewrites.
    - is_empty(self): Checks if any rewrite is missing a score or optimal value.
    - sync_optimals(self, score, optimal): Synchronizes the optimal values for rewrites with the given score.
    - optimal_exists(self): Checks if any rewrite has an optimal value of 1.
    - handle_positive_optimal(self, score): Sets the optimal value for rewrites based on the given score.
    """

    def __init__(self, position, root):
        """
        Initializes the Rewrites object.

        Parameters:
        - position (tk.Position): The position object to manage the layout.
        - root (tk.Tk): The root Tkinter window.
        """
        self.rewrites = []
        self.root = root
        self.rewrites_frame_base = tk.Frame(root)
        position.add(self.rewrites_frame_base, stretch="always", height=100)
        LabelSeparator(self.rewrites_frame_base, text="Rewrites").pack(fill=tk.X)

        # inside Frame for rewrites annotation entries
        self.rewrite_table_grid = tk.Frame(self.rewrites_frame_base)
        self.rewrite_table_grid.pack(fill=tk.BOTH, padx=10, pady=10)
        
        text = tk.Label(self.rewrite_table_grid, text="Text")
        score = tk.Label(self.rewrite_table_grid, text="Score")
        optimal = tk.Label(self.rewrite_table_grid, text="Optimal")
        
        # Place the labels in the grid
        text.grid(row=0, column=1, sticky='nsew')
        score.grid(row=0, column=2, sticky='nsew')
        optimal.grid(row=0, column=3, sticky='nsew')

        # Configure the frame columns to expand with the window size
        self.rewrite_table_grid.columnconfigure(0, weight = 1)
        self.rewrite_table_grid.columnconfigure(1, weight = 50)
        self.rewrite_table_grid.columnconfigure(2, weight = 1)
        self.rewrite_table_grid.columnconfigure(3, weight = 1)

        #label that appear if there are no rewrites
        self.no_rewrites_label = tk.Label(self.rewrite_table_grid, text="No rewrites in this turn.")
        self.no_rewrites_label.grid(column=1, row=3)
        self.no_rewrites_label.grid_remove()  # This hides the label initially

    def get_rewrites(self, json_data, dialog_id, turn_num): 
        """
        Retrieves the rewrites from the given JSON data for a specific dialog and turn.

        Parameters:
        - json_data (dict): The JSON data containing the dialog information.
        - dialog_id (str): The ID of the dialog.
        - turn_num (int): The number of the turn.

        Returns:
        - list: The list of rewrites for the specified dialog and turn.
        """
        rewrites = json_data[dialog_id]['annotations'][turn_num]['rewrites']
        return dict(random.sample(list(rewrites.items()), len(rewrites)))

    def get_rewrite_list(self):
            """
            Returns the list of rewrites.

            Returns:
                list: The list of rewrites.
            """
            return self.rewrites
    
    def update_rewrites(self, dialog_id, turn_num, json_data, original_question):
        """
        Update the rewrites based on the provided parameters.

        Args:
            dialog_id (str): The ID of the dialog.
            turn_num (int): The turn number of the dialog.
            json_data (dict): The JSON data containing the rewrites.
            original_question (str): The original question to compare the rewrites against.

        Returns:
            None
        """

        if not self.rewrites == []:
            for rewrite in self.rewrites:
                rewrite.optimal.destroy()
                rewrite.score.destroy()
                rewrite.text.destroy()
                rewrite.rewrite_label.destroy()

        self.rewrites = []
        rewrites = self.get_rewrites(json_data, dialog_id, turn_num)
        self.hidden_rewrites = {}
        used_rewrites = {}
        rewrite_row = 1
        valid_rewrites_len = 0

        for rewrite_key, rewrite_value in rewrites.items():
            identical_to_question = False
            duplicate = False
            
            if compare_norm_texts(rewrite_value['text'], original_question):
                #self.hidden_rewrites[rewrite_key] = {"reason": 'Identical to current question', "duplicate": None}
                identical_to_question = True
             
            
            for rkey, rvalue in used_rewrites.items():
                if compare_norm_texts(rvalue, rewrite_value['text']):
                    self.hidden_rewrites[rewrite_key] = ({"reason": 'Duplicate of another rewrite', "duplicate": rkey})
                    duplicate = True
                    
               
            if duplicate == False:
                used_rewrites.update({rewrite_key: rewrite_value['text']})
                self.rewrites.append(SingleRewrite(rewrite_key, rewrite_value['text'], rewrite_value['optimal'], rewrite_value['score'], rewrite_row, identical_to_question, self))
                
                rewrite_row += 1
                valid_rewrites_len += 1

        if valid_rewrites_len == 0:
            self.no_rewrites_label.grid()  # Show the label

        else:
            self.no_rewrites_label.grid_remove()  # Hide the label

    def update_json_data(self, dialog_id, turn_num, json_data):
        """
        Updates the JSON data with the scores and optimal values for rewrites.

        Args:
            dialog_id (str): The ID of the dialog.
            turn_num (int): The turn number.
            json_data (dict): The JSON data to be updated.

        Returns:
            dict: The updated JSON data.
        """

        def change_score(field, value):
            json_data[dialog_id]['annotations'][turn_num]['rewrites'][rewrite_key][field] = value

        for rewrite in self.rewrites:
            rewrite_key = rewrite.rewrite_key
            score = rewrite.get_score()
            optimal = rewrite.get_optimal()

            change_score('score', score)
            change_score('optimal', optimal)

        for rewrite_key, rewrite_data in self.hidden_rewrites.items():
            if rewrite_data['reason'] == 'Identical to current question':
                json_data[dialog_id]['annotations'][turn_num]['rewrites'][rewrite_key]['score'] = -1
                json_data[dialog_id]['annotations'][turn_num]['rewrites'][rewrite_key]['optimal'] = -1

            elif rewrite_data['reason'] == 'Duplicate of another rewrite':
                json_data[dialog_id]['annotations'][turn_num]['rewrites'][rewrite_key]['score'] = self.get_score_by_rewrite_key(rewrite_data['duplicate'])
                json_data[dialog_id]['annotations'][turn_num]['rewrites'][rewrite_key]['optimal'] = self.get_optimal_by_rewrite_key(rewrite_data['duplicate'])

        return json_data
    
    def get_score_by_rewrite_key(self, rewrite_key):
        """
        Retrieves the score associated with a given rewrite key.

        Parameters:
        - rewrite_key (str): The rewrite key to search for.

        Returns:
        - int or None: The score of the rewrite if found, None otherwise.
        """
        for rewrite in self.rewrites:
            if rewrite.rewrite_key == rewrite_key:
                return rewrite.get_score()
        return None
    
    def get_optimal_by_rewrite_key(self, rewrite_key): 
        """
        Returns the optimal value for a given rewrite key.

        Parameters:
        - rewrite_key (str): The key to search for in the list of rewrites.

        Returns:
        - The optimal value for the given rewrite key, or None if the key is not found.
        """
        for rewrite in self.rewrites:
            if rewrite.rewrite_key == rewrite_key:
                return rewrite.get_optimal()
        return None
    
    def get_score_list(self):
        """
        Returns a list of scores from the rewrites.

        Returns:
            list: A list of scores from the rewrites.
        """
        score_list = []
        for rewrite in self.rewrites:
            score_list.append(rewrite.score)
        return score_list
    
    def get_max_score(self):
        """
        Returns the maximum score among all the rewrites.

        Returns:
            int: The maximum score. Returns None if any rewrite has a score of None.
        """
        max_score = 0
        for rewrite in self.rewrites:
            if rewrite.get_score() is None:
                return None
            if rewrite.get_score() > max_score:
                max_score = rewrite.get_score()
        return max_score
    
    def all_scores_filled(self):
        """
        Checks if all scores for the rewrites have been filled.

        Returns:
            bool: True if all scores are filled, False otherwise.
        """
        for rewrite in self.rewrites:
            if rewrite.get_score() == None:
                return False
        return True
    
    def clean_optimals(self):
        """
        Clears the optimal values in the rewrites.

        This method iterates through each rewrite in the `rewrites` list and clears the optimal value by deleting the existing text and inserting an empty string.

        Parameters:
            None

        Returns:
            None
        """
        for rewrite in self.rewrites:
            rewrite.optimal.delete(0, tk.END)
            rewrite.optimal.insert(0, '')
            
    def is_empty(self):
        """
        Checks if any rewrite in the list has a score or optimal value of None.

        Returns:
            bool: True if any rewrite has a score or optimal value of None, False otherwise.
        """
        for rewrite in self.rewrites:
            if rewrite.get_score() is None or rewrite.get_optimal() is None:
                return True
        return False
    
    def sync_optimals(self, score, optimal):
        """
        Synchronizes the optimal value for rewrites with a given score.

        Parameters:
        - score: The score to match against the rewrites' scores.
        - optimal: The new optimal value to set for the matching rewrites.

        Returns:
        None
        """
        for rewrite in self.rewrites:
            if rewrite.get_score() == score:
                rewrite.set_optimal(optimal)
                rewrite.optimal.delete(0, tk.END)
                if optimal == None:
                    optimal = ''
                rewrite.optimal.insert(0, optimal)
                
    def optimal_exists(self):
        """
        Checks if an optimal rewrite exists in the list of rewrites.

        Returns:
            bool: True if an optimal rewrite exists, False otherwise.
        """
        for rewrite in self.rewrites:
            if rewrite.get_optimal() == 1:
                return True
        return False
    
    def handle_positive_optimal(self, score):
        """
        Sets the 'optimal' flag for rewrites with a score greater than or equal to the given score.

        Parameters:
        - score: The threshold score to compare against.

        Returns:
        None
        """
        for rewrite in self.rewrites:
            if rewrite.get_score() >= score:
                rewrite.set_optimal(1)
            else:
                rewrite.set_optimal(0)
    
class SingleRewrite():
    """
    Represents a single rewrite instance.

    Attributes:
        rewrite_key (str): The key associated with the rewrite.
        rewrite_text (str): The text content of the rewrite.
        rewrite_optimal (int or None): The optimal value for the rewrite.
        rewrite_score (int or None): The score value for the rewrite.
        rewrite_row (int): The row number of the rewrite in the rewrite table.
        identical_to_question (bool): Indicates if the rewrite is identical to the original question.
        rewrites_instance (Rewrites): The instance of the parent rewrites class.

    Methods:
        __init__(self, rewrite_key, rewrite_text, rewrite_optimal, rewrite_score, rewrite_row, identical_to_question, rewrites_instance)
        score_input_handle(self)
        optimal_input_handle(self)
        select_text(self, event=None)
        get_text(self)
        get_score(self)
        set_score(self, score)
        get_optimal(self)
        set_optimal(self, optimal)
    """
    def __init__(self, rewrite_key, rewrite_text, rewrite_optimal, rewrite_score, rewrite_row, identical_to_question, rewrites_instance):
        """
        Initializes a SingleRewrite instance.

        Parameters:
            rewrite_key (str): The key associated with the rewrite.
            rewrite_text (str): The text content of the rewrite.
            rewrite_optimal (int or None): The optimal value for the rewrite.
            rewrite_score (int or None): The score value for the rewrite.
            rewrite_row (int): The row number of the rewrite in the rewrite table.
            identical_to_question (bool): Indicates if the rewrite is identical to the original question.
            rewrites_instance (Rewrites): The instance of the parent rewrites class.
        """
        self.rewrite_key = rewrite_key
        self.rewrite_text = rewrite_text
        
        rewrite_grid = rewrites_instance.rewrite_table_grid
        
        self.rewrite_instance = rewrites_instance


        self.rewrite_label = tk.Label(rewrite_grid, text=f"Rewrite {rewrite_row}")
        self.rewrite_label.grid(column=0, row=rewrite_row)

        self.text = tk.Text(rewrite_grid, height=1, wrap='none')
        self.score = tk.Entry(rewrite_grid, width=5, text=None)
        self.optimal = tk.Entry(rewrite_grid, width=5, text=None)

        self.text.insert(tk.END, rewrite_text)
        self.text.config(state='disabled')
        self.identical_to_question = identical_to_question


        self.score.insert(tk.END, rewrite_score if rewrite_score is not None else '')
        self.optimal.insert(tk.END, rewrite_optimal if rewrite_optimal is not None else '')
        
        self.text.grid(row=rewrite_row, column=1, sticky='we', padx=5, pady=5)
        self.score.grid(row=rewrite_row, column=2, sticky='we', padx=5, pady=5)
        self.optimal.grid(row=rewrite_row, column=3, sticky='we', padx=5, pady=5)

        self.optimal.bind("<KeyRelease>", lambda event: self.optimal_input_handle())
        self.score.bind("<KeyRelease>",  lambda event: self.score_input_handle())

        self.score.bind("<FocusIn>", self.select_text)
        self.optimal.bind("<FocusIn>", self.select_text)

    def score_input_handle(self):
        """
        Handles the input score and performs necessary actions based on the input.

        Returns:
            bool: True if the input score is valid, False otherwise.
        """
        new_score = self.get_score()
        self.rewrite_instance.clean_optimals()
        
        if new_score == '' or new_score == None:
            self.set_score(None)
            return True
        
        elif new_score in [1,2,3,4,5,6,7,8,9]:
            return True      

        else:
            tk.messagebox.showwarning("Invalid Input", f"Allowed values are: 1-9")
            self.set_score(None)
            return False
        
    def optimal_input_handle(self):
        """
        Handles the input for the optimal value.
        
        Retrieves the text from an Entry widget and performs validation checks.
        If the input is valid, it updates the optimal value and returns True.
        If the input is invalid, it displays a warning message and returns False.
        
        Returns:
            bool: True if the input is valid and processed successfully, False otherwise.
        """
        # Retrieve text from an Entry widget
        new_optimal = self.get_optimal()
        
        if new_optimal == '' or new_optimal == None:
            self.set_optimal(None)
            return True
        
        if not self.rewrite_instance.all_scores_filled():
            tk.messagebox.showwarning("Invalid Input", f"Please fill in all scores first.")
            self.set_optimal(None)
            return False
        
        if new_optimal == 1:

            if True or (self.rewrite_instance.get_max_score() == self.get_score()):
                self.rewrite_instance.sync_optimals(self.get_score(), new_optimal)
                self.rewrite_instance.handle_positive_optimal(self.get_score())
                return True
            
            else:
                tk.messagebox.showwarning("Invalid Input", f"Score is not the highest.")
                self.set_optimal(None)
                return False

        elif new_optimal == 0:
            self.rewrite_instance.sync_optimals(self.get_score(), new_optimal)
            return True

        else:
            self.set_optimal(None)
            tk.messagebox.showwarning("Invalid Input", f"Allowed values are: 0 or 1")
            return False
        
    def select_text(self, event=None):
        """
        Selects all the text in the widget.

        Parameters:
        - event: The event that triggered the method (optional).

        Returns:
        None
        """
        event.widget.select_range(0, tk.END)

        
    def get_text(self):
        """
        Retrieve the text from the text widget and return it as a string.

        Returns:
            str: The text content of the text widget.
        """
        return self.text.get(1.0, tk.END).strip()

    def get_score(self):
        """
        Retrieves the score from the input field.

        Returns:
            int or str or None: The score value entered by the user. If the score is a valid integer, it is returned as an int.
            If the score is a non-empty string, it is returned as a str. If the score is None or an empty string, None is returned.
        """
        score = self.score.get()
        if score.isdigit():
            return int(score)
        elif score != None and score != '':
            return score
        else:
            return None
    
    def set_score(self, score):
        """
        Sets the score value in the input field.

        Parameters:
            score (int or str or None): The score value to be set. If the score is None, an empty string is set.

        Returns:
            None
        """
        if score == None:
            score = ''
        self.score.delete(0, tk.END)
        self.score.insert(0, score)
        
    def get_optimal(self):
        """
        Retrieves the optimal value from the input field.

        Returns:
            int or str or None: The optimal value entered by the user. If the optimal value is a valid integer, it is returned as an int.
            If the optimal value is a non-empty string, it is returned as a str. If the optimal value is None or an empty string, None is returned.
        """
        optimal = self.optimal.get()
        if optimal.isdigit():
            return int(optimal)
        elif optimal != None and optimal != '':
            return optimal
        else:
            return None

    def set_optimal(self, optimal):
        """
        Sets the optimal value in the input field.

        Parameters:
            optimal (int or str or None): The optimal value to be set. If the optimal value is None, an empty string is set.

        Returns:
            None
        """
        if optimal == None:
            optimal = ''
        self.optimal.delete(0, tk.END)
        self.optimal.insert(0, optimal)
            
class AnnotatorRewrite():
    """
    A class representing the Annotator Rewrite component.

    Attributes:
    - position: The position object to add the Annotator Rewrite frame to.
    - root: The root Tkinter window.
    """

    def __init__(self, position, root):
        """
        Initializes the AnnotatorRewrite object.

        Parameters:
        - position: The position object to add the Annotator Rewrite frame to.
        - root: The root Tkinter window.
        """
        self.annotator_rewrite_frame_base = tk.Frame(root)
        position.add(self.annotator_rewrite_frame_base, stretch="always", height=30)
        LabelSeparator(self.annotator_rewrite_frame_base, text="Annotator Rewrite").pack(fill=tk.X)
        
        self.annotator_rewrite_frame_grid = tk.Frame(self.annotator_rewrite_frame_base)
        self.annotator_rewrite_frame_grid.pack(fill=tk.X, padx=10, pady=10)
        
        self.annotator_rewrite_label = tk.Label(self.annotator_rewrite_frame_grid, text="Annotator Rewrite:")
        self.annotator_rewrite_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.annotator_rewrite_entry = tk.Entry(self.annotator_rewrite_frame_grid)
        self.annotator_rewrite_entry.grid(row=1, column=1, sticky='wne', padx=5, pady=5)

        self.annotator_rewrite_frame_grid.columnconfigure(0, weight=10)
        self.annotator_rewrite_frame_grid.columnconfigure(1, weight=1000)
        self.annotator_rewrite_entry.bind("<FocusIn>", self.select_text)
    
    def get_annotator_rewrite(self):
        """
        Returns the text entered in the Annotator Rewrite entry field.

        Returns:
        - The text entered in the Annotator Rewrite entry field.
        """
        text = self.annotator_rewrite_entry.get()
        
        if text == '':
            return None
        
        else:
            return self.annotator_rewrite_entry.get()
    
    def set_annotator_rewrite(self, text):
        """
        Sets the text in the Annotator Rewrite entry field.

        Parameters:
        - text: The text to set in the Annotator Rewrite entry field.
        """
        if text == None:
            text = ''
            
        self.annotator_rewrite_entry.delete(0, tk.END)
        self.annotator_rewrite_entry.insert(0, text)
    
    def is_empty(self):
        """
        Checks if the Annotator Rewrite entry field is empty.

        Returns:
        - True if the Annotator Rewrite entry field is empty, False otherwise.
        """
        def contains_english_char(s):
            return any(c.isalpha() and c.isascii() for c in s)

        text = self.get_annotator_rewrite()
        
        if text == None:
            return True
        
        elif contains_english_char(text):
            return False
        
        else:
            return True
          
    def select_text(self, event=None):
        """
        Selects all the text in the Annotator Rewrite entry field.

        Parameters:
        - event: The event that triggered the text selection (default: None).
        """
        event.widget.select_range(0, tk.END)
        
    def update_json_data(self, dialog_id, turn_num, json_data):
        """
        Updates the JSON data with the new Annotator Rewrite value.

        Parameters:
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.
        - json_data: The JSON data to update.

        Returns:
        - The updated JSON data.
        """
        new_value = self.get_annotator_rewrite()
            
        json_data[dialog_id]['annotations'][turn_num]['annotator_rewrite'] = new_value
        return json_data
     
    def update(self, dialog_id, turn_num, json_data):
        """
        Updates the Annotator Rewrite entry field with the value from the JSON data.

        Parameters:
        - dialog_id: The ID of the dialog.
        - turn_num: The turn number.
        - json_data: The JSON data.

        """
        annotator_rewrite = ''
        if 'annotator_rewrite' in json_data[dialog_id]['annotations'][turn_num]:
            value = json_data[dialog_id]['annotations'][turn_num]['annotator_rewrite']
            if value is not None:
                annotator_rewrite = value

        self.set_annotator_rewrite(annotator_rewrite)

    def bindIsUnique(self, get_rewrites, get_original_question):
        """
        Binds the handle_unique method to the FocusOut event of the Annotator Rewrite entry field.

        Parameters:
        - get_rewrites: A function to get the list of rewrites.
        - get_original_question: A function to get the original question.

        """
        self.annotator_rewrite_entry.bind("<FocusOut>", lambda event: self.handle_unique(get_rewrites(), get_original_question()))
    
    def handle_unique(self, rewrites, original_question):
        """
        Handles the uniqueness check for the Annotator Rewrite.

        Parameters:
        - rewrites: The list of rewrites.
        - original_question: The original question.

        Returns:
        - True if the Annotator Rewrite is unique, False otherwise.
        """
        if self.is_empty():
            return True
        
        for rewrite in rewrites:
            if compare_norm_texts(rewrite.get_text(), self.get_annotator_rewrite()):
                self.set_annotator_rewrite(None)
                tk.messagebox.showwarning("Annotator Rewrite Identical", f"Annotator Rewrite is identical to a rewrite.")
                return False
            
        if (compare_norm_texts(self.get_annotator_rewrite(), original_question)):
            self.set_annotator_rewrite(None)
            tk.messagebox.showwarning("Annotator Rewrite Identical", f"Annotator Rewrite is identical to the original question.")
            return False
        
        return True
    
class JsonViewerApp:

    def __init__(self, root, ):
        
        # Main windows settings
        self.root = root
        self.root.title("OneAI ReWrite Annotation Software")  

        # Set the minimum size of the window
        root.minsize(1000, 900)
        self.root.update()
        self.fields_check = True
        self.disable_copy = True
        self.online = True
        
                                          
        # Create a Top Panel Frame for options
        top_panel_frame = tk.Frame(root)
        top_panel_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Create Main PanedWindow
        main_pane = tk.PanedWindow(root, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True)
      
        # "<" (Previous) and ">" (Next) buttons next to each other
        prev_button = tk.Button(top_panel_frame, text="<", command=self.prev_turn)
        prev_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        next_button = tk.Button(top_panel_frame, text=">", command=self.next_turn)
        next_button.pack(side=tk.LEFT)
        
        # "<<" (Previous Dialog) and ">>" (Next Dialog) buttons
        prev_dialog_button = tk.Button(top_panel_frame, text="<<", command=self.prev_dialog)
        prev_dialog_button.pack(side=tk.LEFT, padx=(10, 0), pady=10)

        next_dialog_button = tk.Button(top_panel_frame, text=">>", command=self.next_dialog)
        next_dialog_button.pack(side=tk.LEFT)
        


        # Disable Copy Paste 
        if self.disable_copy == True:
            root.event_delete('<<Paste>>', '<Control-v>')
            root.event_delete('<<Copy>>', '<Control-c>')
        
        # Save Button at the bottom
        self.save_button = tk.Button(root, text="Save and Next", command=self.next_turn)
        self.save_button.pack(side=tk.BOTTOM, pady=10)
        self.root.bind("<Return>", self.next_turn)


        #Init all the items in the program
        self.data = None
        if self.online == False: 
            self.data = JsonData(self.root)
            
        else:
            connection_string = "mongodb+srv://orik:Ori121322@cluster0.tyiy3mk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            self.data = MongoData(self.root, connection_string)

        self.progress = ProgressIndicator(top_panel_frame)
        self.dialog_frame = DialogFrame(main_pane, root)
        self.font = FontSizeChanger(top_panel_frame, root)
        self.require_rewrite = RequireRewrite(main_pane, root)
        self.annotator_id = AnnotatorId(top_panel_frame, root)
        self.loading_screen = LoadingScreen(root)
        self.rewrites = Rewrites(main_pane, root)
        self.annotator_rewrite = AnnotatorRewrite(main_pane, root)
        self.annotator_id.update_id_button.config(command=lambda: self.annotator_id.update_annotator_id_dialog(self.data.json_data))
        self.annotator_rewrite.bindIsUnique(self.rewrites.get_rewrite_list, self.get_original_question)

        

        # Load JSON and display data
        self.current_dialog_num = 0
        self.current_turn_num = 0

        self.focus_list = []
        self.focus_index = 0
        self.first_focus_action = None

        if(self.data.json_data == None or self.data.json_data == ''):
            raise Exception(f"The json files is Null.\n JSON={self.data.json_data}")
      
        self.data.json_data = self.annotator_id.handle_annotatorId(self.data.json_data)
        
        
        # After loading JSON data, find the first turn with an empty score
        self.find_next_unscored_turn()
        self.init_turn()
        
        self.font.increase_font_size()
        self.focused_element = None

    def find_next_unscored_turn(self):
        """ goes through the json_file and finds the next turn which is not filled already, then sets the program to show the turn"""
        for dialog_index, dialog_id in enumerate(self.data.json_data):
            annotations = self.data.json_data[dialog_id]['annotations']
            for turn_id in range(len(annotations)):

                turn_data = annotations[turn_id]['requires_rewrite']
                if (turn_data == None):
                    self.current_dialog_num = dialog_index
                    self.current_turn_num = turn_id
                    return
                
        self.current_dialog_num = self.count_dialogs_in_batch()-1
        self.current_turn_num = self.count_turns_in_dialog()-1
    
    def are_all_fields_filled(self):
        """check if the turn the annotator is currently on is saved comletly, used before moving to the next turn

        Returns:
            boolean: True if everything is filled, False if not.
        """
        missing_fields = []

        # Check if annotator_id is filled
        first_dialog_id = next(iter(self.data.json_data))  
        if not self.data.json_data[first_dialog_id].get('annotator_name'):
            if (not self.annotator_id.annotator_id_empty(self.data.json_data)):
                self.data.json_data = self.annotator_id.update_annotator_id(self.data.json_data)
            else:
                missing_fields.append("Annotator-Name")
        
        if self.require_rewrite.is_empty():
            missing_fields.append('Requires-Rewrite')
            
        if self.rewrites.is_empty():
            missing_fields.append('Rewrites-Fields')
            
       
        
        if self.annotator_rewrite.is_empty():
            
            if (self.require_rewrite.is_empty()):
                missing_fields.append('Annotator-Rewrite')
                
            elif (self.require_rewrite.requires_rewrite_positive()):
                
                if (self.rewrites.is_empty()):
                    missing_fields.append('Annotator-Rewrite')
                    
                elif (self.rewrites.optimal_exists()):
                    pass
                
                else:
                    missing_fields.append('Annotator-Rewrite')
                
        if missing_fields and self.fields_check:
            tk.messagebox.showwarning("Warning", "The following fields are missing: " + ", ".join(missing_fields) + ". Please fill them in before proceeding.")
            return False
        
        return True
    
    def update_json(self, prev=False):
        """updates the json_file inside the Data class (MongoDB or JsonHandler), to be saved later

        Raises:
            MemoryError: Raises when using online mode, and the annotation was not saved correctly in MongoDB

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        self.data.json_data = self.require_rewrite.update_json_data(self.get_dialog_id(), self.current_turn_num, self.data.json_data)
        self.data.json_data = self.rewrites.update_json_data(self.get_dialog_id(), self.current_turn_num, self.data.json_data)
        self.data.json_data = self.annotator_rewrite.update_json_data(self.get_dialog_id(), self.current_turn_num, self.data.json_data)
        
        # Save current state and move to next if all fields are filled
        self.data.save_json()

        if self.online == True:
            self.data.save_annotation_draft()
            if self.data.test_if_annotation_updated_in_mongo() == False:
                raise MemoryError("Online data doesn't match local data, please contact Ori")
            
        return True
        
    def get_dialog_id(self):
        """simply gets the string of the dialog_id using the current num of the dialog in the batch file

        Returns:
            string: the dialog_id
        """
        return list(self.data.json_data.keys())[self.current_dialog_num]

    def init_turn(self):
        """This is an important function which initilaises and update the GUI each turn
        """
        self.progress.update_current_turn_dialog_labels(self.current_dialog_num, self.current_turn_num, self.data.json_data, len(self.data.json_data[self.get_dialog_id()]['annotations']))
        self.dialog_frame.display_dialog(self.get_dialog_id(), self.current_turn_num, self.data.json_data)
        self.require_rewrite.update_entry_text(self.get_dialog_id(), self.current_turn_num, self.data.json_data)  
        self.rewrites.update_rewrites(self.get_dialog_id(), self.current_turn_num, self.data.json_data, self.get_original_question())
        self.annotator_rewrite.update(self.get_dialog_id(), self.current_turn_num, self.data.json_data)
        self.font.update_font_size_wrapper()
        self.require_rewrite.requires_rewrite_entry.focus()
        progress_string = f"Turn={self.current_turn_num+1} | Dialog={self.current_dialog_num+1}"
        if self.online == True: progress_string += f" | Batch={self.data.get_batch_num()}"
        print(progress_string)             

    def get_original_question(self):
            """
            Retrieves the original question from the dialog data based on the current turn number.

            Returns:
                str: The original question from the dialog data.
            """
            for dialog_turn_data in self.data.json_data[self.get_dialog_id()]['dialog']:
                real_turn_num = self.data.json_data[self.get_dialog_id()]['annotations'][self.current_turn_num]['turn_num']
                if dialog_turn_data["turn_num"] == real_turn_num:
                    return dialog_turn_data["original_question"]
        
    def count_turns_in_dialog(self):
        """count the number of turn in the dialog

        Returns:
            int: number of turns in dialog
        """
        return len(self.data.json_data[self.get_dialog_id()]['annotations'])
    
    def count_dialogs_in_batch(self):
        """count the number of dialogs in the batch file

        Returns:
            int: number of dialogs in batch
        """
        return len(self.data.json_data)
     
    def prev_turn(self):
        """goes to the previous turn in the dialog
            if there are no more turns, go to the prev dialog,
            if there are no more dialogs and using mongo, goes to prev batch (if offline need to manually change target.json)

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        
        if not self.update_json(prev=True):
            return False
        
        if self.current_turn_num > 0:
            self.current_turn_num -= 1
            
        elif self.current_dialog_num > 0:
            self.current_dialog_num -= 1
            self.current_turn_num = self.count_turns_in_dialog() - 1
            
        elif self.online == True:
            if not self.prev_batch():
                return False
        
        self.init_turn()
        
        return True
    
    def next_turn(self, event = None):
        """goes to the previous turn in the dialog
            if there are no more turns, go to the next dialog,
            if there are no more dialogs and using mongo, goes to next batch (if offline need to manually change target.json)

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        if not self.handle_require_rewrite_negative_with_identical_rewrite():
            return False

        if not self.are_all_fields_filled():
            return False
        
        elif not self.update_json():
            return False
        
        if self.current_turn_num < self.count_turns_in_dialog() - 1:
            self.current_turn_num += 1
            
        elif self.current_dialog_num < self.count_dialogs_in_batch() - 1:
            self.current_dialog_num += 1
            self.current_turn_num = 0
            
        elif self.online == True:
            if not self.next_batch():
                tk.messagebox.showinfo(title='Finished Annotating!', message='No More Annotations', icon='info')
                return False
            
            else:
                self.data.json_data = self.annotator_id.update_annotator_id(self.data.json_data) #update annotator name
                self.current_dialog_num = 0
                self.current_turn_num = 0
              
        self.init_turn()
        
        return True

    def prev_dialog(self):
        """used in the prev dialog button to go to prev dialog
        """
       
        if self.current_dialog_num > 0:
                if not self.require_rewrite.is_empty():
                        self.update_json()
                self.current_dialog_num -= 1
                self.current_turn_num = self.count_turns_in_dialog()-1
                self.init_turn()
                self.font.update_font_size_wrapper()

        elif (self.online == True and self.data.check_prev_batch_exist()):
                if not self.require_rewrite.is_empty():
                            self.update_json()

                self.prev_batch()
                
                self.init_turn()
        else:
            tk.messagebox.showwarning("Warning", "This is the first dialog")

    def next_dialog(self):
        """used in the next dialog button to go to prev dialog
        """
       
        if self.current_dialog_num < len(self.data.json_data) - 1:
            if self.fields_check:
                if self.are_all_turns_filled():
                    if not self.require_rewrite.is_empty():
                        self.update_json()
                    self.current_dialog_num += 1
                    self.current_turn_num = 0
                    self.init_turn()
                    
                else:
                    tk.messagebox.showwarning("Warning", "Not all turns in this dialog are filled")
            else:
                self.update_json()
                self.current_dialog_num += 1
                self.current_turn_num = 0
                self.init_turn()
                

        elif (self.online == True and self.data.check_next_batch_exist()):
            if self.fields_check:
                if self.are_all_turns_filled():
                    if not self.require_rewrite.is_empty():
                        self.update_json()

                    self.next_batch()
   
                    self.init_turn()
                    
        else:
            tk.messagebox.showinfo(title='Finished Annotating!', message='No More Annotations', icon='info')
                    
    def next_batch(self):
        """in online mode, goes to the next batch

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        if self.online == False and not self.data.check_next_batch_exist():
            return False
        
        self.loading_screen.show_loading_screen()

        if not self.data.next_batch():
            self.loading_screen.close_loading_screen()
            return False
        
        self.data.json_data = self.annotator_id.update_annotator_id(self.data.json_data)
        self.current_dialog_num = 0
        self.current_turn_num = 0

        self.loading_screen.close_loading_screen()
        return True
    
    def prev_batch(self):
        """in online mode, goes to the prev batch

        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        if self.online == False and not self.data.check_prev_batch_exist():
            return False
        
        self.loading_screen.show_loading_screen()
        
        if not self.data.prev_batch():
            self.loading_screen.close_loading_screen()
            return False
        

        self.current_dialog_num = self.count_dialogs_in_batch() - 1
        self.current_turn_num = self.count_turns_in_dialog() - 1
        self.loading_screen.close_loading_screen()
        return True
                                    
    def are_all_turns_filled(self):
        """when going to the next dialog using the button, checks if all the turns in the dialog are filled


        Returns:
            boolean: Return True if opertion was successful, False if not
        """
        dialog_data = self.data.json_data[self.get_dialog_id()]
        for turn in dialog_data['annotations']:
            if turn['requires_rewrite'] == None: return False
        return True
    
    def handle_require_rewrite_negative_with_identical_rewrite(self):
        """
        Checks if the require_rewrite flag is set to 0 and if any rewrites are marked as non-optimal
        and identical to the original question. If so, it displays a warning message
        and returns False. Otherwise, it returns True.

        Returns:
            bool: True if the conditions are met, False otherwise.
        """
        if self.require_rewrite.get_requires_rewrite() == 1:
            return True
        
        rewrites = self.rewrites.get_rewrite_list()
        for rewrite in rewrites:
            if rewrite.identical_to_question == True and rewrite.get_optimal() == 0:
                self.rewrites.clean_optimals()
                tk.messagebox.showwarning("Invalid Input", f"When RequireRewrite is 0, rewrites identical to the original question cannot be marked as non-optimal.")
                return False
            
        return True
        
       
def main():
    online = True
    if online == False:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)

        else:
            application_path = ''

        target_path = os.path.join(application_path, 'target.json')

        # Check if the file exists
        if not os.path.isfile(target_path):
            tk.messagebox.showerror("Annotation File Not Found", "Please place target.json inside the same folder with the program")

            return


    root = tk.Tk()
    app = JsonViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    """
    try:
        main()
    except Exception:
        with open("error_log.txt", "w") as f:
            traceback.print_exc(file=f)"""

# %%



