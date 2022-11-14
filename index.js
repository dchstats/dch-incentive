const {app, BrowserWindow} = require('electron')

function createWindow () {
    window = new BrowserWindow({width: 600, height: 400})
    window.loadFile('index.html')
  }

app.on('ready', createWindow)

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit()
    }
  })

let {PythonShell} = require('python-shell')

let options = {
  mode: 'text',
  pythonOptions: ['-u'], // get print results in real-time
  args: ["-i 'atul'"]
};


let pyshell = new PythonShell('test.py', options);

// sends a message to the Python script via stdin
//pyshell.send('hello');

pyshell.on('message', function (message) {
  // received a message sent from the Python script (a simple "print" statement)
  console.log(message);
});

// end the input stream and allow the process to exit
pyshell.end(function (err,code,signal) {
  if (err) throw err;
  console.log('The exit code was: ' + code);
  console.log('The exit signal was: ' + signal);
  console.log('finished');
});