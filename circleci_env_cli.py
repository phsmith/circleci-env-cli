#!/usr/bin/env python
import logging
from concurrent.futures import as_completed, ThreadPoolExecutor

import click
from pycircleci.api import Api, CircleciError

class CircleCIEnvsManage:
    """CircleCI environment variables managent Class"""

    def __init__(self, api_url, token, debug=False):
        """Initialize a client to interact with CircleCI API.

        :param url: CircleCI API URL.
        :param token: CircleCI API access token.
        :param debug: Enable verbose outputs.
        """

        self.circle_client = Api(token=token, url=api_url)

        if debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format="[%(levelname)s] %(module)s:%(funcName)s - %(message)s"
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="> %(message)s"
            )

        self.logger = logging.getLogger(__class__.__name__)

    def get_context_id(
        self, org, owner_id, owner_type, vcs_type, context
    ):
        """Get CircleCI Project Context ID.

        :param org: Org or user name.
        :param owner_id: Org or user id.
        :param owner_type: Either ``organization`` or ``account``.
        :param vcs_type: VCS type (``github``, ``bitbucket``).
        :param context: Context name.
        """

        try:
            contexts = self.circle_client.get_contexts(
                org, owner_id, owner_type, vcs_type, True
            )
            context_id = list(
                filter(lambda c: True if c["name"] == context else None, contexts)
            )
        except Exception as error:
            raise SystemExit(f"Error: {error}")

        return context_id[0]["id"] if context_id else None

    def manage_context(
        self, org, owner_id, owner_type, vcs_type, context,
        context_id, env, value, create=False, delete=False
    ):
        """Manage CircleCI Contexts.

        :param org: Org or user name.
        :param owner_id: Org or user id.
        :param owner_type: Either ``organization`` or ``account``.
        :param vcs_type: VCS type (``github``, ``bitbucket``).
        :param context: Context name.
        :param context_id: Context ID.
        :param env: Context env var name.
        :param value: Context env var value.
        :param create: Context create (``True``, ``False``). Defaults to``False``.
        :param delete: Context delete (``True``, ``False``). Defaults to``False``.
        """

        try:
            if create:
                create_new_context = input(
                    f'The context named "{context}" was not found. Do you want to create it? [y/n]: '
                )

                if create_new_context.lower() == "y":
                    new_context = self.circle_client.add_context(
                        context, org, owner_id, owner_type, vcs_type
                    )
                    context_id = new_context["id"]

                    self.logger.info(f"Successfully create context: {context}")

                    return context_id

                exit()

            if delete:
                action = "delete"

                if not env:
                    confirm = input(
                        f'Are you sure want to delete the context "{context}"? [y/n]: '
                    )

                    if confirm.lower() == "y":
                        self.circle_client.delete_context(context_id)
                        self.logger.info(f"Successfully delete context")

                    exit()
                else:
                    self.circle_client.delete_context_envvar(context_id, env)
            else:
                action = "add/update"
                self.circle_client.add_context_envvar(context_id, env, value)

            self.logger.info(f"Successfully {action} context variable: {env}")

            return True
        except Exception as error:
            self.logger.error(f"Error: {error}")

            return False

    def manage_envvars(self, org, vcs_type, project, env, value, delete=False):
        """Manage CircleCI Project Environment Variables.

        :param org: Org or user name.
        :param vcs_type: VCS type (``github``, ``bitbucket``).
        :param project: Project name.
        :param env: Context env var name.
        :param value: Context env var value.
        :param delete: Context delete (``True``, ``False``). Defaults to``False``.
        """

        action = "add/update"

        try:
            if delete:
                action = "delete"
                self.circle_client.delete_envvar(org, project, env, vcs_type)
            else:
                self.circle_client.add_envvar(org, project, env, value, vcs_type)

            self.logger.info(f"Successfully {action} variable: {env}")
            return True
        except Exception as error:
            self.logger.error(f"Error: {error}")
            return False

    def main(self, owner_type, context, project_slug, env, env_file, list_envs, delete):
        """Manage the CircleCI Contexts and Env Vars

        :param owner_type: Either ``organization`` or ``account``.
        :param context: Context name.
        :param project_slug: Project slug. Example: ``github/org_name/project_name``.
        :param env: Env var name and value. Example: ``KEY1=VALUE1``.
        :param env_file: Env vars file. Must be in the format: ``KEY1=VALUE1``, one per line.
        :param delete: Delete envs or the context (``True``, ``False``). Defaults to``False``.
        """

        vcs_type, org, project_name = project_slug.split("/")
        vars = []

        if env:
            vars += list(env)

        if env_file:
            vars += list(set(env_file.read().strip().split("\n")))

        if context:
            project_info = self.circle_client.get_project(project_slug)
            owner_id = project_info["organization_id"]
            context_id = self.get_context_id(
                org, owner_id, owner_type, vcs_type, context
            )

            if not context_id:
                context_id = self.manage_context(
                    org, owner_id, owner_type, vcs_type, context,
                    context_id, None, None, create=True
                )

            if list_envs:
                context_envs = self.circle_client.get_context_envvars(context_id, True)
                self.logger.info("\n"+"\n".join([x["variable"] for x in context_envs]))
                exit()

            if not vars and delete and context_id:
                self.manage_context(
                    org, owner_id, owner_type, vcs_type, context,
                    context_id, None, None, delete=True
                )

        if list_envs:
            envvars = self.circle_client.list_envvars(org, project_name, vcs_type)
            self.logger.info("\n"+"\n".join([x["name"] for x in envvars]))
            exit()

        with ThreadPoolExecutor(max_workers=5) as executor:
            threadpool = []

            for var in vars:
                try:
                    key, value = var.split("=", 1)
                except ValueError:
                    key, value = (var, "")
                except Exception:
                    raise SystemExit(f"Error: failed to proccess variable {var}...")

                if context:
                    threadpool.append(
                        executor.submit(
                            self.manage_context, org, owner_id, owner_type,
                            vcs_type, context, context_id, key.strip(),
                            value.strip(), False, delete
                        )
                    )
                else:
                    threadpool.append(
                        executor.submit(
                            self.manage_envvars, org, vcs_type, project_name,
                            key.strip(), value.strip(), delete
                        )
                    )

            for thread in as_completed(threadpool):
                thread.result()


@click.command()
@click.option(
    "-u", "--api-url",
    metavar="<circleci_api_url>",
    default="https://circleci.com/api",
    show_default=True,
)
@click.option(
    "-t", "--token",
    metavar="<circleci_token>",
    show_default="CIRCLE_TOKEN"
)
@click.option(
    "-c", "--context",
    metavar="<context_name>",
    help="It will ask for create if does not exists",
)
@click.option(
    "-p", "--project",
    metavar="<project_slug>",
    required=True,
    help="Example: github/org-name/project-name",
)
@click.option(
    "-e", "--env",
    multiple=True,
    metavar="<environment_var>"
)
@click.option(
    "-ef", "--env-file",
    metavar="<environment_vars_file>",
    type=click.File("r")
)
@click.option(
    "-l", "--list-envs",
    metavar="<environment_vars_list>",
    is_flag=True
)
@click.option(
    "-d", "--delete",
    metavar="<environment_var_delete>",
    is_flag=True,
    help=("Context only, will delete the context\n\b"
          " Context + vars, will delete the context vars"
          " Vars only, will delete the environment vars")
)
@click.option(
    "-ot", "--owner-type",
    metavar="<owner_type>",
    default="organization",
    show_default=True,
)
@click.option(
    "--debug",
    metavar="<debug>",
    default=False,
    is_flag=True
)
@click.pass_context
def cli(ctx, api_url, token, context, project, env, env_file, list_envs, delete, owner_type, debug):
    """CLI tool for manage CircleCI contexts and environment vars

    All options can be specified as environment variables in the format:
    CIRCLE_<OPTION>. Example: CIRCLE_TOKEN=********
    """

    try:
        ctx.obj = CircleCIEnvsManage(api_url, token, debug)
        ctx.obj.main(owner_type, context, project, env, env_file, list_envs, delete)
    except CircleciError as error:
        raise SystemExit(f"Error: {error}")


if __name__ == "__main__":
    cli(auto_envvar_prefix="CIRCLE")
