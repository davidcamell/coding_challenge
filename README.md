# Data Pipeline Technical Challenge

This was a technical challenge I once was asked to complete. The description below came from the original challenge, all other content is original and completed by only me.

## Challenge Description

> The challenge is to develop a simple AWS S3 storage analysis tool.
> 
> The tool must be executable from the command line, and must return a list of all [S3](https://aws.amazon.com/documentation/s3/) buckets accessible to the user. > For each bucket, the tool should display the following information:
> 
> - Bucket name
> - Creation date
> - Number of files
> - Aggregate size of files (an option should permit display in bytes, kB, MB, etc.)
> - Last modified date of the most recent file
> 
> The tool must work on Linux and OSX, and the installation process must be clearly documented. Ideally, your tool won't require installation of any other tools > / libraries / frameworks to work.

> Your are free to use the programming language and the [SDK](https://aws.amazon.com/tools/) of your choice. You may assume the user has `bash`, `python3`, and > > `pip` installed on their system; any other executables and libraries must be included as part of the installation process. The installation process should be > > quick and easy, and the documentation must cover installation on both Ubuntu 18.04 and OSX.
> 
> Your project should be hosted on GitHub and be a standalone project

# coding_challenge response
For this challenge, I have created `S3Explore`, a simple command line based AWS S3 analysis tool written in python. 

All command line instructions below are given as if the user has navigated to the git directory of the program. The program does require Python 3.

## Installation

### Clone git repo
The first step is to download the code from github. The most basic way is to use command line to clone the repo to your local system:
```
git clone git@github.com:davidcamell/coding_challenge.git {LOCAL_DESTINATION}
```

### Run setup.sh

Use the `setup.sh` script to prepare basic infrastructure needed for the program to operate. This will create credential storage file locally, set up data directory for logging of results, and automate the [pip](https://pip.pypa.io/en/stable/) installation of needed packages as listed in 'requirements.txt':

```bash
./setup.sh
```

## Credential Management
There are two methods available to manage credentials:
### AWS Command Line Interface (AWS CLI)
If you already have [AWS Command Line Interface](https://aws.amazon.com/cli/) installed on your system, you can use the profiles you already have set up there. Simply enter the name of a pre-existing profile in the `--profile` (or `-p`) argument of the script as described below under Usage, and explicitly request this method by also supplying the `--use_aws_cli_creds` (or `-a`) switch. Refer to the [AWS CLI documentation](https://docs.aws.amazon.com/cli/index.html) for more information. You can edit the credentials in the file directly (by default stored at `~/.aws/credentials`), or via the command:
```
aws configure
```
### .cred.json
If you do not already have AWS CLI installed, or if you simply want to keep credentials used for this program separate, there is a lightweight way to supply and save your credentials. There is a file `.cred.json` that will be created in the `data` directory within the app directory when `setup.sh` is run. You can simply edit the doc, for example via command line (`pico` just used here for an example):
```bash
pico data/.cred.json
```
The initial contents will be "fake" credentials as an example, which you would replace with your own.
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
If you would like to access multiple data sources, you also have the option of adding additional profiles by adding another nested `dict` inside the `json` formatted file:
```buildoutcfg
{
  "aws_profiles": {
    "default": ...
    },
    "second_profile": {
      "aws_access_key_id": "AKIAIOSFODNNEXAMPLE2",
      "aws_secret_access_key": "tYUioPUtnFEMI/K7MDENG/bPxRfiEXAMPLEKEY#2"
    }
  }
}
```

## Usage
The program is python script based, but there is a `bash` wrapper that helps make sure we are using the right virtual environment and paths (design decision was made to not permanently alter the user's bash profile, etc.). To run the program, simply run:
```
./s3explore.sh {see arguements below}
```
Program behavior, display formats, and credentials are detemined by the following script arguments, which you can also access from  `./s3explore.sh --help` anytime:
```bash
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
Results will print out on the command line:
```
Bucket "bucket_example_prod", created 05/15/2017
 Contains 8653 files
 Most recently updated 11/18/2019
 Total size: 986.0 MB

Bucket "bucket_example_dev", created 05/13/2015
 Contains 5450 files
 Most recently updated 07/10/2019
 Total size: 343.7 MB

```

## Testing
Unit tests are also included. The script `run_tests.sh` can be used in a similar way to the main script above. It preps the system for running `pytest` and also passes through any arguments that a user may want to include.
