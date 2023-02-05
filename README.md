# circleci-env-cli
CLI tool for manage CircleCI contexts and environment vars

## Installation
### Install locally
```
pip install -r requirements.txt
./circleci_env_cli.py [OPTIONS]
```

### Install via Pip
```
pip install circleci-env-cli
```

### Install via Docker
```
docker run --rm phsmith/circleci-env-cli:latest [OPTIONS]
```

## Usage

A [CircleCI personal API token](https://circleci.com/docs/managing-api-tokens/#creating-a-personal-api-token) must be create before use this tool.

> All options can be specified as environment variables in the format: `CIRCLE_<OPTION>`.
>
> Example: `CIRCLE_TOKEN=********`

```
Usage: circleci-env-cli [OPTIONS]

  CLI tool for manage CircleCI contexts and environment vars

Options:
  -u, --api-url <circleci_api_url>
                                  [default: https://circleci.com/api]
  -t, --token <circleci_token>    [default: (CIRCLE_TOKEN)]
  -c, --context <context_name>    It will ask for create if does not exists
  -p, --project <project_slug>    Example: github/org-name/project-name
                                  [required]
  -e, --env <environment_var>
  -ef, --env-file <environment_vars_file>
  -d, --delete                    Context only, will delete the context
                                  Context + vars, will delete the context vars
                                  Vars only, will delete the environment vars
  -ot, --owner-type <owner_type>  [default: organization]
  --debug
  --help                          Show this message and exit.
```

### Examples

#### Add project environment variables
```
$ circleci-env-cli -p github/myorg/myproject -e KEY1=VAL1 -e KEY2=VAL2 -ef project.envs.txt
> Successfully add/update variable: KEY1
> Successfully add/update variable: KEY2
> Successfully add/update variable: KEY3
> Successfully add/update variable: KEY4
```

#### Delete project environment variables
```
$ circleci-env-cli -p github/myorg/myproject -e KEY1 -e KEY2 -d
> Successfully delete variable: KEY1
> Successfully delete variable: KEY2
```

#### Create/update a context and add variables
```
$ circleci-env-cli -p github/myorg/myproject -c mycontext -e KEY1=VAL1 -e KEY2=VAL2
The context named "mycontext" was not found. Do you want to create it? [y/n]: y
> Successfully create context: mycontext
> Successfully add/update context variable: KEY1
> Successfully add/update context variable: KEY2
```

#### Delete context variables
```
$ circleci-env-cli -p github/myorg/myproject -c mycontext -e KEY1 -e KEY2 -d
> Successfully delete context variable: KEY1
> Successfully delete context variable: KEY2
```

#### Delete context
```
$ circleci-env-cli -p github/myorg/myproject -c mycontext -d
Are you sure want to delete the context "mycontext"? [y/n]: y
> Successfully delete context
```
