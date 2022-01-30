"""Settings loader, powered by dynaconf module."""

from dynaconf import Dynaconf


def load_settings():
    settings = Dynaconf(
        envvar_prefix="FADDR",
        settings_files=["/etc/faddr/faddr.yaml"],
    )
    return settings
