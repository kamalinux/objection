import click
import frida

from .repl import Repl
from ..__init__ import __version__
from ..commands.device import get_device_info
from ..commands.mobile_packages import patch_ios_ipa
from ..state.connection import state_connection


# Start the Click command group
@click.group()
@click.option('--network', '-N', is_flag=True, help='Connect using a network connection instead of USB.',
              show_default=True)
@click.option('--host', '-h', default='127.0.0.1', show_default=True)
@click.option('--port', '-p', required=False, default=27042, show_default=True)
@click.option('--gadget', '-g', required=False, default='Gadget',
              help='Name of the Frida Gadget/Process to connect to.',
              show_default=True)
def cli(network: bool, host: str, port: int, gadget: str) -> None:
    """
        \b
             _     _         _   _
         ___| |_  |_|___ ___| |_|_|___ ___
        | . | . | | | -_|  _|  _| | . |   |
        |___|___|_| |___|___|_| |_|___|_|_|
                |___|(object)inject(ion)
        \b
             Runtime Mobile Exploration
                by: @leonjza from @sensepost

        By default, communications will happen over USB, unless the --network
        option is provided.
    """

    # disable the usb comms if network is chosen.
    if network:
        state_connection.use_network()
        state_connection.host = host
        state_connection.port = port

    state_connection.gadget_name = gadget


@cli.command()
def explore() -> None:
    """
        Start the objection exploration REPL.
    """

    r = Repl()

    try:

        device_info = get_device_info()
        r.set_prompt_tokens(device_info)

    except (frida.TimedOutError, frida.ServerNotRunningError) as e:
        click.secho('Error: {0}'.format(e.message), fg='red')

    r.start_repl()


@cli.command()
def version() -> None:
    """
        Prints the current version and exists
    """

    click.secho('objection: {0}'.format(__version__))


@cli.command()
def device_type():
    """
        Get information about an attached device.
    """

    device_name, system_name, model, system_version = get_device_info()

    if state_connection.get_comms_type() == state_connection.TYPE_USB:
        click.secho('Connection: USB')

    elif state_connection.get_comms_type() == state_connection.TYPE_REMOTE:
        click.secho('Connection: Network')

    click.secho('Name: {0}'.format(device_name))
    click.secho('System: {0}'.format(system_name))
    click.secho('Model: {0}'.format(model))
    click.secho('Version: {0}'.format(system_version))


@cli.command()
@click.option('--source', '-s', help='The source IPA to path', required=True)
@click.option('--codesign-signature', '-c',
              help='Codesigning Identity to use. Get it with: `security find-identity -p codesigning -v`',
              required=True)
@click.option('--provision-file', '-p', help='The .mobileprovision file to use in the patched .ipa', required=True)
@click.option('--binary-name', '-b', help='Name of the Mach-O binary in the IPA (used to patch with Frida)')
def patchipa(source: str, codesign_signature: str, provision_file: str, binary_name: str) -> None:
    """
        Patch an IPA with the FridaGadget dylib.
    """

    patch_ios_ipa(**locals())


if __name__ == '__main__':
    cli()
