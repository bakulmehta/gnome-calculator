import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from backend import CalculatorBackend

class Calculator(Gtk.Window):
    def __init__(self):
        super().__init__(title="Calculator")
        self.set_border_width(0)
        self.set_resizable(True)
        self.set_name("calculator-window")
        
        # Get screen dimensions and set window to full height
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        screen_height = geometry.height
        screen_width = geometry.width
        
        # Set calculator to use most of screen height but leave room for system UI
        calc_width = min(713, int(screen_width * 0.59))  # Use 59% of screen width or 713px, whichever is smaller
        calc_height = int(screen_height * 0.90)  # Use 90% of screen height to leave room for title bar, taskbar, etc.
        self.set_default_size(calc_width, calc_height)
        
        # Set dark theme
        self.set_app_paintable(True)
        
        # Force dark theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)
        
        self.backend = CalculatorBackend()
        self.just_calculated = False  # Flag to track if we just got a result

        # Apply CSS styling first
        self.apply_css()
        
        # Main container - center the calculator content
        outer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        outer_box.get_style_context().add_class("main-container")
        
        # Add expanding space on sides to center content
        outer_box.pack_start(Gtk.Box(), True, True, 0)  # Left spacer
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.set_size_request(calc_width, calc_height)  # Fixed calculator size
        outer_box.pack_start(main_box, False, False, 0)    # Calculator content (fixed)
        
        outer_box.pack_start(Gtk.Box(), True, True, 0)  # Right spacer
        
        self.add(outer_box)

        # Working area container with fixed size
        working_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        working_container.set_size_request(calc_width - 24, 530)  # Fixed size: width minus margins, 530px height
        
        # History area - scrollable
        history_area = Gtk.ScrolledWindow()
        history_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        history_area.get_style_context().add_class("history-area")
        
        self.history_view = Gtk.TextView()
        self.history_view.set_editable(False)
        self.history_view.set_cursor_visible(True)
        self.history_view.set_justification(Gtk.Justification.LEFT)
        self.history_view.set_valign(Gtk.Align.END)
        self.history_view.get_style_context().add_class("history-display")
        
        self.history_buffer = self.history_view.get_buffer()
        self.history_buffer.set_text("")
        
        history_area.add(self.history_view)
        
        # Separator line
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.get_style_context().add_class("separator")
        
        # Current typing area
        typing_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        typing_area.get_style_context().add_class("typing-area")
        
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(True)
        self.text_view.set_justification(Gtk.Justification.LEFT)
        self.text_view.set_valign(Gtk.Align.START)
        self.text_view.get_style_context().add_class("typing-display")
        
        self.text_buffer = self.text_view.get_buffer()
        self.text_buffer.set_text("")
        
        typing_area.pack_start(self.text_view, True, True, 0)
        
        # Pack everything together
        working_container.pack_start(history_area, True, True, 0)
        working_container.pack_start(separator, False, False, 0)
        working_container.pack_start(typing_area, False, False, 0)
        
        # Set fixed heights
        history_area.set_size_request(-1, 450)  # Fixed 450px for history
        typing_area.set_size_request(-1, 76)    # Fixed 76px for typing (reduced by 5%)
        
        main_box.pack_start(working_container, True, True, 0)

        # Button grid - fixed size at bottom
        button_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        button_container.set_size_request(calc_width - 24, 220)  # Fixed size: 220px height
        
        self.grid = Gtk.Grid()
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_spacing(2)
        self.grid.set_column_spacing(2)
        self.grid.set_margin_left(8)
        self.grid.set_margin_right(8)
        self.grid.set_margin_top(8)
        self.grid.set_margin_bottom(8)
        
        button_container.pack_start(self.grid, True, True, 0)
        main_box.pack_start(button_container, False, False, 0)

        # Button layout to match the image exactly
        buttons = [
            # Row 0
            ("C", 0, 0, "function"), ("(", 0, 1, "function"), (")", 0, 2, "function"), ("mod", 0, 3, "function"), ("π", 0, 4, "function"),
            # Row 1  
            ("7", 1, 0, "number"), ("8", 1, 1, "number"), ("9", 1, 2, "number"), ("÷", 1, 3, "operator"), ("√", 1, 4, "function"),
            # Row 2
            ("4", 2, 0, "number"), ("5", 2, 1, "number"), ("6", 2, 2, "number"), ("×", 2, 3, "operator"), ("x²", 2, 4, "function"),
            # Row 3
            ("1", 3, 0, "number"), ("2", 3, 1, "number"), ("3", 3, 2, "number"), ("-", 3, 3, "operator"), 
            # Row 4
            ("0", 4, 0, "number"), (".", 4, 1, "operator"), ("%", 4, 2, "operator"), ("+", 4, 3, "operator"),
        ]

        for (label, row, col, style_class) in buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked)
            button.get_style_context().add_class(style_class)
            self.grid.attach(button, col, row, 1, 1)
            
        # Add equals button separately to span 2 rows
        equals_button = Gtk.Button(label="=")
        equals_button.connect("clicked", self.on_button_clicked)
        equals_button.get_style_context().add_class("equals")
        self.grid.attach(equals_button, 4, 3, 1, 2)  # Column 4, Row 3, Width 1, Height 2

        # Enable keyboard input
        self.set_can_focus(True)
        self.set_focus_on_map(True)
        self.connect("key-press-event", self.on_key_press)
        
        # Make sure window can receive all key events
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)



    def on_key_press(self, widget, event):
        # Handle keyboard input
        key = event.keyval
        key_name = Gdk.keyval_name(key)

        
        # Map keyboard keys to calculator buttons
        key_mappings = {
            # Numbers
            Gdk.KEY_0: "0", Gdk.KEY_1: "1", Gdk.KEY_2: "2", Gdk.KEY_3: "3", Gdk.KEY_4: "4",
            Gdk.KEY_5: "5", Gdk.KEY_6: "6", Gdk.KEY_7: "7", Gdk.KEY_8: "8", Gdk.KEY_9: "9",
            # Operations
            Gdk.KEY_plus: "+", Gdk.KEY_minus: "-", Gdk.KEY_asterisk: "×", Gdk.KEY_slash: "÷",
            Gdk.KEY_percent: "%", Gdk.KEY_period: ".", Gdk.KEY_comma: ".",
            # Parentheses
            Gdk.KEY_parenleft: "(", Gdk.KEY_parenright: ")",
            # Equals and Enter
            Gdk.KEY_equal: "=", Gdk.KEY_Return: "=", Gdk.KEY_KP_Enter: "=",
            # Clear
            Gdk.KEY_Escape: "C", Gdk.KEY_Delete: "C",
            # Keypad numbers
            Gdk.KEY_KP_0: "0", Gdk.KEY_KP_1: "1", Gdk.KEY_KP_2: "2", Gdk.KEY_KP_3: "3", Gdk.KEY_KP_4: "4",
            Gdk.KEY_KP_5: "5", Gdk.KEY_KP_6: "6", Gdk.KEY_KP_7: "7", Gdk.KEY_KP_8: "8", Gdk.KEY_KP_9: "9",
            # Keypad operations
            Gdk.KEY_KP_Add: "+", Gdk.KEY_KP_Subtract: "-", Gdk.KEY_KP_Multiply: "×", 
            Gdk.KEY_KP_Divide: "÷", Gdk.KEY_KP_Decimal: ".", Gdk.KEY_KP_Equal: "="
        }
        
        # Special handling for 'x' key to represent multiplication
        if key_name == 'x' or key_name == 'X':
            button_label = "×"
        elif key == Gdk.KEY_BackSpace:
            button_label = "BACKSPACE"
        elif key in key_mappings:
            button_label = key_mappings[key]
        else:
            return False  # Let other handlers process the key
        
        # Simulate button click
        self.simulate_button_click(button_label)
        return True  # Event handled
    
    def simulate_button_click(self, label):
        # Simulate the button click logic
        if label == "=":
            # Add the calculation to history
            current_expr = self.backend.expression
            result = self.backend.evaluate()
            
            # Format result to show only up to 9 decimal places
            if isinstance(result, float):
                # Remove trailing zeros and limit to 9 decimal places
                formatted_result = f"{result:.9f}".rstrip('0').rstrip('.')
            else:
                formatted_result = str(result)
            
            # Replace * with × and / with ÷ for display purposes in the expression
            display_expr = current_expr.replace('*', '×').replace('/', '÷')
            
            # Add equation to history area with proper spacing
            current_history = self.history_buffer.get_text(
                self.history_buffer.get_start_iter(),
                self.history_buffer.get_end_iter(),
                False
            )
            
            # Format with proper spacing - equation takes 60%, = at boundary, answer takes 40%
            # Calculate padding to position = sign exactly at 60/40 split
            equation_part = display_expr
            answer_part = formatted_result
            
            # Use character width calculation for proper alignment
            total_width = 45  # Increased to use more available space
            equation_width = int(total_width * 0.6)
            
            # Left-align equation, push answer to extreme right
            # Padding to reach the = sign position (60% boundary)
            equation_to_equals_padding = max(1, equation_width - len(equation_part))
            
            # Calculate maximum padding to push answer to extreme right edge
            used_space = len(equation_part) + equation_to_equals_padding + 2 + len(answer_part)  # +2 for "= "
            answer_padding = max(1, total_width - used_space)
            
            # Format: equation + padding + = + space + maximum_padding + answer (extreme right)
            formatted_line = f"{equation_part}{' ' * equation_to_equals_padding}= {' ' * answer_padding}{answer_part}"
            
            if current_history == "":
                new_history = formatted_line
            else:
                new_history = f"{current_history}\n{formatted_line}"
            
            self.history_buffer.set_text(new_history)
            
            # Show only result in typing area
            self.text_buffer.set_text(formatted_result)
            
            # Clear the backend and set it to the result for next calculation
            self.backend.clear()
            self.backend.input(formatted_result)
            self.just_calculated = True  # Set flag that we just calculated
            
            # Keep scroll position at top - do not auto-scroll to bottom
            # User can manually scroll to see latest entries
            
        elif label == "C":
            self.backend.clear()
            self.text_buffer.set_text("")
            self.just_calculated = False  # Reset flag
        elif label == "BACKSPACE":
            # Handle backspace - check for selection first
            if self.text_buffer.get_has_selection():
                # If text is selected (e.g., Ctrl+A), clear everything
                self.backend.clear()
                self.text_buffer.set_text("")
            else:
                # No selection, remove last character
                current_expr = self.backend.expression
                if current_expr and len(current_expr) > 0:
                    # Remove last character from backend
                    new_expr = current_expr[:-1]
                    self.backend.clear()
                    if new_expr:
                        self.backend.input(new_expr)
                    
                    # Update display
                    display_text = new_expr if new_expr else ""
                    display_text = display_text.replace('*', '×').replace('/', '÷')
                    self.text_buffer.set_text(display_text)
                else:
                    # If nothing to delete, clear the display
                    self.text_buffer.set_text("")
        else:
            current_text = self.text_buffer.get_text(
                self.text_buffer.get_start_iter(),
                self.text_buffer.get_end_iter(),
                False
            )
            
            if (current_text == "0" or current_text == "") and label.isdigit():
                self.backend.clear()
            elif self.just_calculated and label.isdigit():
                # If we just calculated and user types a number, start fresh
                self.backend.clear()
                self.just_calculated = False  # Clear flag after handling
            elif self.just_calculated and label in ['+', '-', '×', '÷', '*', '/', '%', '(', ')']:
                # If we just calculated and user types an operator, continue from result
                self.just_calculated = False  # Clear flag after handling
            
            # Convert × back to * for backend processing
            backend_label = label.replace('×', '*').replace('÷', '/')
            self.backend.input(backend_label)
            display_text = self.backend.expression if self.backend.expression else "0"
            
            # Replace * with × for display purposes
            display_text = display_text.replace('*', '×').replace('/', '÷')
            
            # Update only the typing area
            self.text_buffer.set_text(display_text)

    def apply_css(self):
        css_provider = Gtk.CssProvider()
        css = """
        @define-color window_bg_color #222226;
        @define-color window_fg_color #ffffff;
        @define-color view_bg_color #343437;
        @define-color view_fg_color #ffffff;
        @define-color accent_color #3584e4;
        @define-color accent_bg_color #1c71d8;
        
        * {
            outline: none;
        }
        
        window {
            background-color: @window_bg_color;
            color: @window_fg_color;
        }
        
        .main-container {
            background-color: @window_bg_color;
        }
        
        .history-area {
            background-color: #3e3e41;
            border-radius: 8px 8px 0 0;
            margin: 12px 12px 0 12px;
            box-shadow: inset 0 1px 2px alpha(black, 0.1);
        }
        
        .typing-area {
            background-color: #343437;
            border-top: none;
            border-radius: 0 0 8px 8px;
            margin: 0 12px 12px 12px;
            box-shadow: inset 0 1px 2px alpha(black, 0.1);
        }
        
        .separator {
            margin: 0 12px;
            min-height: 1px;
        }
        
        .history-display {
            background-color: transparent;
            color: @view_fg_color;
            font-size: 24px;
            font-weight: 500;
            font-family: 'Consolas';
            border: none;
            padding: 15px 20px;
        }
        
        .typing-display {
            background-color: transparent;
            color: @view_fg_color;
            font-size: 20px;
            font-weight: 500;
            font-family: 'Consolas';
            border: none;
            padding: 15px 20px;
        }
        
        .history-display text {
            background-color: transparent;
            color: @view_fg_color;
        }
        
        .typing-display text {
            background-color: transparent;
            color: @view_fg_color;
        }
        
        textview text {
            background-color: transparent;
            color: @view_fg_color;
        }
        
        button {
            background: #3a3a3a;
            background-image: none;
            color: @window_fg_color;
            font-size: 19px;
            font-weight: bold;
            font-family: 'Cantarell';
            border: none;
            border-radius: 10px;
            min-height: 37px;
            min-width: 45px;
            margin: 1px;
            box-shadow: 0 1px 2px alpha(black, 0.05);
            text-shadow: none;
            transition: all 200ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        
        button:hover {
            background: #404040;
            box-shadow: 0 2px 4px alpha(black, 0.1);
        }
        
        button:active {
            background: #2a2a2a;
            box-shadow: inset 0 1px 2px alpha(black, 0.2);
        }
        
        button:focus {
            box-shadow: 0 0 0 2px alpha(@accent_color, 0.3);
        }
        
        .number {
            background: #4e4e51;
        }
        
        .number:hover {
            background: #5a5a5d;
        }
        
        .operator {
            background: #38383c;
        }
        
        .operator:hover {
            background: #3e3e42;
        }
        
        .function {
            background: #38383c;
            font-weight: 600;
        }
        
        .function:hover {
            background: #3e3e42;
        }
        
        .equals {
            background: #3584e4;
            color: white;
            font-weight: 700;
        }
        
        .equals:hover {
            background: #4094f0;
        }
        
        .equals:active {
            background: #2574d8;
        }
        
        .equals:focus {
            box-shadow: 0 0 0 2px alpha(white, 0.4);
        }
        """
        css_provider.load_from_data(css.encode())
        
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, 
            css_provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def on_button_clicked(self, widget):
        label = widget.get_label()
        self.simulate_button_click(label)

if __name__ == "__main__":
    win = Calculator()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    
    # Ensure the window gets keyboard focus
    win.grab_focus()
    win.present()
    
    Gtk.main()
