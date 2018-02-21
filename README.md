## Project

This project, Coding by Dictation, is a hands-free programming application. 
This application allows users to write a program by just dictating the code to the computer via voice input.
This project aims to help people with disabilities or conditions such as the Carpal Tunnel Syndrome (CTS) to write computer programs.
CTS (also known as Repetitive Strain Injury) is a medical condition which affects the median nerves of the hand, causing pain and discomfort to the user.

## Installation

1. Ensure that you have `python version 2.7` installed in your computer. If not, proceed to https://www.python.org/downloads/ to download and install `python version 2.7`. <br />
> Note that python version 3 and above are not supported and will cause alot of files to fail.
2. `pip` should come with and already be installed with `python`. In case it does not, please see https://pip.pypa.io/en/stable/installing/ if you need help with the download and installation. 
3. Proceed to fork this project and create a local clone of your fork. For help, please see: https://help.github.com/articles/fork-a-repo/
4. At your local repository of the project, open `shell`/`command prompt`/`bash` or any equivalent program for your OS. Type `pip install -r requirements.txt` to install all python library dependencies.
5. At the root of the project, create a file named `SpeechRecognition-8e50e15b5266.json` 
6.
 a) The contents of the newly created json file contains the private key to our speech recognition module for google cloud. Thus, contact Nicholas privately to get the contents. <br />
 b) Alternatively, you can create your own Google Cloud Platform account for your own Google Cloud Speech Recognition API. Refer to  https://cloud.google.com/speech/docs/getting-started> for details and instructions. Basically, create a project and enable billing for the project, and enable Google Cloud Speech API for the project. Then, set up a Service Account Key credentials for the project and download the JSON file containing the API credentials. Replace the file created in step 5 with this new file. Replace the name of this file accordingly in `credentials.py`, replacing the value of `GOOGLE_CREDENTIAL_FILE` in `credentials.py` <br />
 
 7. Proceed to look at the following section on `Usage` to learn about how to use the program after installation.


## Usage

Run the python file `CodingByDictationUI.py` with IDLE or any other python IDE <br />
Optionally, you can run the `cleanup.py` program after you are done using the program, to kill all the daemon threads/processes created
by the program.

## Contributors

Lam Zhen Zong, Nicholas

## Credits

Ooi Wei Tsang (for supervising and mentoring this project) <br />
Gao Risheng (for the component to convert structured command to code)

## License

School of Computing, National University of Singapore
