inputPath = ""
outputPath = ""
errors = 0

document.getElementById('gif').style.display = 'none';

// Initialize buttons
document.querySelectorAll('.neon-button').forEach(button => {
  button.addEventListener('click', async () => {
    const output = document.getElementById('terminal-output');

    if (button.classList.contains('load-btn')) {
      const path = await window.pywebview.api.select_input_folder();
      if (path) {
        appendToTerminal(`[+] Input folder selected: ${path} (づ ᴗ _ᴗ)づ`);
        inputPath = path;
      }
    } 
    else if (button.classList.contains('save-btn')) {
      const path = await window.pywebview.api.select_output_folder();
      if (path) {
        appendToTerminal(`[+] Output folder selected: ${path} (づ ᴗ _ᴗ)づ`);
        outputPath = path;
      }
    }
    else if (button.classList.contains('go-btn')) {
      if (inputPath !== "" && outputPath !== "") {
        appendToTerminal("[*] Starting process... ( ◡̀_◡́)ᕤ");
        errors = 0;
        document.getElementById('gif').src = 'images/ongoing.gif';
        document.getElementById('gif').style.display = 'block';


        const progressBar = document.getElementById('progress-bar');

        // Get list of JS files in input folder
        const files = await window.pywebview.api.list_js_files(inputPath);

        const total = files.length;
        const barLength = 20;

        if (total === 0) {
          appendToTerminal("[!] No .js files found in the input folder. (¬`‸´¬)", "#ff9130ff");
          return;
        }

        for (let i = 0; i < total; i++) {
          const file = files[i];
          await window.pywebview.api.js_to_p8(file, outputPath);

          const percent = Math.round(((i + 1) / total) * 100);
          const filledLength = Math.round((barLength * (i + 1)) / total);
          const bar = '[' + '='.repeat(filledLength) + ' '.repeat(barLength - filledLength) + ']';

          progressBar.textContent = `${bar} %${percent}`;

          output.parentElement.scrollTop = output.parentElement.scrollHeight;
        }

        appendToTerminal("[✓] Process completed! ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧", "#30bdffff");
        if(errors == 0)
        {
          document.getElementById('gif').src = 'images/success.gif';
        }
        else{
          appendToTerminal(`But ${errors} error(s) happened. (╥﹏╥)`, "#ff9130ff");
        }

      } else {
        appendToTerminal("[!] Please select both input and output folders!", "#ff5555");
      }
    }

    output.parentElement.scrollTop = output.parentElement.scrollHeight;
  });
});

// Terminal output helper
function appendToTerminal(text, color = '#ffffff') {
  const output = document.getElementById('terminal-output');
  const line = document.createElement('div');
  line.textContent = text;
  line.style.color = color;
  output.appendChild(line);

  line.scrollIntoView({ behavior: "auto", block: "end" });
}

let progressBar = document.getElementById('progress-bar');
if (!progressBar) {
  progressBar = document.createElement('pre');
  progressBar.id = 'progress-bar';
  progressBar.style.color = '#66ff66';
  progressBar.style.marginTop = '5px';

  const terminal = document.querySelector('.terminal');
  terminal.appendChild(progressBar);
}
