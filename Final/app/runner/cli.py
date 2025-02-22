from __future__ import annotations

from typing import no_type_check

import uvicorn
from dotenv import load_dotenv
from typer import Typer

from app.runner.setup import init_app

cli = Typer(no_args_is_help=True, add_completion=False)


@cli.command()
@no_type_check
def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    load_dotenv()

    uvicorn.run(host=host, port=port, app=init_app())
