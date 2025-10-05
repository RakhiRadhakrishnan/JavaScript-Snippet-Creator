import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyperclip  # Used for the copy-to-clipboard feature
import datetime  # For timestamp generation

# --- JavaScript Generation Functions ---

def generate_select_element(selector_type, selector_value):
    """Generates JS code to select an element."""
    if not selector_value:
        return "// Error: Selector value cannot be empty."
    if selector_type == "ID":
        return f"const element = document.getElementById('{selector_value}');"
    elif selector_type == "Class Name (First)":
        # Selects the first element with the class
        return f"const element = document.querySelector('.{selector_value}');"
    elif selector_type == "Tag Name (First)":
        # Selects the first element with the tag name
        return f"const element = document.querySelector('{selector_value}');"
    else:
        return "// Error: Invalid selector type."

def generate_event_listener(element_id, event_type, function_body=""):
    """Generates JS code for an event listener."""
    if not element_id or not event_type:
        return "// Error: Element ID and Event Type are required."

    # Basic indentation for the function body placeholder
    indented_body = "\n    // Your code here...\n"
    if function_body.strip():
         indented_body = "\n" + "\n".join(["    " + line for line in function_body.splitlines()]) + "\n"

    return f"""
const element_{element_id} = document.getElementById('{element_id}');

if (element_{element_id}) {{
  element_{element_id}.addEventListener('{event_type}', function(event) {{
    // 'event' object contains information about the event
    console.log('{event_type} triggered on element with ID: {element_id}');{indented_body}
  }});
}} else {{
  console.error('Element with ID "{element_id}" not found.');
}}
"""

def generate_change_content(element_id, content_type, new_content):
    """Generates JS code to change element content."""
    if not element_id:
        return "// Error: Element ID is required."
    prop = 'textContent' if content_type == 'Text Content' else 'innerHTML'
    # Escape backticks and backslashes in the content for template literals
    escaped_content = new_content.replace('\\', '\\\\').replace('`', '\\`')
    return f"""
const element_{element_id}_content = document.getElementById('{element_id}');

if (element_{element_id}_content) {{
  element_{element_id}_content.{prop} = `{escaped_content}`;
}} else {{
  console.error('Element with ID "{element_id}" not found for changing content.');
}}
"""

def generate_change_style(element_id, style_prop, style_value):
    """Generates JS code to change element style."""
    if not element_id or not style_prop or not style_value:
        return "// Error: Element ID, Style Property, and Style Value are required."
    # Convert CSS property from dash-case to camelCase if needed
    if '-' in style_prop:
        js_style_prop = ''.join(word.capitalize() for word in style_prop.split('-'))
        js_style_prop = js_style_prop[0].lower() + js_style_prop[1:]
    else:
        js_style_prop = style_prop
    return f"""
const element_{element_id}_style = document.getElementById('{element_id}');

if (element_{element_id}_style) {{
  element_{element_id}_style.style.{js_style_prop} = '{style_value}';
}} else {{
  console.error('Element with ID "{element_id}" not found for changing style.');
}}
"""

def generate_function_definition(func_name, params_str, function_body=""):
    """Generates a basic JS function definition."""
    if not func_name:
        return "// Error: Function Name is required."
    # Basic validation for function name
    if not func_name.isidentifier() or func_name in ['function', 'var', 'let', 'const']:
         return f"// Error: '{func_name}' is not a valid JavaScript function name."

    # Basic indentation for the function body placeholder
    indented_body = "\n  // Your function logic here...\n"
    if function_body.strip():
         indented_body = "\n" + "\n".join(["  " + line for line in function_body.splitlines()]) + "\n"

    return f"""
function {func_name}({params_str}) {{
  console.log('Function {func_name} called with parameters: ' + Array.from(arguments).join(', '));{indented_body}
  // return result; // Optional return statement
}}

// Example usage (optional):
// {func_name}(/* provide arguments here */);
"""

# --- GUI Application Class ---

class JsGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("JavaScript Snippet Generator")
        master.geometry("650x600")  # Adjusted size

        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')  # Use a theme that looks better on Windows
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10))
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        style.configure("TCombobox", padding=5, font=('Helvetica', 10))

        # --- Top Frame: Task Selection ---
        self.top_frame = ttk.Frame(master, padding="10")
        self.top_frame.pack(fill=tk.X)

        self.task_label = ttk.Label(self.top_frame, text="Select JavaScript Task:")
        self.task_label.pack(side=tk.LEFT, padx=(0, 10))

        self.task_options = [
            "Select Element",
            "Add Event Listener",
            "Change Element Content",
            "Change Element Style",
            "Define Basic Function"
        ]
        self.selected_task = tk.StringVar()
        self.task_combobox = ttk.Combobox(self.top_frame, textvariable=self.selected_task,
                                          values=self.task_options, state="readonly", width=30)
        self.task_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.task_combobox.current(0)  # Default selection
        self.task_combobox.bind("<<ComboboxSelected>>", self.update_input_fields)

        # --- Middle Frame: Dynamic Inputs ---
        self.input_frame = ttk.Frame(master, padding="10")
        self.input_frame.pack(fill=tk.BOTH, expand=True)
        self.input_widgets = {}  # To keep track of dynamic widgets

        # --- Bottom Frame: Output and Actions ---
        self.bottom_frame = ttk.Frame(master, padding="10")
        self.bottom_frame.pack(fill=tk.X)

        self.generate_button = ttk.Button(self.bottom_frame, text="Generate Code", command=self.generate_code)
        self.generate_button.pack(side=tk.LEFT, padx=(0, 10))

        self.copy_button = ttk.Button(self.bottom_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.LEFT)

        # --- Output Text Area ---
        self.output_label = ttk.Label(master, text="Generated JavaScript:", padding=(10, 5, 10, 0))
        self.output_label.pack(fill=tk.X)

        self.output_text = scrolledtext.ScrolledText(master, height=15, width=70, wrap=tk.WORD,
                                                     font=("Courier New", 10), relief=tk.SUNKEN, borderwidth=1)
        self.output_text.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)
        self.output_text.insert(tk.END, "// Select a task and provide inputs to generate JavaScript code.")
        self.output_text.configure(state='disabled')  # Make read-only initially

        # Initial setup
        self.update_input_fields()  # Populate inputs for the default task

    def clear_input_frame(self):
        """Removes all widgets from the input frame."""
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.input_widgets = {}

    def add_input_field(self, label_text, key, widget_type='entry', options=None, text_height=3):
        """Adds a labeled input field to the input frame."""
        frame = ttk.Frame(self.input_frame)
        frame.pack(fill=tk.X, pady=2)

        label = ttk.Label(frame, text=label_text, width=18, anchor="w")
        label.pack(side=tk.LEFT, padx=(0, 5))

        if widget_type == 'entry':
            widget = ttk.Entry(frame)
            widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        elif widget_type == 'combobox':
            var = tk.StringVar()
            # For combobox, set state to "normal" to allow free text input
            widget = ttk.Combobox(frame, textvariable=var, values=options, state="normal")
            if options:
                widget.current(0)
            widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.input_widgets[key + '_var'] = var  # Store the variable too
        elif widget_type == 'textarea':
            widget = tk.Text(frame, height=text_height, width=40, relief=tk.SUNKEN, borderwidth=1, font=('Helvetica', 10))
            widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.input_widgets[key] = widget

    def update_input_fields(self, event=None):
        """Updates the input fields based on the selected task."""
        self.clear_input_frame()
        task = self.selected_task.get()

        if task == "Select Element":
            self.add_input_field("Selector Type:", "selector_type", widget_type='combobox',
                                 options=["ID", "Class Name (First)", "Tag Name (First)"])
            self.add_input_field("Selector Value:", "selector_value")
        elif task == "Add Event Listener":
            self.add_input_field("Element ID:", "element_id")
            self.add_input_field("Event Type:", "event_type", widget_type='combobox',
                                 options=["click", "mouseover", "mouseout", "keydown", "submit", "change", "load"])
            self.add_input_field("Function Body (Optional):", "function_body", widget_type='textarea', text_height=4)
        elif task == "Change Element Content":
            self.add_input_field("Element ID:", "element_id")
            self.add_input_field("Content Type:", "content_type", widget_type='combobox',
                                 options=["Text Content", "HTML Content"])
            self.add_input_field("New Content:", "new_content", widget_type='textarea', text_height=4)
        elif task == "Change Element Style":
            self.add_input_field("Element ID:", "element_id")
            self.add_input_field("CSS Property:", "style_prop", widget_type='combobox',
                                 options=['color', 'background-color', 'font-size', 'display', 'border', 'padding', 'margin'])
            self.add_input_field("Style Value:", "style_value")
        elif task == "Define Basic Function":
            self.add_input_field("Function Name:", "func_name")
            self.add_input_field("Parameters (comma-sep):", "params_str")
            self.add_input_field("Function Body (Optional):", "function_body", widget_type='textarea', text_height=5)

        # Clear previous output
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, "// Provide inputs above and click 'Generate Code'.")
        self.output_text.configure(state='disabled')

    def get_input_value(self, key, widget_type='entry'):
        """Safely gets the value from an input widget."""
        widget = self.input_widgets.get(key)
        if not widget:
            return None

        if widget_type == 'entry':
            return widget.get().strip()
        elif widget_type == 'combobox':
            var = self.input_widgets.get(key + '_var')
            return var.get() if var else None
        elif widget_type == 'textarea':
            return widget.get("1.0", tk.END).strip()

        return None

    def generate_code(self):
        """Generates the JavaScript code based on inputs."""
        task = self.selected_task.get()
        js_code = f"// Code generation for task: {task}\n// Timestamp: {datetime.datetime.now()}\n\n"

        try:
            if task == "Select Element":
                selector_type = self.get_input_value("selector_type", 'combobox')
                selector_value = self.get_input_value("selector_value")
                js_code += generate_select_element(selector_type, selector_value)
            elif task == "Add Event Listener":
                element_id = self.get_input_value("element_id")
                event_type = self.get_input_value("event_type", 'combobox')
                function_body = self.get_input_value("function_body", 'textarea')
                js_code += generate_event_listener(element_id, event_type, function_body)
            elif task == "Change Element Content":
                element_id = self.get_input_value("element_id")
                content_type = self.get_input_value("content_type", 'combobox')
                new_content = self.get_input_value("new_content", 'textarea')
                js_code += generate_change_content(element_id, content_type, new_content)
            elif task == "Change Element Style":
                element_id = self.get_input_value("element_id")
                style_prop = self.get_input_value("style_prop")
                style_value = self.get_input_value("style_value")
                js_code += generate_change_style(element_id, style_prop, style_value)
            elif task == "Define Basic Function":
                func_name = self.get_input_value("func_name")
                params_str = self.get_input_value("params_str")
                function_body = self.get_input_value("function_body", 'textarea')
                js_code += generate_function_definition(func_name, params_str, function_body)
            else:
                js_code += "// Task not yet implemented."
        except Exception as e:
            js_code += f"\n// An error occurred during code generation: {e}"
            messagebox.showerror("Generation Error", f"An unexpected error occurred:\n{e}")

        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', js_code)
        self.output_text.configure(state='disabled')

    def copy_to_clipboard(self):
        """Copies the generated code to the clipboard."""
        code = self.output_text.get('1.0', tk.END).strip()
        if code and not code.startswith("// Provide inputs"):
            try:
                pyperclip.copy(code)
                messagebox.showinfo("Copied", "JavaScript code copied to clipboard!")
            except pyperclip.PyperclipException as e:
                messagebox.showwarning("Copy Error", f"Could not copy to clipboard:\n{e}\n\nYou may need to install the 'pyperclip' library:\n pip install pyperclip")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred during copy:\n{e}")
        else:
            messagebox.showwarning("Nothing to Copy", "Generate some code first.")

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = JsGeneratorApp(root)
    root.mainloop()
