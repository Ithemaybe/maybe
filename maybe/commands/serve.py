import click
import http.server
import socketserver
import os
import socket


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unavailable"


def print_box(port):
    local = f"http://localhost:{port}"
    network = f"http://{get_local_ip()}:{port}"

    lines = [
        "",
        "   \033[32mServing!\033[0m",
        "",
        f"   \033[1m- Local:  \033[0m    {local}",
        f"   \033[1m- Network:\033[0m    {network}",
        "",
        "   \033[90mCtrl+C to stop\033[0m",
        "",
    ]

    width = max(len(click.unstyle(l)) for l in lines) + 2

    top    = "   ┌" + "─" * width + "┐"
    bottom = "   └" + "─" * width + "┘"

    click.echo(top)
    for line in lines:
        raw = click.unstyle(line)
        pad = width - len(raw)
        click.echo("   │" + line + " " * pad + "│")
    click.echo(bottom)
    click.echo("")


@click.command()
@click.argument("port", default=3000, type=int)
@click.option("--dir", "-d", default=".", help="Directory to serve")
def serve(port, dir):
    """Start a local static HTTP server."""
    target = os.path.abspath(dir)

    if not os.path.isdir(target):
        click.echo(f"Error: '{target}' is not a directory.", err=True)
        raise SystemExit(1)

    os.chdir(target)

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            code = args[1] if len(args) > 1 else "?"
            if str(code) == "400":
                return
            method = self.command if hasattr(self, "command") else "?"
            path = self.path if hasattr(self, "path") else "/"
            color = "\033[32m" if str(code).startswith("2") else "\033[33m" if str(code).startswith("3") else "\033[31m"
            reset = "\033[0m"
            click.echo(f"   {color}HTTP{reset}  {self.log_date_time_string()}  {code}  {method} {path}")

        def log_error(self, format, *args):
            pass

    print_box(port)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), QuietHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            click.echo("\n   Gracefully shutting down. Please wait...\n")
