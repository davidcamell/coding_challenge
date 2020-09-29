# tagup_challenge
Simple AWS S3 storage analysis tool.

All command line instructions below are given as if the user has navigated to the git directory of the program.

## Installation

### Clone git repo


### Run setup.sh

Use the `setup.sh` script to prepare basic infrastructure needed for the program to operate. This will create credential storage file locally, set up data directory for logging of results, and automate the [pip](https://pip.pypa.io/en/stable/) installation of needed packages as listed in 'requirements.txt'. 

```bash
./setup.sh
```

## Credential Management
There are two methods available to manage credentials.
### AWS Command Line Interface (AWS CLI)
If you already have [AWS Command Line Interface](https://aws.amazon.com/cli/) installed on your system, you can use the profiles you already have set up there. Simply enter the name of a pre-existing profile in the `--profile` (or `-p`) argument of the script as described below under Usage, and explicitly request this method by also supplying the `--use_aws_cli_creds` (or `-a`) switch. 
### .cred.json
If you do not already have AWS CLI installed, there is a lightweight way to supply and save your credentials. There is a file `cred.json`
```bash
pico data/.cred.json
```

```buildoutcfg
{
  "aws_profiles": {
    "default": {
      "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
      "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
  }
}
```

## Usage

```python
usage: s3explore.py [-h] [-p PROFILE] [-s {bytes,kb,mb,gb,tb}]
                    [-d {month_first,year_first,day_first}] [-a] [-t] [-w]

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        Provide profile name (will use default if not
                        supplied).
  -s {bytes,kb,mb,gb,tb}, --size_format {bytes,kb,mb,gb,tb}
                        Choose unit to display total bucket size.
  -d {month_first,year_first,day_first}, --date_format {month_first,year_first,day_first}
                        Choose unit to display last modified date for bucket
                        files, for example 09/29/2020, 2020_09_29, or
                        29/09/2020
  -a, --use_aws_cli_creds
                        Use AWS profiles instead of credentials stored by this
                        app.
  -t, --show_time_modified
                        Include the time of day for last modified file, for
                        example "... 13:01:20".
  -w, --write_results_to_disk
                        After displaying in command line, also write to a log
                        file in "data" directory.

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)