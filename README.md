<a href="https://github.com/labjack/ljm_constants">
	<img 
	 alt="tag:?"
	 src="https://img.shields.io/github/workflow/status/labjack/ljm_constants/test"
	>
</a>

# ljm_constants

[LJM](https://labjack.com/ljm) constants files and related tools.


## LabJack/LJM/ directory

The [LabJack/LJM/ directory](LabJack/LJM/readme.md) is installed for all [LJM installations](https://labjack.com/support/software/api/ljm/what-ljm-files-are-installed). Of the files contained in it, the most important is ljm_constants.json, which describes the "Modbus map" of all devices LJM supports. This Modbus map describes device registers by name, address, data type, description, etc.

For a web app version of ljm_constants.json, see [LabJack's Modbus Map](https://labjack.com/support/software/api/modbus/modbus-map), which is part of the [ljsimpleregisterlookup](https://github.com/labjack/ljsimpleregisterlookup) project. ljsimpleregisterlookup also produces ljscribe's automated documentation, which is interleaved throughout the [T-series Datasheet](https://labjack.com/support/datasheets/t-series/).


## Generated code

generate_c_header.py outputs generated content to gen_output/. Currently, it's a C header file which contains a constants version of ljm_constants.json. Test code for gen_output/ is in gen_test/.


## Continuous Integration

CI is done by Travis CI. See .travis.yml.


## Contributing


#### ljm_constants.json

Non-LabJack employees: Since in ljm_constant.json is used to generate T-series Datasheet documentation and the Modbus Map lookup tool, changes in ljm_constant.json are considered sensitive. It's easy to write a description that will confuse or mislead. For that reason, contributors not lucky enough to work at LabJack are encouraged to submit Issues instead of directly submitting Pull Requests. LabJack employees will vet Issues carefully.

LabJack employees: LabJack employees should get themselves added to LabJack's GitHub organization first. Then:

- Navigate to [ljm_constants.json on GitHub](https://github.com/labjack/ljm_constants/blob/master/LabJack/LJM/ljm_constants.json)
- Hit the edit button to begin editing. (This is a pencil icon, as of writing.)
- Make your changes in the browser window.
- Scroll to the bottom of the page to make a commit message.
- Create a new branch. (Don't commit directly to the `master` branch, please.)
- Commit changes.
- Submit a pull request.
- Wait for the pull request to be addressed. Or bug someone to address it sooner.


#### Other Code

Code contributions not related to ljm_constants.json should follow conventions as set forth in ljmmm.py. Code should have reasonable tests.
