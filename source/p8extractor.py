import re
import os
import webview
import sys
from pathlib import Path
from webview import FileDialog

from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('interface')

class PICO8JSExtractor:
    def __init__(self):
        # Get the absolute path to the interface directory
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle
            base_path = sys._MEIPASS
        else:
            # If the application is run from a Python interpreter
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.interface_dir = os.path.join(base_path, 'interface')
        self.input_path = None
        self.output_path = None

    def start_gui(self):
        # Convert Path to proper file URL using os.path
        html_path = os.path.join(self.interface_dir, 'index.html')
        file_url = 'file:///' + html_path.replace('\\', '/')
        
        # Create window with web interface
        window = webview.create_window(
            'PICO-8 Extractor',
            url=file_url,
            width=800,
            height=800,
            resizable=False,
            min_size=(800, 800),
            js_api=self
        )
        
        # Set window icon after creation
        if sys.platform == 'win32':
            import ctypes
            myappid = 'com.juq.pico8extractor.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        webview.start()


    def js_to_p8(self, js_filename, output_folder):
        try:
            # Generate output filename (same as JS file, but .p8.rom extension)
            base_name = os.path.splitext(os.path.basename(js_filename))[0]
            output_filename = os.path.join(output_folder, base_name + ".p8.rom")

            # Read JS file content
            with open(js_filename, 'r', encoding='utf-8', errors='ignore') as f:
                js_content = f.read().replace('\n', '')

            # Extract _cartdat array using regex
            cartdat_match = re.search(
                r'var _cartdat\s*=\s*\[([\d\s,]*)\];',
                js_content,
                re.DOTALL
            )

            if not cartdat_match:
                webview.windows[0].evaluate_js("document.getElementById('gif').src = 'images/error.gif';")
                webview.windows[0].evaluate_js("errors += 1;")
                raise ValueError("_cartdat array not found in JavaScript file.")

            # Convert comma-separated string to integer list
            cart_data = [
                int(x) for x in cartdat_match.group(1).split(',') if x.strip()
            ]

            # Validate ROM size (should be exactly 32KB)
            if len(cart_data) != 32768:
                self.log_to_terminal(f"⚠️ Warning: Expected 32768 bytes, found {len(cart_data)} bytes.", "#ffaa00")
                self.log_to_terminal("Proceeding anyway...", "#ffaa00")

            # Check write permission
            if not os.access(output_folder, os.W_OK):
                webview.windows[0].evaluate_js("document.getElementById('gif').src = 'images/error.gif';")
                webview.windows[0].evaluate_js("errors += 1;")
                raise PermissionError(f"No write permission to output folder: {output_folder}")

            # Write binary data to output file
            with open(output_filename, 'wb') as f:
                f.write(bytes(cart_data))

            safe_path = output_filename.replace("\\", "\\\\")
            self.log_to_terminal(f"✅ ROM created successfully: {safe_path}", "#00ff88")


        except Exception as e:
            import traceback
            traceback.print_exc()
            webview.windows[0].evaluate_js("document.getElementById('gif').src = 'images/error.gif';")
            webview.windows[0].evaluate_js("errors += 1;")
            self.log_to_terminal(f"❌ Error: {str(e)}", "#FF0000")

    def select_input_folder(self):
        result = webview.windows[0].create_file_dialog(
            FileDialog.FOLDER
        )
        if result:
            self.input_path = result[0]
            return result[0]
        return None

    def select_output_folder(self):
        result = webview.windows[0].create_file_dialog(
            FileDialog.FOLDER
        )
        if result:
            self.output_path = result[0]
            return result[0]
        return None
    
    def list_js_files(self, folder_path):
        try:
            return [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.lower().endswith('.js')
            ]
        except Exception as e:
            webview.windows[0].evaluate_js("document.getElementById('gif').src = 'images/error.gif';")
            webview.windows[0].evaluate_js("errors += 1;")
            self.log_to_terminal(f"Error listing JS files: {str(e)}", "#FF0000")
            return []
    
    def log_to_terminal(self, text, color='#ffffff'):
        js_code = f'appendToTerminal("{text}", "{color}");'
        webview.windows[0].evaluate_js(js_code)



if __name__ == '__main__':
    extractor = PICO8JSExtractor()
    extractor.start_gui()