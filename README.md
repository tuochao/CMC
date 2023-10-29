##Instruction
### requirement and description
requirement and description is in file: "Curious Monkey Chat.pdf"

### python version
This codebase use python 3.9.14, please use python 3.9.X to run it.

### install
1. create a venv in pycharm or terminal, run `source venv/bin/activate` to enter virtual environment. 
2. run `pip3 install -r requirements.txt` to install required packages. The majority packages are flask, pandas and requests.

### run
1. run `python3 app.py` to start CMC service.
2. run `python3 report_program.py` to generate report. Report will be printed in console and written into report/report.txt
3. run 'python3 test_driver.py --friend={friend name}' to run test driver. To make script name more meaningful, can also use
```angular2html
alias talk-to-george='python3 test_driver.py'
talk-to-george --friend={friend name}
```
to run test driver.
